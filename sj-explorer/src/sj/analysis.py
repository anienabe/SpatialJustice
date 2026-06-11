import logging 
import esda # uv add esda
import pandas as pd

logger = logging.getLogger(__name__)

def compute_global_morans(gdf, w, variable: str) -> esda.Moran:
    logger.info("Computing Global Morans I - variable: %s", variable)
    y = gdf[variable].values

    return esda.Moran(y, w)


def build_morans_table(gdf, weights_dict: dict, variable: str) -> pd.DataFrame:
    logger.info("Building Morans I comparison table - variable %s", variable)
    results = []

    for name, w in weights_dict.items():
        mi = compute_global_morans(gdf, w, variable)
        results.append(
            {
                "W Type": name,
                "Morans I": round(mi.I, 4),
                "p-value": round(mi.p_sim, 4),
                "z-score": round(mi.z_sim, 4),
                "Significant": "yes" if mi.p_sim < 0.05 else "no",
            }
        )

    return pd.DataFrame(results)

def compute_local_morans(gdf, w, variable: str) -> esda.Moran_Local:
    logger.info("Computing Local Morans I - variable %s", variable)
    y = gdf[variable].values
    return esda.Moran_Local(y, w)