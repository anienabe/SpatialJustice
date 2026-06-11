import sys
import logging
import typer
from pathlib import Path
from typing import List
from sj.io import load_database
from sj.weights import create_rook_swm, create_queen_swm, create_knn_swm, create_distance_swm, create_socio_swm
from sj.analysis import build_morans_table, compute_local_morans


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

app = typer.Typer()

@app.command()
def main(
    filename: str = typer.Option(
        "administrative_districts_dortmund_data_2018.geojson",
        "--input",
        "-i",
        help="GeoJSON filename with location/year of data, inside the data/ folder.",
    ),
    analysis_variable: str = typer.Option(
        "new_flats_1999_2016_pct",
        "--variable", 
        "-v",
        help="Column name to run Moran's I on.",
    ),
    socio_index: str = typer.Option(
        "transfer_payment_pct",
        "--socio-index", 
        "-s",
        help="Column name used for socioeconomic SWM weighting.",
    ),
    distance_threshold: int = typer.Option(
        5000,
        "--distance", 
        "-d",
        help="Distance threshold in metres for distance-band SWM.",
    ),
    weights: List[str] = typer.Option(
        ["rook", "queen", "knn", "distance"],
        "--weight", 
        "-w",
        help="Which SWMs to build. Repeat flag for multiple: -w rook -w queen",
    ),
):
    """
    Loads a GeoJSON file, builds one or more spatial weight matrices (SWMs),
    and computes Moran's I (global spatial autocorrelation) for a chosen variable.

    Supported weight types (--weight flag):
      rook       shared edges only (strict contiguity)
      queen      shared edges AND corners (loose contiguity)
      knn        k nearest neighbours (default k=4)
      distance   all neighbours within --distance metres
      socio      distance-band W re-weighted by a socioeconomic similarity index
    """

    logger.info("SJ Explorer. Starting Execution")
    Path("reports").mkdir(exist_ok=True)

    polygons = load_database(filename=filename)

    # --- Build selected spatial weight matrices ---
    available = {}
    if "rook" in weights: available["Rook"] = create_rook_swm(polygons)
    if "queen" in weights: available["Queen"] = create_queen_swm(polygons)
    if "knn" in weights: available["KNN (k=4)"] = create_knn_swm(polygons)
    if "distance" in weights: available[f"Distance Band ({distance_threshold})"] = create_distance_swm(polygons, threshold=distance_threshold)

    # socio always needs a distance base → only if distance was built
    if "socio" in weights:
        base_w = available.get(f"Distance Band ({distance_threshold})")
        if base_w is None:
            base_w = create_distance_swm(polygons, threshold=distance_threshold)
        available["Socio-Similarity"] = create_socio_swm(polygons, base_w, index_col=socio_index)

    

    # --- Global Moran's I table ---
    table = build_morans_table(polygons, available, variable=analysis_variable)

    



    logger.info("---- end of execution ----")




if __name__ == "__main__":
    app()