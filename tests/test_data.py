"""Tests for data validation and group-aware splitting."""

import numpy as np
import pytest

from thermalguard.data import DataValidationError, split_by_profile, validate_dataset


def test_validate_dataset_returns_summary(motor_frame):
    summary = validate_dataset(motor_frame)

    assert summary.rows == 12
    assert summary.profiles == 4
    assert summary.missing_values == 0


def test_validate_dataset_rejects_missing_column(motor_frame):
    invalid = motor_frame.drop(columns="pm")

    with pytest.raises(DataValidationError, match="pm"):
        validate_dataset(invalid)


def test_validate_dataset_rejects_non_finite_value(motor_frame):
    invalid = motor_frame.copy()
    invalid.loc[0, "torque"] = np.inf

    with pytest.raises(DataValidationError, match="infinite"):
        validate_dataset(invalid)


def test_split_by_profile_prevents_session_leakage(motor_frame):
    train, test = split_by_profile(motor_frame, test_size=0.25)

    train_profiles = set(train["profile_id"])
    test_profiles = set(test["profile_id"])
    assert train_profiles.isdisjoint(test_profiles)
    assert len(train) + len(test) == len(motor_frame)


def test_split_by_profile_is_reproducible(motor_frame):
    first_train, first_test = split_by_profile(motor_frame, test_size=0.25)
    second_train, second_test = split_by_profile(motor_frame, test_size=0.25)

    assert first_train.index.tolist() == second_train.index.tolist()
    assert first_test.index.tolist() == second_test.index.tolist()


def test_real_dataset_schema_when_available():
    from pathlib import Path

    from thermalguard.data import load_dataset

    path = Path("data/raw/measures_v2.csv")
    if not path.exists():
        pytest.skip("Real dataset is not available in this checkout.")

    frame = load_dataset(path)
    assert len(frame) == 1_330_816
    assert frame["profile_id"].nunique() == 69

