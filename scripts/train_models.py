"""Train candidate models with a profile-held-out test set."""

from __future__ import annotations

import json
import time
from pathlib import Path

import joblib

from thermalguard.config import DEFAULT_DATA_PATH, GROUP_COLUMN
from thermalguard.data import load_dataset, split_by_profile
from thermalguard.modeling import build_candidate_models, prepare_xy, regression_metrics

MODEL_DIR = Path("models")
METRIC_DIR = Path("reports/metrics")


def main() -> None:
    frame = load_dataset(DEFAULT_DATA_PATH)
    train, test = split_by_profile(frame, test_size=0.2)
    results: dict[str, object] = {
        "split": {
            "strategy": "GroupShuffleSplit",
            "group_column": GROUP_COLUMN,
            "train_rows": len(train),
            "test_rows": len(test),
            "train_profiles": int(train[GROUP_COLUMN].nunique()),
            "test_profiles": int(test[GROUP_COLUMN].nunique()),
            "profile_overlap": 0,
        },
        "models": {},
    }

    fitted_models = {}
    for feature_set, include_stator in (("controller", False), ("enhanced", True)):
        x_train, y_train = prepare_xy(train, include_stator=include_stator)
        x_test, y_test = prepare_xy(test, include_stator=include_stator)
        for model_name, model in build_candidate_models().items():
            name = f"{feature_set}__{model_name}"
            started = time.perf_counter()
            model.fit(x_train, y_train)
            predictions = model.predict(x_test)
            results["models"][name] = regression_metrics(y_test, predictions) | {
                "feature_set": feature_set,
                "feature_count": x_train.shape[1],
                "fit_seconds": round(time.perf_counter() - started, 3),
            }
            fitted_models[name] = model
            print(name, json.dumps(results["models"][name], indent=2))

    best_name = min(
        results["models"], key=lambda name: results["models"][name]["mae_celsius"]
    )
    results["selected_model"] = best_name

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRIC_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(fitted_models[best_name], MODEL_DIR / "thermalguard_model.joblib")
    (METRIC_DIR / "model_comparison.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()

