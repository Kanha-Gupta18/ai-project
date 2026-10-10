"""Diagnostics for the final profile-held-out regression model."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.inspection import permutation_importance

from thermalguard.config import GROUP_COLUMN, TARGET_COLUMN
from thermalguard.config import RANDOM_SEED
from thermalguard.modeling import regression_metrics


def prediction_table(frame: pd.DataFrame, predictions: np.ndarray) -> pd.DataFrame:
    """Build row-level predictions and residuals for diagnostics."""

    result = frame.loc[:, [GROUP_COLUMN, TARGET_COLUMN]].copy()
    result = result.rename(columns={TARGET_COLUMN: "actual_celsius"})
    result["predicted_celsius"] = predictions
    result["error_celsius"] = result["predicted_celsius"] - result["actual_celsius"]
    result["absolute_error_celsius"] = result["error_celsius"].abs()
    return result


def profile_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    """Calculate error measures separately for every held-out profile."""

    rows = []
    for profile_id, group in predictions.groupby(GROUP_COLUMN):
        metrics = regression_metrics(group["actual_celsius"], group["predicted_celsius"])
        rows.append({GROUP_COLUMN: profile_id, "rows": len(group), **metrics})
    return pd.DataFrame(rows).sort_values("mae_celsius", ascending=False)


def permutation_importance_table(
    model: object,
    features: pd.DataFrame,
    target: pd.Series,
    *,
    max_rows: int = 20_000,
) -> pd.DataFrame:
    """Estimate model-agnostic feature importance using a bounded sample."""

    if len(features) > max_rows:
        sample = features.sample(n=max_rows, random_state=RANDOM_SEED)
        sample_target = target.loc[sample.index]
    else:
        sample = features
        sample_target = target

    result = permutation_importance(
        model,
        sample,
        sample_target,
        scoring="neg_mean_absolute_error",
        n_repeats=3,
        random_state=RANDOM_SEED,
        n_jobs=1,
    )
    return pd.DataFrame(
        {
            "feature": sample.columns,
            "mae_increase_celsius": result.importances_mean,
            "importance_std_celsius": result.importances_std,
        }
    ).sort_values("mae_increase_celsius", ascending=False)


def save_diagnostic_plots(predictions: pd.DataFrame, directory: str | Path) -> None:
    """Save actual-versus-predicted and residual diagnostic plots."""

    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    sample = predictions.sample(n=min(50_000, len(predictions)), random_state=42)
    sns.set_theme(style="whitegrid", context="notebook")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(
        sample["actual_celsius"],
        sample["predicted_celsius"],
        s=7,
        alpha=0.18,
        color="#155e75",
    )
    limits = [
        min(sample["actual_celsius"].min(), sample["predicted_celsius"].min()),
        max(sample["actual_celsius"].max(), sample["predicted_celsius"].max()),
    ]
    axes[0].plot(limits, limits, color="#c2410c", linewidth=1.5)
    axes[0].set(
        title="Actual and predicted rotor temperature",
        xlabel="Actual temperature (°C)",
        ylabel="Predicted temperature (°C)",
    )

    axes[1].scatter(
        sample["predicted_celsius"],
        sample["error_celsius"],
        s=7,
        alpha=0.18,
        color="#155e75",
    )
    axes[1].axhline(0, color="#c2410c", linewidth=1.5)
    axes[1].set(
        title="Residuals against predictions",
        xlabel="Predicted temperature (°C)",
        ylabel="Prediction error (°C)",
    )
    fig.tight_layout()
    fig.savefig(output / "final_model_diagnostics.png", dpi=160)
    plt.close(fig)

