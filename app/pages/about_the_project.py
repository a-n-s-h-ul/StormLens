from __future__ import annotations

import streamlit as st

from app.ui import hero, card, pill_row
from utils.config import PHASES

def render() -> None:
    hero(
        "Project Mission",
        "StormLens is an end-to-end framework designed to bridge the gap between complex meteorological data and actionable thunderstorm intelligence.",
        "Science-first | Interpretable | Reproducible"
    )

    st.markdown("### The Challenge")
    st.write(
        "Thunderstorms are multi-scale convective phenomena that pose significant risks to life and infrastructure. "
        "Predicting them requires integrating high-resolution atmospheric reanalysis data (ERA5) with robust "
        "data engineering and machine learning pipelines."
    )

    st.markdown("### Development Roadmap")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.info("Current Focus")
        card(
            "Phase 1: Intelligence",
            PHASES["Phase-1"] + "\n\nBuilding the data lake, ensuring quality through physical rule-based validation, and identifying key predictors via feature intelligence."
        )
    
    with c2:
        st.warning("Upcoming")
        card(
            "Phase 2: Modeling",
            PHASES["Phase-2"] + "\n\nDeveloping interpretable ML models like EBM (Explainable Boosting Machines) to ensure meteorologists can trust 'why' a prediction was made."
        )

    with c3:
        st.success("Future")
        card(
            "Phase 3: MLOps",
            PHASES["Phase-3"] + "\n\nContainerizing the stack for cloud deployment and establishing monitoring for data drift and model performance."
        )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("### Technical Stack")
        pill_row("Python", "Streamlit", "Pandas", "Scikit-Learn")
        pill_row("Plotly", "Xarray", "CDS API", "Docker")
        
        st.markdown("### Key Features")
        st.markdown(
            """
            - **Automated ERA5 Pipelines:** One-click ingestion from Copernicus Climate Data Store.
            - **Scientific Validation:** Meteorological range checks and timestamp continuity verification.
            - **Advanced Dimensionality Reduction:** PCA and t-SNE for feature space visualization.
            - **Feature Scoring:** Mutual Information and Correlation-based ranking.
            - **Integrated Reporting:** Automated PDF research summaries.
            """
        )

    with right:
        st.markdown("### Why StormLens?")
        st.markdown(
            "> 'StormLens is designed not just as a tool, but as a research methodology.'"
        )
        st.markdown(
            "By focusing on **white-box AI**, we ensure that every prediction can be traced back to atmospheric physics. "
            "This project demonstrates the full lifecycle of an ML project, from data ingestion to model-ready feature engineering."
        )
        
        if st.button("Return to Home", use_container_width=True):
            st.session_state["stormlens_page"] = "Home"
            st.rerun()
