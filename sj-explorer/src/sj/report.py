import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def print_morans_table(df: pd.DataFrame, variable: str) -> None:
    """
    Prints
    """

    print()
    print("=" * 60)
    print(f" Global Moran's I Comparison -{variable}")
    print("=" * 60)
    print(df.to_string(index=False))
    print("=" * 60)
    print()

def save_morans_table(
        df: pd.DataFrame, variable: str, output_dir: str = "reports"
) -> None:
        """
        some 
        """
        Path(output_dir).mkdir(exist_ok=True)
        filename = f"{output_dir}/morans_table_{variable}.csv"
        df.to_csv(filename, index=False)
        logger.info("Moran's I table saved to %s", filename)
