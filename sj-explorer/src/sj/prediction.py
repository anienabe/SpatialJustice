import logging
import pandas as pd
import geopandas as gpd
import numpy as np
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

# merges years into one GeoDataFrame, every district has columns with data for both years

def merge_two_years(gdf_t1, gdf_t2, id_col):
    
    # set the district ID as the index so both years can be joined on it
    g1 = gdf_t1.set_index(id_col)
    g2 = gdf_t2.set_index(id_col)
    common = [c for c in g1.columns if c in g2.columns and c != "geometry"]
    # join the two years on the common columns and keep the geometry from t1
    merged = g1[common + ["geometry"]].join(g2[common], lsuffix="_t1", rsuffix="_t2", how="inner")
    return gpd.GeoDataFrame(merged, geometry="geometry", crs=g1.crs)

# Computes each district's neighbour average for a given variable (the spatial lag),
# with a spatial weight matrix

def spatial_lag_from_w(values, w):
    # row-standardize the weights so that each row sums to 1
    w.transform = "r"
    W_full, ids = w.full()
    # compute the spatial lag by multiplying the weight matrix with the values
    lagged = W_full @ values.reindex(ids).to_numpy()
    return pd.Series(lagged, index=ids, name=f"{values.name}_lag").reindex(values.index)


# trains model: what explains change from earlier year to later year best
# calculates residuals: how far off is prediction from value for each district
# calculates projection: uses model for next prediction

def build_prediction_table(gdf, indicator, w, steps=1, name_col=None):
    # define the target variable and the predictor variables 
    y_t1 = gdf[f"{indicator}_t1"]
    y_t2 = gdf[f"{indicator}_t2"]
    lag_t1 = spatial_lag_from_w(y_t1, w)
    # fit a linear regression model to predict the later year from the earlier year and the spatial lag
    X = pd.DataFrame({"y_t1": y_t1, "lag_t1": lag_t1})
    model = LinearRegression().fit(X, y_t2)

    # make predictions for the later year and calculate residuals and projections
    pred = pd.Series(model.predict(X), index=gdf.index)
    residuals = y_t2 - pred
    projection = model.intercept_ + model.coef_[0] * y_t2 + model.coef_[1] * spatial_lag_from_w(y_t2, w)

    logger.info(f"R²={model.score(X, y_t2):.3f}  beta_own={model.coef_[0]:.3f}  beta_neighbors={model.coef_[1]:.3f}")

    # create a DataFrame with the results
    columns = {}
    if name_col:
        name_source = f"{name_col}_t1" if f"{name_col}_t1" in gdf.columns else name_col
        columns["name"] = gdf[name_source]

    columns.update({
        f"{indicator}_t1": y_t1,
        f"{indicator}_t2": y_t2,
        f"{indicator}_pred_t2": pred,
        f"{indicator}_residual": residuals,
        f"{indicator}_projection": projection,
    })

    # recursively apply the model steps into the future
    current = y_t2
    last_projection = None
    # each step uses the previous step's predictions as the new input
    for step in range(1, steps + 1):
        lag_current = spatial_lag_from_w(current, w)
        current = pd.Series(
            model.intercept_ + model.coef_[0] * current + model.coef_[1] * lag_current,
            index=gdf.index,
        )
        columns[f"{indicator}_projection_step{step}"] = current
        last_projection = current
 
    # keep the old single-column name pointing at the final step
    columns[f"{indicator}_projection"] = last_projection

    return pd.DataFrame(columns)


# RMSE = Root Mean Square Error
# MAE = Mean Absolute Error
# measures how far your predictions are from the real values,
# on average, in the same units as the target. Lower is better.

def rmse(actual, predicted):
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))

def mae(actual, predicted):
    return float(np.mean(np.abs(actual - predicted)))