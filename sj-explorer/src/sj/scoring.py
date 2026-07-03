import logging
import pandas as pd
import geopandas as gpd
 
from sj.composite import build_composite_score
from sj.prediction import build_prediction_table
 
logger = logging.getLogger(__name__)

def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """
    Scales a dict of weight, sums to 1.
    Example: {"a": 2, "b": 1} -> {"a": 0.667, "b": 0.333}
    """
    total = sum(weights.values())
    if total <= 0:
        raise ValueError(f"Weights must sum to a positive number, got {weights}")

    normalized = {}
    for key, value in weights.items():
        normalized[key] = value / total
    return normalized

# for one year
def score_single_year(gdf: gpd.GeoDataFrame, indicators: dict[str, str], id_col: str) -> pd.Series:
    """
    Builds a composite score for one year (one GeoDataFrame).

    Returns a Series of composite scores, indexed by district ID (id_col).
    """
    # Set the district ID as the index (instead of the default row number).
    gdf_by_district = gdf.set_index(id_col)

    # build_composite_score comes from composite.py.
    # Normalizes every indicator to [0, 1] and averages them into one "composite_score" column, where 1 = worst situation.
    result = build_composite_score(gdf_by_district, indicators)

    # We only need the composite_score column here, not the individual
    # per-indicator _score columns that build_composite_score also returns.
    return result["composite_score"]

# for two years, so in our context 2024 as current and 2018 as historical values
def build_multi_year_score(
    gdf_t2, indicators, id_col, name_col, scope,
    weight_past=1.0, weight_current=1.0, weight_future=1.0,
    gdf_t1=None, merged=None, w=None, steps=1,
) -> pd.DataFrame:
    if scope not in ("current", "historical", "full"):
        raise ValueError(f"not in scope of current, historical, full")

    # current year is always included
    year_scores = {"score_current": score_single_year(gdf_t2, indicators, id_col)}
    year_weights = {"score_current": weight_current}

    if scope in ("historical", "full"):
        if gdf_t1 is None:
            raise ValueError(f"requires past data")
        year_scores["score_past"] = score_single_year(gdf_t1, indicators, id_col)
        year_weights["score_past"] = weight_past

    if scope == "full":
        if merged is None or w is None:
            raise ValueError("full scope requires merged and w")
        
        projected_gdf = project_indicators_to_future(merged, indicators, name_col=name_col, w=w, steps=steps) # Lea build func!
        future_result = build_composite_score(projected_gdf, indicators)
        year_scores["score_future"] = future_result["composite_score"]
        year_weights["score_future"] = weight_future

    year_weights = normalize_weights(year_weights)
    logger.info(f"Score weights (normalized): { {k: round(v, 3) for k, v in year_weights.items()} }")

    # put all year-scores side by side, matched by district ID
    table = pd.DataFrame(year_scores)

    # drop districts missing a score in one of the included years
    before = len(table)
    table = table.dropna(subset=list(year_weights.keys()))
    if len(table) < before:
        logger.warning(f"Dropped {before - len(table)} district(s) with missing data.")

    # weighted sum of all included year-scores
    final_score = pd.Series(0.0, index=table.index)
    for score_name, weight in year_weights.items():
        final_score = final_score + table[score_name] * weight
    table["final_score"] = final_score

    table = table.sort_values("final_score", ascending=False)
    table["rank"] = range(1, len(table) + 1)

    district_names = gdf_t2.set_index(id_col)[name_col]
    table.insert(0, "name", district_names.reindex(table.index))

    return table