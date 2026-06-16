from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.era5_fetcher import list_raw_csv_files
from app.state import get_dataset, set_dataset
from app.ui import hero, next_step_button
from utils.config import DATA_RAW_DIR
from utils.io import load_csv_cached, save_uploaded_file


def render() -> None:
    hero(
        "Upload CSV",
        "Bring your own datasets into the StormLens pipeline (raw → validated → reports).",
        "Tip: Keep a timestamp column like `time` for best time-series diagnostics.",
    )

    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded is not None:
        try:
            if st.session_state.get("last_uploaded_file") != uploaded.name:
                with st.spinner("Saving and loading CSV …"):
                    saved_path = save_uploaded_file(uploaded, DATA_RAW_DIR)
                    df = load_csv_cached(saved_path)
                    set_dataset(df, name=saved_path.name, path=saved_path)
                    st.session_state["last_uploaded_file"] = uploaded.name
                    st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Upload failed: {exc}")

    st.divider()
    st.subheader("Load an existing raw CSV")
    raw_csvs = list_raw_csv_files()
    if raw_csvs:
        pick = st.selectbox("Raw datasets", options=raw_csvs, format_func=lambda p: p.name)
        if st.button("Load dataset", use_container_width=True):
            df = load_csv_cached(pick)
            set_dataset(df, name=pick.name, path=pick)
            st.success(f"Loaded: `{pick.name}`")
            st.rerun()
    else:
        st.caption("No datasets in `data/raw/` yet.")

    ds = get_dataset()
    if ds is not None:
        st.divider()
        st.success(f"Active dataset: **{ds.name}** ({len(ds.df):,} rows, {ds.df.shape[1]:,} columns)")
        next_step_button(
            "Validation",
            "Continue to validation",
            "next_validation_after_upload_success",
        )
        with st.expander("Preview active dataset", expanded=False):
            st.dataframe(ds.df.head(300), use_container_width=True)
