from __future__ import annotations

import streamlit as st

from app.state import get_dataset
from app.ui import hero, next_step_button
from utils.dimensionality import run_dimensionality_reduction


def render() -> None:
    hero(
        "Dimensionality Reduction",
        "Compress atmospheric variables into low-dimensional feature space for ML readiness and pattern discovery.",
        "PCA | t-SNE | explained variance | feature loadings",
    )

    ds = get_dataset()
    if ds is None:
        st.warning("Load a dataset first from **ERA5 Data Fetch** or **Upload CSV**.")
        return

    numeric_cols = ds.df.select_dtypes(include="number").columns.tolist()
    all_cols = ["None"] + ds.df.columns.tolist()

    with st.expander("Reduction options", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            method = st.selectbox("Method", ["PCA", "t-SNE"], index=0)
        with c2:
            n_components = st.slider("PCA components", 2, max(2, min(10, len(numeric_cols))), 3)
        with c3:
            color_col = st.selectbox("Color by", all_cols, index=0)
        sample_size = st.slider("Max sample size", 250, 10000, 2500, 250)

    d_key = f"dim_result_{ds.name}"
    if st.button("Run dimensionality reduction", type="primary", use_container_width=True):
        with st.spinner("Building feature-space projection..."):
            result = run_dimensionality_reduction(
                ds.df,
                method=method,
                n_components=n_components,
                color_col=None if color_col == "None" else color_col,
                sample_size=sample_size,
            )
            st.session_state[d_key] = result

    if d_key in st.session_state:
        result = st.session_state[d_key]
        if result.insights:
            for msg in result.insights:
                st.info(msg)

        st.subheader("Feature-space projection")
        st.plotly_chart(result.scatter_figure, use_container_width=True)

        st.subheader("Explained variance")
        st.plotly_chart(result.variance_figure, use_container_width=True)
        st.dataframe(result.explained_variance, use_container_width=True)

        if not result.loadings.empty:
            st.subheader("PCA feature loadings")
            st.dataframe(result.loadings, use_container_width=True)

        st.subheader("Projection coordinates")
        st.dataframe(result.coordinates.head(300), use_container_width=True)

        st.divider()
        next_step_button(
            "Model Readiness",
            "Continue to model readiness",
            "next_model_readiness_after_reduction",
        )
    else:
        st.info("Click **Run dimensionality reduction** to visualize the atmospheric state space.")
