"""Generate a compact, reproducible exploratory analysis of the PMSM dataset."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from thermalguard.config import DEFAULT_DATA_PATH, GROUP_COLUMN, TARGET_COLUMN
from thermalguard.data import load_dataset, validate_dataset
from thermalguard.features import add_engineered_features

FIGURE_DIR = Path("reports/figures")
METRIC_DIR = Path("reports/metrics")


def main() -> None:
    frame = load_dataset(DEFAULT_DATA_PATH)
    summary = validate_dataset(frame)
    enriched = add_engineered_features(frame)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    METRIC_DIR.mkdir(parents=True, exist_ok=True)

    numeric_summary = frame.describe().T.round(4).to_dict(orient="index")
    profile_sizes = frame.groupby(GROUP_COLUMN).size()
    payload = {
        "dataset": summary.__dict__,
        "target": {
            "minimum_celsius": float(frame[TARGET_COLUMN].min()),
            "maximum_celsius": float(frame[TARGET_COLUMN].max()),
            "mean_celsius": float(frame[TARGET_COLUMN].mean()),
            "standard_deviation_celsius": float(frame[TARGET_COLUMN].std()),
        },
        "profiles": {
            "minimum_rows": int(profile_sizes.min()),
            "maximum_rows": int(profile_sizes.max()),
            "median_rows": float(profile_sizes.median()),
        },
        "numeric_summary": numeric_summary,
    }
    (METRIC_DIR / "dataset_summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    sample = enriched.sample(n=min(100_000, len(enriched)), random_state=42)
    sns.set_theme(style="whitegrid", context="notebook")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    sns.histplot(sample[TARGET_COLUMN], bins=45, ax=axes[0], color="#c2410c")
    axes[0].set(title="Rotor temperature distribution", xlabel="Permanent magnet temperature (°C)")
    profile_sizes.sort_values().plot(kind="bar", ax=axes[1], color="#155e75", width=0.8)
    axes[1].set(title="Measurements per operating profile", xlabel="Profile", ylabel="Rows")
    axes[1].tick_params(axis="x", labelbottom=False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "dataset_overview.png", dpi=160)
    plt.close(fig)

    correlation_columns = [
        "pm",
        "ambient",
        "coolant",
        "motor_speed",
        "torque",
        "current_magnitude",
        "voltage_magnitude",
        "coolant_ambient_delta",
    ]
    correlations = sample[correlation_columns].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(correlations, cmap="vlag", center=0, annot=True, fmt=".2f", ax=ax)
    ax.set_title("Spearman correlations on a reproducible sample")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "correlation_heatmap.png", dpi=160)
    plt.close(fig)

    print(json.dumps(payload["dataset"] | payload["target"] | payload["profiles"], indent=2))


if __name__ == "__main__":
    main()

