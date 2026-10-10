"""Tests for saving, loading, and using the prediction artifact."""

from pathlib import Path

import numpy as np
from sklearn.dummy import DummyRegressor

from thermalguard.artifact import load_artifact, predict_frame, save_artifact
from thermalguard.modeling import prepare_xy


def test_artifact_round_trip_preserves_predictions(motor_frame):
    features, target = prepare_xy(motor_frame)
    model = DummyRegressor(strategy="mean").fit(features, target)
    path = Path("work/test_model.joblib")
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        summary = {
            name: {
                "minimum": float(motor_frame[name].min()),
                "median": float(motor_frame[name].median()),
                "maximum": float(motor_frame[name].max()),
            }
            for name in motor_frame.columns
            if name not in {"pm", "profile_id"}
        }
        save_artifact(
            model,
            path,
            {"mae_celsius": 1.0},
            include_stator=True,
            input_summary=summary,
        )
        artifact = load_artifact(path)

        expected = model.predict(features)
        actual = predict_frame(artifact, motor_frame)
        assert np.allclose(actual, expected)
        assert artifact["test_metrics"]["mae_celsius"] == 1.0
    finally:
        path.unlink(missing_ok=True)

