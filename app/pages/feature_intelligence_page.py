from __future__ import annotations

import streamlit as st

from app.state import get_dataset
from app.ui import hero, next_step_button
from utils.feature_intelligence import score_features


def render() -> None:
    hero(
        "Feature Intelligence",
        "Rank atmospheric variables using correlation, mutual information, and variance signals.",
        "Outputs a composite score to highlight research-relevant predictors.",
    )

    ds = get_dataset()
    if ds is None:
        st.warning("Load a dataset first from **ERA5 Data Fetch** or **Upload CSV**.")
        return

    with st.expander("Feature scoring options", expanded=True):
        target = st.text_input(
            "Target column (optional, for mutual information + correlations)",
            value="CAPE",
        ).strip()
        method = st.selectbox("Mutual information type", ["auto", "regression", "classification"], index=0)
        top_k = st.slider("Top features to display", 5, 50, 20, 1)

    f_key = f"feat_result_{ds.name}"
    if st.button("Run feature intelligence", type="primary", use_container_width=True):
        with st.spinner("Scoring features..."):
            result = score_features(ds.df, target_col=target or None, mi_mode=method)
            st.session_state[f_key] = result

    if f_key in st.session_state:
        result = st.session_state[f_key]
        st.subheader("Ranked features")
        st.dataframe(result.ranking.head(int(top_k)), use_container_width=True)

        st.subheader("Importance chart")
        st.plotly_chart(result.figure, use_container_width=True)

        if result.insights:
            st.subheader("Insights")
            st.write(result.insights)

        st.divider()
        next_step_button(
            "Model Readiness",
            "Continue to model readiness",
            "next_readiness_after_features",
        )
    else:
        st.info("Click **Run feature intelligence** to score predictors.")
