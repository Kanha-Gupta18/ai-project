"""Tests for model inputs, candidates, and engineering metrics."""

import numpy as np

from thermalguard.modeling import (
    CONTROLLER_FEATURES,
    MODEL_FEATURES,
    build_candidate_models,
    prepare_xy,
    regression_metrics,
)


def test_prepare_xy_uses_only_deployable_features(motor_frame):
    x, y = prepare_xy(motor_frame)

    assert tuple(x.columns) == MODEL_FEATURES
    assert y.name == "pm"
    assert "profile_id" not in x.columns
    assert "pm" not in x.columns

    controller_x, _ = prepare_xy(motor_frame, include_stator=False)
    assert tuple(controller_x.columns) == CONTROLLER_FEATURES
    assert not {"stator_yoke", "stator_tooth", "stator_winding"} & set(controller_x.columns)


def test_candidate_models_include_simple_and_nonlinear_baselines():
    models = build_candidate_models()

    assert set(models) == {
        "mean_baseline",
        "ridge",
        "hist_gradient_boosting",
        "xgboost",
    }


def test_regression_metrics_are_in_engineering_units():
    metrics = regression_metrics(
        np.array([40.0, 50.0, 60.0]), np.array([42.0, 47.0, 61.0])
    )

    assert metrics["mae_celsius"] == 2.0
    assert metrics["within_5c_percent"] == 100.0
    assert metrics["bias_celsius"] == 0.0
