from __future__ import annotations

import streamlit as st

from app.state import get_dataset
from app.ui import hero, kpi_strip, workflow_strip
from utils.catalog import scan_data_catalog


def render() -> None:
    hero(
        "Pipeline Status",
        "A single executive view of project progress across ingestion, validation, analytics, features, and reports.",
        "CV-ready platform view | artifact tracking | active workspace health",
    )

    ds = get_dataset()
    catalog = scan_data_catalog()

    raw_count = int((catalog["bucket"] == "raw").sum()) if not catalog.empty else 0
    validated_count = int((catalog["bucket"] == "validated").sum()) if not catalog.empty else 0
    report_count = int((catalog["bucket"] == "reports").sum()) if not catalog.empty else 0

    kpi_strip(
        [
            ("Loaded" if ds is not None else "Empty", "active dataset"),
            (str(raw_count), "raw artifacts"),
            (str(validated_count), "validated artifacts"),
            (str(report_count), "report artifacts"),
        ]
    )

    workflow_strip(
        [
            ("Ingest", "ERA5 or CSV loaded"),
            ("Validate", "Quality checks complete"),
            ("Explore", "EDA generated"),
            ("Score", "Features ranked"),
            ("Package", "Reports exported"),
        ]
    )

    st.markdown("### Engineering Architecture")
    st.markdown(
        """
        ```mermaid
        graph LR
          A[(ERA5 API)] --> B[Ingest Engine]
          C[Raw CSV] --> B
          B --> D{Quality Gate}
          D -- Passes --> E[Validated Store]
          D -- Fails --> F[Anomaly Log]
          E --> G[EDA Dashboard]
          G --> H[PCA Projection]
          H --> I[Feature Scoring]
          I --> J[Model Readiness]
          J --> K[PDF Report]
        ```
        """,
        unsafe_allow_html=True
    )

    st.subheader("Current workspace")
    if ds is None:
        st.info("No active dataset. Start with ERA5 Data Fetch or Upload CSV.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Dataset", ds.name)
        c2.metric("Rows", f"{len(ds.df):,}")
        c3.metric("Columns", f"{ds.df.shape[1]:,}")
        st.dataframe(ds.df.head(100), use_container_width=True)

    st.subheader("Recent artifacts")
    if catalog.empty:
        st.caption("No artifacts yet.")
    else:
        st.dataframe(catalog.sort_values("modified", ascending=False).head(20), use_container_width=True)
