import logging
import geopandas as gpd

logger = logging.getLogger(__name__)

# filename is defined via typer in main, here just define datatype
def load_database(filename:str) -> gpd.GeoDataFrame:
    logger.info("---- loading {} ---- ".format(filename))

    polygons = gpd.read_file("data/"+filename)

    logger.info("---- adjusting projection ----")
    polygons = polygons.to_crs(epsg=25832)

    return polygons