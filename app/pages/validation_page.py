from __future__ import annotations

import streamlit as st

from app.state import get_dataset
from app.ui import hero, next_step_button
from utils.config import DATA_VALIDATED_DIR
from utils.io import save_dataframe_csv
from validation.engine import validate_dataset


def render() -> None:
    hero(
        "Validation",
        "Scientific meteorological validation with data quality scoring and anomaly surfacing.",
        "Checks: missingness, duplicates, timestamp continuity, physical plausibility, outliers",
    )

    ds = get_dataset()
    if ds is None:
        st.warning("Load a dataset first from **ERA5 Data Fetch** or **Upload CSV**.")
        return

    st.subheader(f"Dataset: {ds.name}")
    with st.expander("Preview", expanded=False):
        st.dataframe(ds.df.head(200), use_container_width=True)

    # State persistence for validation results
    v_key = f"val_result_{ds.name}"
    if st.button("Run validation", type="primary", use_container_width=True):
        with st.spinner("Running validation checks..."):
            result = validate_dataset(ds.df)
            st.session_state[v_key] = result

    if v_key in st.session_state:
        result = st.session_state[v_key]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Quality score", f"{result.quality_score:.1f} / 100")
        with c2:
            st.metric("Warnings", f"{len(result.warnings):,}")
        with c3:
            st.metric("Rows flagged", f"{result.flagged_rows:,}")

        if result.warnings:
            st.warning("Warnings")
            st.write(result.warnings)

        st.subheader("Validation summary")
        st.dataframe(result.summary_table, use_container_width=True)

        st.subheader("Validation charts")
        for fig in result.figures:
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        next_step_button("EDA", "Continue to EDA", "next_eda_after_validation")

        st.divider()
        st.subheader("Export validated dataset")
        out_name = st.text_input("Validated filename", value=f"validated_{ds.name}")
        if st.button("Save validated CSV", use_container_width=True):
            out_path = DATA_VALIDATED_DIR / out_name
            if not out_path.name.lower().endswith(".csv"):
                out_path = out_path.with_suffix(".csv")
            save_dataframe_csv(ds.df, out_path)
            st.success(f"Saved: `{out_path}`")
    else:
        st.info("Click **Run validation** to begin scientific quality assessment.")
