from __future__ import annotations

import streamlit as st

from app.state import get_dataset
from app.ui import card, hero, kpi_strip, pill_row, workflow_strip
from utils.config import DATA_DIR


def render() -> None:
    hero(
        "StormLens",
        "End-to-end meteorological data intelligence platform for thunderstorm prediction workflows.",
        "ERA5 ingestion | validation | EDA | PCA | feature intelligence | model readiness | reports",
    )
    pill_row(
        "ERA5 ingestion",
        "Quality scoring",
        "Interactive EDA",
        "PCA/t-SNE",
        "Feature ranking",
        "Model readiness",
        "PDF reports",
    )
    kpi_strip(
        [
            ("Phase-1", "dataset and intelligence pipeline"),
            ("Phase-2", "interpretable ML bridge"),
            ("Phase-3", "UI and MLOps-ready app"),
            ("Cloud", "deployment-ready structure"),
        ]
    )

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.subheader("Intelligence Workspace")
        card(
            "Project Mission & Architecture",
            "Understand the scientific challenge, the technical roadmap, and the MLOps-ready engineering design behind StormLens."
        )
        if st.button("Explore Mission", use_container_width=True):
            st.session_state["stormlens_page"] = "Mission & Architecture"
            st.rerun()

        st.markdown("### Research Workflow")
        workflow_strip(
            [
                ("Ingest", "ERA5/CSV to lake"),
                ("Validate", "Quality & Physics"),
                ("Analyze", "EDA & Reduction"),
                ("Score", "Feature Intelligence"),
                ("Report", "Package Artifacts"),
            ]
        )

        st.markdown("### Core Modules")
        c1, c2, c3 = st.columns(3)
        with c1:
            card(
                "Data Lake Engine",
                "Automated ingestion, local storage, cataloging, and metadata tracking.",
            )
        with c2:
            card(
                "Analytics Hub",
                "Advanced EDA, feature ranking, and atmospheric state projections.",
            )
        with c3:
            card(
                "Platform Specs",
                "Dockerized, Cloud-ready, and optimized for research reproducibility.",
            )

    with right:
        st.subheader("Active dataset")
        ds = get_dataset()
        if ds is None:
            card("No dataset loaded", "Use ERA5 ingestion or upload a CSV to begin analysis.")
        else:
            st.success(f"Loaded: **{ds.name}**")
            c1, c2 = st.columns(2)
            c1.metric("Rows", f"{len(ds.df):,}")
            c2.metric("Columns", f"{ds.df.shape[1]:,}")
            if ds.path:
                st.caption(f"Source: `{ds.path}`")
            with st.expander("Preview", expanded=True):
                st.dataframe(ds.df.head(200), use_container_width=True)
