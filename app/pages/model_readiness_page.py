from __future__ import annotations

import streamlit as st

from app.state import get_dataset
from app.ui import hero, kpi_strip, next_step_button
from utils.model_readiness import assess_model_readiness


def render() -> None:
    hero(
        "Model Readiness",
        "Evaluate whether the current dataset is ready for interpretable thunderstorm prediction models.",
        "Phase-2 bridge | target readiness | feature health | ML recommendations",
    )

    ds = get_dataset()
    if ds is None:
        st.warning("Load a dataset first from **ERA5 Data Fetch** or **Upload CSV**.")
        return

    target_options = ["None"] + ds.df.columns.tolist()
    target = st.selectbox("Target column for prediction", target_options, index=0)

    result = assess_model_readiness(ds.df, None if target == "None" else target)
    kpi_strip(
        [
            (f"{result.score:.1f}", "readiness score"),
            (f"{len(ds.df):,}", "rows"),
            (f"{ds.df.shape[1]:,}", "columns"),
            (target, "target"),
        ]
    )

    st.subheader("Readiness checks")
    st.dataframe(result.checks, use_container_width=True)

    st.subheader("Feature health")
    st.dataframe(result.feature_table, use_container_width=True)

    st.subheader("Recommended next actions")
    for item in result.recommendations:
        st.write(f"- {item}")

    st.divider()
    next_step_button(
        "Model Selector Preview",
        "Explore phase-2 model candidates",
        "next_model_selector_after_readiness",
    )
