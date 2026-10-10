"""Feature engineering grounded in PMSM electrical measurements."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_engineered_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add interpretable magnitude and temperature-difference features."""

    required = {"i_d", "i_q", "u_d", "u_q", "coolant", "ambient"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Cannot engineer features; missing columns: {', '.join(missing)}")

    enriched = frame.copy()
    enriched["current_magnitude"] = np.hypot(enriched["i_d"], enriched["i_q"])
    enriched["voltage_magnitude"] = np.hypot(enriched["u_d"], enriched["u_q"])
    enriched["coolant_ambient_delta"] = enriched["coolant"] - enriched["ambient"]
    return enriched

