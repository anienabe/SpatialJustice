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