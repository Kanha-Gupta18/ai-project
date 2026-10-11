"""Select, evaluate, explain, and package the ThermalGuard regression model."""

from __future__ import annotations

import json
import time
from pathlib import Path

from thermalguard.artifact import save_artifact
from thermalguard.config import DEFAULT_DATA_PATH, GROUP_COLUMN, RAW_MODEL_INPUTS
from thermalguard.data import load_dataset, split_by_profile
from thermalguard.evaluation import (
    permutation_importance_table,
    prediction_table,
    profile_metrics,
    save_diagnostic_plots,
)
from thermalguard.modeling import build_candidate_models, prepare_xy, regression_metrics

MODEL_DIR = Path("models")
METRIC_DIR = Path("reports/metrics")
TABLE_DIR = Path("reports/tables")
FIGURE_DIR = Path("reports/figures")


def main() -> None:
    frame = load_dataset(DEFAULT_DATA_PATH)
    development, test = split_by_profile(frame, test_size=0.2, random_state=42)
    train, validation = split_by_profile(development, test_size=0.2, random_state=43)

    results: dict[str, object] = {
        "split": {
            "strategy": "profile-separated train, validation, and test sets",
            "group_column": GROUP_COLUMN,
            "train_rows": len(train),
            "validation_rows": len(validation),
            "test_rows": len(test),
            "train_profiles": int(train[GROUP_COLUMN].nunique()),
            "validation_profiles": int(validation[GROUP_COLUMN].nunique()),
            "test_profiles": int(test[GROUP_COLUMN].nunique()),
            "profile_overlap": 0,
        },
        "validation_models": {},
    }

    selected = None
    selected_name = ""
    selected_include_stator = True
    best_mae = float("inf")
    for feature_set, include_stator in (("controller", False), ("enhanced", True)):
        x_train, y_train = prepare_xy(train, include_stator=include_stator)
        x_validation, y_validation = prepare_xy(
            validation, include_stator=include_stator
        )
        for model_name, model in build_candidate_models().items():
            name = f"{feature_set}__{model_name}"
            started = time.perf_counter()
            model.fit(x_train, y_train)
            predictions = model.predict(x_validation)
            metrics = regression_metrics(y_validation, predictions) | {
                "feature_set": feature_set,
                "feature_count": x_train.shape[1],
                "fit_seconds": round(time.perf_counter() - started, 3),
            }
            results["validation_models"][name] = metrics
            print(name, json.dumps(metrics, indent=2))
            if metrics["mae_celsius"] < best_mae:
                best_mae = metrics["mae_celsius"]
                selected = model
                selected_name = name
                selected_include_stator = include_stator

    if selected is None:
        raise RuntimeError("No candidate model was trained.")

    x_development, y_development = prepare_xy(
        development, include_stator=selected_include_stator
    )
    x_test, y_test = prepare_xy(test, include_stator=selected_include_stator)
    selected.fit(x_development, y_development)
    test_predictions = selected.predict(x_test)
    test_metrics = regression_metrics(y_test, test_predictions)
    results["selected_model"] = selected_name
    results["test_metrics"] = test_metrics

    predictions = prediction_table(test, test_predictions)
    by_profile = profile_metrics(predictions)
    feature_importance = permutation_importance_table(
        selected, x_test, y_test
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRIC_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    input_summary = {
        name: {
            "minimum": float(development[name].min()),
            "median": float(development[name].median()),
            "maximum": float(development[name].max()),
        }
        for name in RAW_MODEL_INPUTS
    }
    save_artifact(
        selected,
        MODEL_DIR / "thermalguard_model.joblib",
        test_metrics,
        include_stator=selected_include_stator,
        input_summary=input_summary,
    )
    (METRIC_DIR / "model_comparison.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    by_profile.to_csv(TABLE_DIR / "profile_metrics.csv", index=False)
    feature_importance.to_csv(TABLE_DIR / "permutation_importance.csv", index=False)
    save_diagnostic_plots(predictions, FIGURE_DIR)

    print("final_test", json.dumps(test_metrics, indent=2))
    print("worst_profiles")
    print(by_profile.head(5).to_string(index=False))
    print("feature_importance")
    print(feature_importance.head(8).to_string(index=False))


if __name__ == "__main__":
    main()

