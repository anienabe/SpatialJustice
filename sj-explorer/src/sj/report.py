import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# prints the moran's I table
def print_morans_table(df: pd.DataFrame, variable: str) -> None:
    print()
    print("=" * 60)
    print(f" Global Moran's I Comparison -{variable}")
    print("=" * 60)
    print(df.to_string(index=False))
    print("=" * 60)
    print()

# saves the moran's I table as CSV
def save_morans_table(
        df: pd.DataFrame, variable: str, output_dir: str = "reports"
) -> None:
        Path(output_dir).mkdir(exist_ok=True)
        filename = f"{output_dir}/morans_table_{variable}.csv"
        df.to_csv(filename, index=False)
        logger.info("Moran's I table saved to %s", filename)

# prints the composite score ranking
def print_ranking(table: pd.DataFrame, scope: str) -> None:
    """Prints the composite score ranking table."""
    print()
    print("=" * 60)
    print(f" Composite Score Ranking (scope={scope})")
    print(" 1 = highest need for action, 0 = best situation")
    print("=" * 60)
    cols = [c for c in table.columns if c != "geometry"]
    print(table[cols].to_string())
    print("=" * 60)
    print()

# saves the composite score ranking table as CSV
def save_ranking(table: pd.DataFrame, scope: str, label: str = "composite", output_dir: str = "reports") -> None:
    filename = f"{output_dir}/score_{label}_{scope}.csv"
    cols = [c for c in table.columns if c != "geometry"]
    table[cols].to_csv(filename)
    logger.info("Composite score ranking saved to %s", filename)