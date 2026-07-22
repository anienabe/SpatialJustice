import logging
import pandas as pd
import geopandas as gpd

logger = logging.getLogger(__name__)

# the flag of indicators have to have a lower_worse or higher_worse, this is to make a readable dictionary of it
def parse_indicators(indicator_flags: list[str]) -> dict[str, str]:
    """
    Parses the CLI indicator flags into a dict of {column: direction}.
 
    Each flag is expected in the format "column_name:direction" where direction
    is either "higher_worse" or "lower_worse".
 
    Example:
        ["children_under_15_SGB_II_pct:higher_worse", "living_space_per_inhabitant_sq_abs:lower_worse"]
        → {"children_under_15_SGB_II_pct": "higher_worse", "living_space_per_inhabitant_sq_abs": "lower_worse"}
    """

    parsed= {}
    for flag in indicator_flags:
        if ":" not in flag:
            raise ValueError(
                f"Indicator '{flag}' is missing a direction. "
                f"Use the format 'column_name:higher_worse' or 'column_name:lower_worse'."
            )
        col, direction = flag.split(":", 1) # cut the String in two at :
        col = col.strip()
        direction = direction.strip()
        if direction not in ("higher_worse", "lower_worse"):
            raise ValueError(
                f"Unknown direction '{direction}' for indicator '{col}'."
                f"Must be 'higher_worse' or 'lower_worse'."
            )
        parsed[col] = direction 
    return parsed

# normalize a Series of values to values between 0 and 1, the calculating function needed for build_composite_score
def minmax(series: pd.Series) -> pd.Series:
    """Min-max normalization to [0, 1]. Returns 0.5 everywhere if range is zero."""
    rng = series.max() - series.min()
    if rng == 0:
        logger.warning(f"Column '{series.name}' has zero range - all values are identical. Scoring as 0.5.")
        return pd.Series(0.5, index=series.index)
    return (series- series.min()) / rng

def build_composite_score(gdf: gpd.GeoDataFrame, indicators: dict[str, str]) -> pd.DataFrame:
    """
    Normalizes each indicator to [0, 1] and averages them into a composite score where 1 = worst sitution, 0 = best situation. 

    Args:
        gdf:        GeoDataFrame containing all indicator columns.
        indicators: Dict of {column_name: direction} as returned by parse_indicators.
                    direction is "higher_worse" or "lower_worse".

    Returns:
        DataFrame with one row per district containing:
        - one normalized column per indicator (suffixed with _score)
        - composite_score: mean of all normalized columns
    """
    missing = [col for col in indicators if col not in gdf.columns]
    if missing: 
        raise KeyError(f"Columns not found in GeoDataFrame: {missing}")
    
    normalized = {}
    for col, direction in indicators.items():
        norm = minmax(gdf[col])
        if direction == "lower_worse":
            #invert so that low raw values -> high score (=worse)
            norm = 1 - norm
        normalized[f"{col}_score"] = norm
        logger.info(f" {col} ({direction}): min={gdf[col].min():.3f}, max={gdf[col].max():.3f}")

    result = pd.DataFrame(normalized, index=gdf.index)
    result["composite_score"] = result.mean(axis=1)

    logger.info(
        f"Composite score built from {len(indicators)} indicator(s)."
        f"Score range: {result['composite_score'].min():.3f} - {result['composite_score'].max():.3f}"
    )
    return result

def flag_consistent_disadvantage(
    gdf: gpd.GeoDataFrame, indicators: dict[str, str], flag_top_n: int = 10
) -> pd.DataFrame:
    """
    Identifies districts that are consistently disadvantaged across MULTIPLE
    indicators, rather than just scoring high on the single averaged
    composite_score.

    For each indicator, a district is "flagged" if it is among the flag_top_n
    worst districts for that indicator (ties included, via rank(method="min")).
    """
    scored = build_composite_score(gdf, indicators)

    # each entry is a boolean indicating whether the district is flagged for that indicator
    flag_cols = {}
    for col in indicators:
        score_col = f"{col}_score"
        ranks = scored[score_col].rank(method="min", ascending=False)
        flag_cols[f"{col}_flagged"] = ranks <= flag_top_n

    result = pd.DataFrame(flag_cols, index=scored.index)
    # count how many indicators each district is flagged for
    result["n_indicators_flagged"] = result.sum(axis=1)
    result["flagged_indicators"] = result[list(flag_cols)].apply(
        lambda row: ", ".join(col.removesuffix("_flagged") for col, is_flagged in row.items() if is_flagged),
        axis=1,
    )
    # sort by number of indicators flagged, descending
    result = result.sort_values("n_indicators_flagged", ascending=False)

    logger.info(
        f"Flagged {int((result['n_indicators_flagged'] > 0).sum())} district(s) as top-{flag_top_n} "
        f"worst in at least one of {len(indicators)} indicator(s); "
        f"{int((result['n_indicators_flagged'] == len(indicators)).sum())} district(s) flagged in ALL of them."
    )
    return result