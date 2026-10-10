"""Loading, validation, and leakage-safe splitting for motor measurements."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from thermalguard.config import GROUP_COLUMN, RANDOM_SEED, REQUIRED_COLUMNS


class DataValidationError(ValueError):
    """Raised when a dataset cannot be used safely by the training pipeline."""


@dataclass(frozen=True)
class DatasetSummary:
    """Small, serializable summary used in logs and reports."""

    rows: int
    columns: int
    profiles: int
    missing_values: int
    duplicate_rows: int


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load the motor dataset from CSV and validate its required structure."""

    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. See data/README.md for setup instructions."
        )

    frame = pd.read_csv(csv_path)
    validate_dataset(frame)
    return frame


def validate_dataset(frame: pd.DataFrame) -> DatasetSummary:
    """Validate assumptions required for training and group-aware evaluation."""

    if frame.empty:
        raise DataValidationError("The dataset is empty.")

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing_columns:
        raise DataValidationError(f"Missing required columns: {', '.join(missing_columns)}")

    required = frame.loc[:, REQUIRED_COLUMNS]
    non_numeric = [name for name in REQUIRED_COLUMNS if not pd.api.types.is_numeric_dtype(required[name])]
    if non_numeric:
        raise DataValidationError(f"Required columns must be numeric: {', '.join(non_numeric)}")

    missing_count = int(required.isna().sum().sum())
    if missing_count:
        raise DataValidationError(f"Required columns contain {missing_count} missing values.")

    numeric_values = required.to_numpy(dtype=float, copy=False)
    if not np.isfinite(numeric_values).all():
        raise DataValidationError("Required columns contain infinite values.")

    profile_count = int(frame[GROUP_COLUMN].nunique())
    if profile_count < 2:
        raise DataValidationError("At least two measurement profiles are required.")

    return DatasetSummary(
        rows=len(frame),
        columns=len(frame.columns),
        profiles=profile_count,
        missing_values=missing_count,
        duplicate_rows=int(frame.duplicated().sum()),
    )


def split_by_profile(
    frame: pd.DataFrame,
    *,
    test_size: float = 0.2,
    random_state: int = RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create train and test sets whose measurement profiles never overlap."""

    validate_dataset(frame)
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")

    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_index, test_index = next(splitter.split(frame, groups=frame[GROUP_COLUMN]))
    train = frame.iloc[train_index].copy()
    test = frame.iloc[test_index].copy()

    overlap = set(train[GROUP_COLUMN].unique()) & set(test[GROUP_COLUMN].unique())
    if overlap:
        raise RuntimeError("Profile leakage detected while creating the holdout set.")

    return train, test

