"""Validation helpers shared by the Streamlit interface and its tests."""

from __future__ import annotations

import pandas as pd


class PredictionInputError(ValueError):
    """Raised when interface values do not match the model input contract."""


def build_input_frame(
    values: dict[str, float], input_summary: dict[str, dict[str, float]]
) -> pd.DataFrame:
    """Validate one sensor reading and return a single-row data frame."""

    expected = set(input_summary)
    received = set(values)
    if missing := sorted(expected - received):
        raise PredictionInputError(f"Missing sensor inputs: {', '.join(missing)}")
    if unexpected := sorted(received - expected):
        raise PredictionInputError(f"Unexpected sensor inputs: {', '.join(unexpected)}")

    for name, value in values.items():
        limits = input_summary[name]
        if not limits["minimum"] <= value <= limits["maximum"]:
            raise PredictionInputError(
                f"{name} must be between {limits['minimum']:.2f} and "
                f"{limits['maximum']:.2f}."
            )

    return pd.DataFrame([values])

