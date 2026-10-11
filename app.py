"""ThermalGuard Streamlit prediction interface."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from thermalguard.app_logic import PredictionInputError, build_input_frame
from thermalguard.artifact import load_artifact, predict_frame

MODEL_PATH = Path("models/thermalguard_model.joblib")

INPUT_GROUPS = {
    "Thermal measurements": (
        ("ambient", "Ambient temperature", "°C"),
        ("coolant", "Coolant temperature", "°C"),
        ("stator_yoke", "Stator yoke temperature", "°C"),
        ("stator_tooth", "Stator tooth temperature", "°C"),
        ("stator_winding", "Stator winding temperature", "°C"),
    ),
    "Operating point": (
        ("motor_speed", "Motor speed", "rpm"),
        ("torque", "Torque", "Nm"),
    ),
    "Electrical measurements": (
        ("u_d", "Direct-axis voltage", "V"),
        ("u_q", "Quadrature-axis voltage", "V"),
        ("i_d", "Direct-axis current", "A"),
        ("i_q", "Quadrature-axis current", "A"),
    ),
}


@st.cache_resource
def get_artifact(path: Path) -> dict:
    """Load the model once for the Streamlit process."""

    return load_artifact(path)


def render_input(
    name: str,
    label: str,
    unit: str,
    summary: dict[str, dict[str, float]],
) -> float:
    """Render one bounded numeric sensor input."""

    limits = summary[name]
    return float(
        st.number_input(
            f"{label} ({unit})",
            min_value=float(limits["minimum"]),
            max_value=float(limits["maximum"]),
            value=float(limits["median"]),
            help=(
                f"Observed training range: {limits['minimum']:.2f} to "
                f"{limits['maximum']:.2f} {unit}."
            ),
            key=name,
        )
    )


def main() -> None:
    st.set_page_config(
        page_title="ThermalGuard motor estimator",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
        :root { color-scheme: light; }
        .stApp { background: #f7faf9; color: #17302d; }
        .block-container { max-width: 1180px; padding-top: 2.5rem; padding-bottom: 4rem; }
        h1, h2, h3 { color: #102a27; letter-spacing: -0.025em; }
        [data-testid="stMetric"] {
            background: #e8f1ef;
            border: 1px solid #c7d9d5;
            border-radius: 12px;
            padding: 1rem;
        }
        [data-testid="stForm"] {
            background: #ffffff;
            border: 1px solid #c7d9d5;
            border-radius: 12px;
            padding: 1.25rem;
        }
        .stButton > button, .stFormSubmitButton > button {
            min-height: 44px;
            border-radius: 8px;
            font-weight: 650;
        }
        *:focus-visible { outline: 3px solid #0f766e !important; outline-offset: 2px; }
        @media (max-width: 768px) {
            .block-container { padding: 1.25rem 1rem 3rem; }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Estimate Rotor Temperature")
    st.write("Enter one motor operating snapshot to estimate permanent-magnet temperature.")

    if not MODEL_PATH.is_file():
        st.error(
            "The trained model is missing. Add the dataset, then run "
            "`python scripts/train_models.py` before opening this application."
        )
        st.stop()

    try:
        artifact = get_artifact(MODEL_PATH)
    except (OSError, ValueError) as exc:
        st.error(f"The model artifact could not be loaded: {exc}")
        st.stop()

    metrics = artifact["test_metrics"]
    metric_columns = st.columns(3)
    metric_columns[0].metric("Test MAE", f"{metrics['mae_celsius']:.2f} °C")
    metric_columns[1].metric("Test R²", f"{metrics['r2']:.3f}")
    metric_columns[2].metric("Within ±5 °C", f"{metrics['within_5c_percent']:.1f}%")

    input_column, result_column = st.columns([1.55, 1], gap="large")
    with input_column:
        st.subheader("Motor measurements")
        with st.form("prediction_form", border=True):
            values: dict[str, float] = {}
            for group_name, fields in INPUT_GROUPS.items():
                st.markdown(f"#### {group_name}")
                first, second = st.columns(2)
                for index, (name, label, unit) in enumerate(fields):
                    with (first if index % 2 == 0 else second):
                        values[name] = render_input(
                            name, label, unit, artifact["input_summary"]
                        )
            submitted = st.form_submit_button(
                "Estimate temperature", type="primary", use_container_width=True
            )

    with result_column:
        st.subheader("Model estimate")
        if submitted:
            try:
                input_frame = build_input_frame(values, artifact["input_summary"])
                prediction = float(predict_frame(artifact, input_frame)[0])
            except (PredictionInputError, ValueError) as exc:
                st.error(f"Check the entered measurements: {exc}")
            else:
                st.metric("Estimated rotor temperature", f"{prediction:.1f} °C")
                st.success("Prediction completed using the saved model artifact.")
                st.caption(
                    f"The final test RMSE was {metrics['rmse_celsius']:.2f} °C. "
                    "This is a model-wide error measure, not a confidence interval "
                    "for this individual prediction."
                )
        else:
            st.info("Enter measurements and select Estimate temperature.")

        st.markdown("#### How to read this result")
        st.write(
            "The estimate describes the permanent-magnet temperature for the entered "
            "sensor snapshot. It is intended for coursework and model demonstration."
        )
        st.warning(
            "Do not use this estimate as the sole input to a motor shutdown or safety system."
        )

    with st.expander("Model and evaluation details"):
        st.write(
            "The selected estimator is Histogram Gradient Boosting. Model selection used "
            "validation profiles, followed by one evaluation on 14 untouched test profiles."
        )
        st.write(
            "The model uses stator temperatures, electrical measurements, speed, torque, "
            "coolant temperature, ambient temperature, and three derived features."
        )


if __name__ == "__main__":
    main()

