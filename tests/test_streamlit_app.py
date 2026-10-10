"""Smoke test for the complete Streamlit prediction flow."""

import os
import tempfile
from pathlib import Path

TEMPORARY_ROOT = Path("work/streamlit-test-temp").resolve()
TEMPORARY_ROOT.mkdir(parents=True, exist_ok=True)
os.environ["TMP"] = str(TEMPORARY_ROOT)
os.environ["TEMP"] = str(TEMPORARY_ROOT)
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")
tempfile.tempdir = str(TEMPORARY_ROOT)

import pytest
from streamlit.testing.v1 import AppTest


def test_streamlit_app_predicts_with_generated_artifact():
    if not Path("models/thermalguard_model.joblib").exists():
        pytest.skip("Train the model artifact before running the interface smoke test.")

    app = AppTest.from_file("app.py").run(timeout=30)
    assert not app.exception
    assert len(app.number_input) == 11
    assert app.button[0].label == "Estimate temperature"

    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert any(metric.label == "Estimated rotor temperature" for metric in app.metric)
    assert app.success[0].value == "Prediction completed using the saved model artifact."

