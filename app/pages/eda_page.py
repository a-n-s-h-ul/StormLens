from __future__ import annotations

import streamlit as st

from app.state import get_dataset
from app.ui import hero, next_step_button
from eda.engine import run_eda


def render() -> None:
    hero(
        "EDA",
        "Automated exploratory data analysis tailored for thunderstorm research.",
        "Interactive plots: distributions, correlations, missingness, time-series diagnostics",
    )

    ds = get_dataset()
    if ds is None:
        st.warning("Load a dataset first from **ERA5 Data Fetch** or **Upload CSV**.")
        return

    st.subheader(f"Dataset: {ds.name}")

    with st.expander("EDA options", expanded=True):
        max_cols = st.slider("Max columns for pairwise correlation", 5, 60, 30, 1)
        ts_col = st.text_input("Timestamp column (optional)", value="time")
        focus = st.multiselect(
            "Thunderstorm focus variables (if present)",
            ["CAPE", "CIN", "humidity", "temperature", "u wind", "v wind", "precipitation", "pressure"],
            default=["CAPE", "CIN", "humidity", "u wind", "v wind", "precipitation"],
        )

    e_key = f"eda_result_{ds.name}"
    if st.button("Run automated EDA", type="primary", use_container_width=True):
        with st.spinner("Computing statistics and plots..."):
            result = run_eda(
                ds.df,
                timestamp_col=ts_col.strip() or None,
                max_corr_cols=int(max_cols),
                focus_vars=focus,
            )
            st.session_state[e_key] = result

    if e_key in st.session_state:
        result = st.session_state[e_key]
        st.subheader("Statistical summary")
        st.dataframe(result.stats_table, use_container_width=True)

        st.subheader("Missing values")
        st.dataframe(result.missing_table, use_container_width=True)

        st.subheader("Visual diagnostics")
        for fig in result.figures:
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        next_step_button(
            "Dimensionality Reduction",
            "Continue to dimensionality reduction",
            "next_reduction_after_eda",
        )
    else:
        st.info("Click **Run automated EDA** to generate visual diagnostics.")
