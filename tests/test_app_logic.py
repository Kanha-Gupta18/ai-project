"""Tests for interface input validation."""

import pytest

from thermalguard.app_logic import PredictionInputError, build_input_frame


def test_build_input_frame_accepts_values_inside_training_ranges():
    summary = {"ambient": {"minimum": 10.0, "median": 20.0, "maximum": 30.0}}

    frame = build_input_frame({"ambient": 22.0}, summary)

    assert frame.loc[0, "ambient"] == 22.0


def test_build_input_frame_rejects_out_of_range_values():
    summary = {"ambient": {"minimum": 10.0, "median": 20.0, "maximum": 30.0}}

    with pytest.raises(PredictionInputError, match="between"):
        build_input_frame({"ambient": 35.0}, summary)


def test_build_input_frame_rejects_missing_values():
    summary = {"ambient": {"minimum": 10.0, "median": 20.0, "maximum": 30.0}}

    with pytest.raises(PredictionInputError, match="Missing"):
        build_input_frame({}, summary)
