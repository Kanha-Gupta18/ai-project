"""Tests for physics-informed feature engineering."""

import pytest

from thermalguard.features import add_engineered_features


def test_add_engineered_features_uses_vector_magnitudes(motor_frame):
    enriched = add_engineered_features(motor_frame)

    first = enriched.iloc[0]
    assert first["current_magnitude"] == pytest.approx((30.0**2 + 15.0**2) ** 0.5)
    assert first["voltage_magnitude"] == pytest.approx((10.0**2 + 100.0**2) ** 0.5)
    assert first["coolant_ambient_delta"] == pytest.approx(4.0)
    assert "current_magnitude" not in motor_frame.columns

