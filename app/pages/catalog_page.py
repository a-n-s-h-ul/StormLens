from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.state import set_dataset
from app.ui import hero, kpi_strip
from utils.catalog import catalog_summary, scan_data_catalog
from utils.io import load_csv_cached


def render() -> None:
    hero(
        "Dataset Catalog",
        "Track raw, processed, validated, and report artifacts from one storage control center.",
        "Storage visibility | file metadata | quick CSV loading",
    )

    catalog = scan_data_catalog()
    summary = catalog_summary(catalog)
    if catalog.empty:
        kpi_strip([("0", "files"), ("0 MB", "stored"), ("4", "pipeline buckets"), ("Ready", "catalog scanner")])
        st.info("No data artifacts found yet. Fetch ERA5 data or upload a CSV to populate the catalog.")
        return

    kpi_strip(
        [
            (str(len(catalog)), "files"),
            (f"{catalog['size_mb'].sum():.2f} MB", "stored"),
            (str(catalog["bucket"].nunique()), "active buckets"),
            (catalog["modified"].max().strftime("%Y-%m-%d"), "latest update"),
        ]
    )

    st.subheader("Storage summary")
    st.dataframe(summary, use_container_width=True)

    st.subheader("Artifacts")
    bucket = st.selectbox("Filter bucket", ["all"] + sorted(catalog["bucket"].unique().tolist()))
    view = catalog if bucket == "all" else catalog[catalog["bucket"] == bucket]
    st.dataframe(view, use_container_width=True)

    csv_files = catalog[catalog["extension"] == ".csv"]
    if not csv_files.empty:
        st.subheader("Load CSV from catalog")
        selected = st.selectbox(
            "CSV artifact",
            csv_files["path"].tolist(),
            format_func=lambda p: f"{Path(p).parent.name}/{Path(p).name}",
        )
        if st.button("Load selected CSV", type="primary", use_container_width=True):
            path = Path(selected)
            df = load_csv_cached(path)
            st.success(f"Loaded `{path.name}` into the active workspace.")
            from app.ui import next_step_button
            next_step_button(
                "Validation",
                "Continue to validation",
                "next_validation_after_catalog",
            )
