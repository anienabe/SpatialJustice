"""

Spatial-lag-based prediction for socioeconomic indicators across Dortmund's
administrative sub-districts (Unterbezirke).

Modell (SLX - Spatial Lag of X):
    y_t2 = b0 + b1 * y_t1 + b2 * (W @ y_t1) + eps

Where:
    y_t1        = the indicator's value at the earlier time point (e.g. 2018)
    y_t2        = the indicator's value at the later time point (e.g. 2024)
    W @ y_t1    = the row-standardized average of each district's neighbors
                  at t1 (the "spatial lag")
    b0, b1, b2  = coefficients estimated via ordinary least squares (OLS)
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
import geopandas as gpd
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)


@dataclass

class SpatialLagPredictionResult:
    indicator: str # Name of the socioeconomic indicator
    coefficients: dict # Dictionary with keys 'intercept', 'beta_own', 'beta_neighbors'
    r2: float # R² of the fitted model
    predictions: pd.Series # Predicted values for t2 based on the model
    residuals: pd.Series # Actual t2 values minus predictions (model errors)
    projection: pd.Series | None = None 


def merge_two_years(
    gdf_t1: gpd.GeoDataFrame,
    gdf_t2: gpd.GeoDataFrame,
    id_col: str,
) -> gpd.GeoDataFrame:
    """
    Merge two yearly GeoDataFrames into a single GeoDataFrame, joined on a shared district ID column.
    
    Args:
        gdf_t1: GeoDataFrame for the earlier year (e.g. 2018).
        gdf_t2: GeoDataFrame for the later year (e.g. 2024).
        id_col: Name of the column containing the unique district ID
                shared by both years
    Returns:
        A GeoDataFrame with columns from both years, suffixed with _t1 and _t2, and a single geometry column.
    
    """
    g1 = gdf_t1.set_index(id_col)
    g2 = gdf_t2.set_index(id_col)

    # Only keep columns that are in both years
    common = [c for c in g1.columns if c in g2.columns and c != "geometry"]

    merged = g1[common + ["geometry"]].join(
        g2[common], lsuffix="_t1", rsuffix="_t2", how="inner"
    )
    return gpd.GeoDataFrame(merged, geometry="geometry", crs=g1.crs)


def spatial_lag_from_w(values: pd.Series, w) -> pd.Series:
    """
    Compute the spatial lag (neighborhood average) of a value series,
    given a libpysal spatial weight matrix (W).

    Args:
        values: A pandas Series of indicator values, indexed by district
            ID (must match the IDs known to `w`).
        w: A fitted libpysal W object (returned by create_rook_swm, create_queen_swm, ...)
    
    Returns:
        A pandas Series of the same length as `values`, containing each
        district's neighborhood average
    """
    # each row of W must sum to 1 so that the lag is a weighted average of neighbors rather than a sum
    w.transform = "r"

    W_full, ids = w.full()
    aligned = values.reindex(ids)  # gleiche Reihenfolge wie W
    lagged = W_full @ aligned.to_numpy()
    return pd.Series(lagged, index=ids, name=f"{values.name}_lag").reindex(values.index)


def fit_spatial_lag_model(
    gdf: gpd.GeoDataFrame,
    indicator: str,
    w,
) -> SpatialLagPredictionResult:
    """
    Fit an SLX (Spatial Lag of X) regression model for one indicator.
 
    The model predicts each district's t2 value from two predictors:
    (1) its own t1 value, and (2) the spatial lag (neighborhood average)
    of its t1 value. This is estimated via ordinary least squares (OLS).
    
    Args:
        gdf: GeoDataFrame produced by merge_two_years()
        indicator: Name of the socioeconomic indicator to model
        w: A fitted object used to compute the spatial lag of the t1 values.
 
    Returns:
        A SpatialLagPredictionResult containing the fitted coefficients,
        R², in-sample predictions, and residuals for this indicator.

    """
    y_t1 = gdf[f"{indicator}_t1"]
    y_t2 = gdf[f"{indicator}_t2"]
    lag_t1 = spatial_lag_from_w(y_t1, w)

    # two predictors: own t1 value and spatial lag of t1
    # t2 values are excluded, because want to predict them from information available in t1
    X = pd.DataFrame({"y_t1": y_t1, "lag_t1": lag_t1})
    model = LinearRegression().fit(X, y_t2)

    pred = pd.Series(model.predict(X), index=gdf.index, name=f"{indicator}_pred")
    
    # Residual = actual - predicted. Positive residual means the district
    # grew/changed MORE than the model expected; negative means LESS.
    residuals = (y_t2 - pred).rename(f"{indicator}_residual")

    logger.info(f"Spatial-Lag-Modell für '{indicator}': R²={model.score(X, y_t2):.3f}")

    return SpatialLagPredictionResult(
        indicator=indicator,
        coefficients={
            "intercept": model.intercept_,
            "beta_own": model.coef_[0],
            "beta_neighbors": model.coef_[1],
        },
        r2=model.score(X, y_t2),
        predictions=pred,
        residuals=residuals,
    )


def project_forward(
    result: SpatialLagPredictionResult,
    y_t2: pd.Series,
    w,
    steps: int = 1,
) -> pd.Series:
    """Apply a fitted spatial-lag model recursively to project values beyond
    the most recent observed time point (e.g. estimate "2030" from 2024).
    
    rgs:
        result: The fitted SpatialLagPredictionResult from
            fit_spatial_lag_model(), providing the coefficients to reuse.
        y_t2: The most recent observed values (e.g. 2024 data) 
        w: The same object used during fitting, so the spatial
            lag is computed consistently.
        steps: Number of times to re-apply the model. steps=1 produces a
            single projection one "model step" into the future; higher
            values compound the projection further (with compounding
            uncertainty - use cautiously).
 
    Returns:
        A pandas Series of projected values, indexed like y_t2.
    """
    current = y_t2.copy()
    b0, b1, b2 = (
        result.coefficients["intercept"],
        result.coefficients["beta_own"],
        result.coefficients["beta_neighbors"],
    )
    for _ in range(steps):
        lag = spatial_lag_from_w(current, w)
        current = b0 + b1 * current + b2 * lag

    current.name = f"{result.indicator}_projection"
    return current


def build_prediction_table(
    gdf: gpd.GeoDataFrame,
    indicator: str,
    w,
    steps: int = 1,
    name_col: str | None = None,
) -> pd.DataFrame:
    """
    Convenience function that runs the full prediction pipeline for one
    indicator and assembles all results into a single, readable table.
    
    """
    result = fit_spatial_lag_model(gdf, indicator, w)
    projection = project_forward(result, gdf[f"{indicator}_t2"], w, steps=steps)
 
    columns = {}
    if name_col is not None:
        # Name ist in beiden Jahren gleich, daher reicht eine Variante (_t1)
        name_source = f"{name_col}_t1" if f"{name_col}_t1" in gdf.columns else name_col
        columns["name"] = gdf[name_source]
 
    columns.update({
        f"{indicator}_t1": gdf[f"{indicator}_t1"],
        f"{indicator}_t2": gdf[f"{indicator}_t2"],
        f"{indicator}_pred_t2": result.predictions,
        f"{indicator}_residual": result.residuals,
        f"{indicator}_projection": projection,
    })
 
    return pd.DataFrame(columns)