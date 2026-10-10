"""Tests for residual and profile-level evaluation outputs."""

import numpy as np
from sklearn.linear_model import LinearRegression

from thermalguard.evaluation import (
    permutation_importance_table,
    prediction_table,
    profile_metrics,
)
from thermalguard.modeling import prepare_xy


def test_prediction_table_calculates_signed_errors(motor_frame):
    predicted = motor_frame["pm"].to_numpy() + 2.0

    table = prediction_table(motor_frame, predicted)

    assert np.allclose(table["error_celsius"], 2.0)
    assert np.allclose(table["absolute_error_celsius"], 2.0)


def test_profile_metrics_returns_one_row_per_profile(motor_frame):
    predicted = motor_frame["pm"].to_numpy() + 2.0

    metrics = profile_metrics(prediction_table(motor_frame, predicted))

    assert len(metrics) == 4
    assert np.allclose(metrics["mae_celsius"], 2.0)
    assert np.allclose(metrics["within_5c_percent"], 100.0)


def test_permutation_importance_supports_any_regressor(motor_frame):
    features, target = prepare_xy(motor_frame)
    model = LinearRegression().fit(features, target)

    importance = permutation_importance_table(
        model, features, target, max_rows=len(features)
    )

    assert set(importance["feature"]) == set(features.columns)
    assert importance["mae_increase_celsius"].notna().all()

