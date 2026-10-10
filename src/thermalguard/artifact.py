"""Persistence and inference helpers for the selected ThermalGuard model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from thermalguard.modeling import CONTROLLER_FEATURES, MODEL_FEATURES, prepare_features

ARTIFACT_VERSION = 1


def save_artifact(
    model: Any,
    path: str | Path,
    metrics: dict[str, float],
    *,
    include_stator: bool,
) -> None:
    """Save the fitted model together with its inference contract."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    feature_names = MODEL_FEATURES if include_stator else CONTROLLER_FEATURES
    joblib.dump(
        {
            "artifact_version": ARTIFACT_VERSION,
            "model": model,
            "feature_names": list(feature_names),
            "include_stator": include_stator,
            "target": "pm",
            "test_metrics": metrics,
        },
        destination,
    )


def load_artifact(path: str | Path) -> dict[str, Any]:
    """Load and check a ThermalGuard model artifact."""

    artifact = joblib.load(Path(path))
    if artifact.get("artifact_version") != ARTIFACT_VERSION:
        raise ValueError("Unsupported ThermalGuard model artifact version.")
    expected_features = MODEL_FEATURES if artifact.get("include_stator") else CONTROLLER_FEATURES
    if artifact.get("feature_names") != list(expected_features):
        raise ValueError("The model artifact feature contract is incompatible.")
    return artifact


def predict_frame(artifact: dict[str, Any], frame: pd.DataFrame) -> np.ndarray:
    """Predict rotor temperature from raw sensor rows."""

    features = prepare_features(frame, include_stator=artifact["include_stator"])
    return np.asarray(artifact["model"].predict(features))

