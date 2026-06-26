import sys
import logging
import typer
from pathlib import Path
from typing import List
import matplotlib.pyplot as plt
from sj.io import load_database
from sj.weights import create_rook_swm, create_queen_swm, create_knn_swm, create_distance_swm, create_socio_swm
from sj.analysis import build_morans_table, compute_local_morans
from sj.viz import plot_lisa, plot_swm_weighted, plot_prediction_maps
from sj.report import print_morans_table, save_morans_table
from sj.points import count_points_in_boundaries 
from sj.prediction import merge_two_years, build_prediction_table 


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
        "do_data2018.geojson",
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
    points: List[str] = typer.Option(
        None,
        "--points",
        "-p",
        help="Name of point layer (without .geojson). E.g. --points playground. Repeat for multiple: -p playgrounds -p kindergarten",
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
        for point_layer in points:
            polygons, point_col = count_points_in_boundaries(polygons, point_layer)
        if socio_index == "deaths_per_1000_abs":  # default not explicitly set
            socio_index = point_col
    
    # add two columns of the geojson or add two point datasets
    if "+" in analysis_variable:
        col1, col2 = analysis_variable.split("+")
        col1 = col1.strip()
        col2 = col2.strip()
        combined = col1 + "_plus_" + col2
        polygons[combined] = polygons[col1] + polygons[col2]
        analysis_variable = combined

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
        fig = plot_lisa(polygons, lisa, title=f"LISA — {analysis_variable} — {name}")
        fig.savefig(
            f"reports/lisa_{analysis_variable.replace(' ', '_').lower()}_{name.replace(' ', '_').lower()}.png",
            dpi=150,
            bbox_inches="tight",
        )
        plt.close(fig)

    
    logger.info("---- end of execution ----")

# access both workflows separately
@app.command()
def predict(
    filename_t1: str = typer.Option(
        "do_data2018.geojson",
        "--filename-t1",
        "-f1",
        help="GeoJSON for earlier time point (e.g., 2018).",
    ),
    filename_t2: str = typer.Option(
        "do_data2024.geojson",
        "--filename-t2",
        "-f2",
        help="GeoJSON for later time point (e.g., 2024).",
    ),
    year_t1: int = typer.Option(
        2018,
        "--year-t1",
        "-y1",
        help="Year label for t1 (for map titles; not parsed from the filename).",
    ),
    year_t2: int = typer.Option(
        2024,
        "--year-t2",
        "-y2",
        help="Year label for t2 (for map titles; not parsed from the filename).",
    ),
    indicator: str = typer.Option(
        "share_65_80_pct",
        "--variable",
        "-v",
        help="Name of the socioeconomic indicator to predict.",
    ),
    id_col: str = typer.Option(
        "unbeznr",
        "--id-col",
        "-i",
        help="Column name of the unique district ID, used to join t1/t2 data.",
    ),
    name_col: str = typer.Option(
        "bezeichnun",
        "--name-col",
        "-n",
        help="Column name of the district name (used for display).",
    ),
    weight: str = typer.Option(
        "queen",
        "--weight",
        "-w",
        help="Which spatial weight matrix to use for the spatial lag predictor. Options: rook, queen, knn, distance.",
    ),
    distance_threshold: int = typer.Option(
        5000, 
        "--distance", 
        "-d",
        help="Distance threshold in metres for distance-band SWM (if selected)."
    ),
    steps: int = typer.Option(
        1, 
        "--steps", 
        "-s",
        help="How often the model is applied recursively (future projection)."
    ),
):
    """
    Loads two GeoJSON files for different years, merges them, builds a spatial weight matrix,
    and fits a spatial lag regression model to predict the chosen indicator in t2 based on t1 values and spatial lag of t1.
    """
    logger.info(f"Loading {filename_t1} and {filename_t2} for prediction.")
    Path("reports").mkdir(exist_ok=True)
 
    polygons_t1 = load_database(filename=filename_t1)
    polygons_t2 = load_database(filename=filename_t2)
    gdf = merge_two_years(polygons_t1, polygons_t2, id_col=id_col)
 
    # use previously defined weight functions
    weight_builders = {
        "rook": lambda: create_rook_swm(gdf),
        "queen": lambda: create_queen_swm(gdf),
        "knn": lambda: create_knn_swm(gdf),
        "distance": lambda: create_distance_swm(gdf, threshold=distance_threshold),
    }
    if weight not in weight_builders:
        raise typer.BadParameter(f"Unknown weight: {weight}")
    w = weight_builders[weight]()
 
    table = build_prediction_table(gdf, indicator=indicator, w=w, steps=steps, name_col=name_col)
    print(table.sort_values(f"{indicator}_residual", key=abs, ascending=False).head(10))
 
    out_path = f"reports/prediction_{indicator}_{weight}.csv"
    table.to_csv(out_path)
    logger.info(f"Prediction table saved: {out_path}")

    # side-by-side maps: t1, t2 and projected future step
    fig = plot_prediction_maps(
        gdf, table, indicator=indicator, year_t1=year_t1, year_t2=year_t2, steps=steps
    )
    map_path = f"reports/prediction_map_{indicator}_{weight}.png"
    fig.savefig(map_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Prediction map saved: {map_path}")




if __name__ == "__main__":
    app()