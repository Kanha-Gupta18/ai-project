"""Shared configuration for the ThermalGuard data pipeline."""

from pathlib import Path

RANDOM_SEED = 42
TARGET_COLUMN = "pm"
GROUP_COLUMN = "profile_id"

RAW_FEATURES = (
    "ambient",
    "coolant",
    "motor_speed",
    "torque",
    "u_d",
    "u_q",
    "i_d",
    "i_q",
)

STATOR_FEATURES = (
    "stator_yoke",
    "stator_tooth",
    "stator_winding",
)

REQUIRED_COLUMNS = (*RAW_FEATURES, *STATOR_FEATURES, TARGET_COLUMN, GROUP_COLUMN)
RAW_MODEL_INPUTS = (*RAW_FEATURES, *STATOR_FEATURES)
DEFAULT_DATA_PATH = Path("data/raw/measures_v2.csv")

