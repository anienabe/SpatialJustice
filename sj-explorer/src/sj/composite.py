import logging
import pandas as pd
import geopandas as gpd

logger = logging.getLogger(__name__)


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
        col, direction = flag.split(":", 1)
        col = col.strip()
        direction = direction.strip()
        if direction not in ("higher_worse", "lower_worse"):
            raise ValueError(
                f"Unknown direction '{direction}' for indicator '{col}'."
                f"Must be 'higher_worse' or 'lower_worse'."
            )
        parsed[col] = direction
    return parsed

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