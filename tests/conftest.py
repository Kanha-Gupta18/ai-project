"""Shared test fixtures."""

import pandas as pd
import pytest


@pytest.fixture
def motor_frame() -> pd.DataFrame:
    """Return a small valid dataset containing four measurement profiles."""

    rows = []
    for profile_id in range(1, 5):
        for step in range(3):
            rows.append(
                {
                    "ambient": 20.0 + profile_id,
                    "coolant": 25.0 + step,
                    "motor_speed": 1000.0 + 50 * step,
                    "torque": 20.0 + profile_id,
                    "u_d": -10.0 - step,
                    "u_q": 100.0 + step,
                    "i_d": -30.0 - step,
                    "i_q": 15.0 + step,
                    "pm": 45.0 + profile_id + step,
                    "stator_yoke": 35.0 + profile_id + step,
                    "stator_tooth": 40.0 + profile_id + step,
                    "stator_winding": 42.0 + profile_id + step,
                    "profile_id": profile_id,
                }
            )
    return pd.DataFrame(rows)

