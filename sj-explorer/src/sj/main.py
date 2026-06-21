import sys
import logging
import typer
from pathlib import Path
from typing import List
from sj.io import load_database
from sj.weights import create_rook_swm, create_queen_swm, create_knn_swm, create_distance_swm, create_socio_swm
from sj.analysis import build_morans_table, compute_local_morans
from sj.viz import plot_lisa, plot_swm_weighted
from sj.report import print_morans_table, save_morans_table
from sj.points import count_points_in_boundaries #new from Anke



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
        "average_age_years",
        "--variable", 
        "-v",
        help="Column name to run Moran's I on.",
    ),
    socio_index: str = typer.Option(
        "deaths_per_1000_abs",
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
    points: str = typer.Option(
        None,
        "--points",
        "-p",
        help="Name of point layer (without .geojson). E.g. --points playground",
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

    # Point data counting (if desired)
    if points:
        polygons, point_col = count_points_in_boundaries(polygons, points)
        if socio_index == "deaths_per_1000_abs":  # default not explicitly set
            socio_index = point_col

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

    # --- Visualize ---
    for name, w in available.items():
        fig = plot_swm_weighted(polygons, w, title=f"{name} W")
        fig.savefig(f"reports/swm_{name.replace(' ', '_').lower()}.png", dpi=150, bbox_inches="tight")

    # --- Global Moran's I table ---
    table = build_morans_table(polygons, available, variable=analysis_variable)
    print_morans_table(table, variable=analysis_variable)
    save_morans_table(table, variable=analysis_variable)

    # --- LISA maps ---
    for name, w in available.items():
        lisa = compute_local_morans(polygons, w, variable=analysis_variable)
        fig = plot_lisa(polygons, lisa, title=f"LISA — {name}")
        fig.savefig(f"reports/lisa_{name.replace(' ', '_').lower()}.png", dpi=150, bbox_inches="tight")

    
    logger.info("---- end of execution ----")

if __name__ == "__main__":
    app()