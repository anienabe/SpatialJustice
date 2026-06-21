import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def count_points_in_boundaries(boundaries, point_layer_name: str, output_dir: str = "preprocessing/output"):
    """
    Counts points per district and returns enriched boundaries GeoDataFrame.
    Saves a GeoJSON to output_dir/{point_layer_name}_counts.geojson
    """
    # Loading point data
    pts_raw = gpd.read_file(f"data/{point_layer_name}.geojson", encoding="latin-1")
    logger.info(f"Loaded {len(pts_raw)} points from {point_layer_name}.geojson")

    # CRS 
    pts_raw = pts_raw.to_crs(boundaries.crs)

    # plot both datasets to check data situation
    fig, ax = plt.subplots()
    boundaries.plot(ax=ax, edgecolor='black', color='powderblue')
    pts_raw.plot(ax=ax, color='red')
    plt.show()

    # copy of points
    pts = pts_raw.copy()

    # spatial Join, within: geometric approach to find out with coordinates if a point is inside the polygon
    joined = gpd.sjoin(pts, boundaries, how='left', predicate='within')

    # count the points
    point_count = joined.groupby('index_right').size().reset_index(name='amount_points')

    # merge with boundaries
    boundaries_result = boundaries.copy()
    col_name = f"{point_layer_name}_count"
    boundaries_result[col_name] = boundaries_result.index.map(
        point_count.set_index('index_right')['amount_points']
    ).fillna(0).astype(int)

    # print sorted
    print(boundaries_result[['bezeichnun', 'unbeznr', col_name]].sort_values('unbeznr', ascending=True))

    # export as GeoJSON
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = f"{output_dir}/{point_layer_name}_counts.geojson"
    boundaries_result.to_file(out_path, driver="GeoJSON")
    logger.info(f"Saved counts to {out_path}")

    # Plot to verify
    boundaries_result['coloring'] = boundaries_result[col_name] > 0
    ax = boundaries_result.plot(edgecolor='black', facecolor='powderblue')
    pts_raw.plot(ax=ax, color='red', markersize=5)
    boundaries_result[boundaries_result['coloring']].plot(ax=ax, facecolor='coral', edgecolor='black')
    plt.show()

    return boundaries_result, col_name