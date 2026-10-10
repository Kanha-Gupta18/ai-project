"""Model construction and evaluation for rotor-temperature regression."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd
from sklearn.base import RegressorMixin
from sklearn.compose import TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from thermalguard.config import RANDOM_SEED, RAW_FEATURES, STATOR_FEATURES, TARGET_COLUMN
from thermalguard.features import add_engineered_features

ENGINEERED_FEATURES = (
    "current_magnitude",
    "voltage_magnitude",
    "coolant_ambient_delta",
)
CONTROLLER_FEATURES = (*RAW_FEATURES, *ENGINEERED_FEATURES)
MODEL_FEATURES = (*RAW_FEATURES, *STATOR_FEATURES, *ENGINEERED_FEATURES)


def prepare_xy(
    frame: pd.DataFrame, *, include_stator: bool = True
) -> tuple[pd.DataFrame, pd.Series]:
    """Create the deployable feature matrix and rotor-temperature target."""

    enriched = add_engineered_features(frame)
    features = MODEL_FEATURES if include_stator else CONTROLLER_FEATURES
    return enriched.loc[:, features], enriched[TARGET_COLUMN]


def build_candidate_models() -> Mapping[str, RegressorMixin]:
    """Return a small, defensible set of regression candidates."""

    return {
        "mean_baseline": DummyRegressor(strategy="mean"),
        "ridge": TransformedTargetRegressor(
            regressor=Pipeline(
                steps=[
                    ("scale", StandardScaler()),
                    ("model", Ridge(alpha=1.0)),
                ]
            ),
            transformer=StandardScaler(),
        ),
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            learning_rate=0.08,
            max_iter=300,
            max_leaf_nodes=31,
            l2_regularization=1.0,
            early_stopping=True,
            random_state=RANDOM_SEED,
        ),
        "xgboost": XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=8,
            min_child_weight=5,
            subsample=0.8,
            colsample_bytree=0.9,
            reg_lambda=2.0,
            objective="reg:squarederror",
            tree_method="hist",
            n_jobs=4,
            random_state=RANDOM_SEED,
        ),
    }


def regression_metrics(y_true: pd.Series, predictions: np.ndarray) -> dict[str, float]:
    """Calculate accuracy measures with units suitable for engineering review."""

    errors = np.asarray(predictions) - np.asarray(y_true)
    return {
        "mae_celsius": float(mean_absolute_error(y_true, predictions)),
        "rmse_celsius": float(mean_squared_error(y_true, predictions) ** 0.5),
        "r2": float(r2_score(y_true, predictions)),
        "within_5c_percent": float(np.mean(np.abs(errors) <= 5.0) * 100),
        "bias_celsius": float(np.mean(errors)),
    }

