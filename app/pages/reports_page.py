from __future__ import annotations

import streamlit as st

from app.state import get_dataset
from app.ui import hero
from eda.engine import run_eda
from reports.generator import generate_reports_bundle
from utils.feature_intelligence import score_features
from validation.engine import validate_dataset


def render() -> None:
    hero(
        "Reports",
        "Generate downloadable scientific reports (PDF + CSV summaries).",
        "Bundle includes dataset stats plus optional validation, EDA, and feature ranking sections.",
    )

    ds = get_dataset()
    if ds is None:
        st.warning("Load a dataset first from **ERA5 Data Fetch** or **Upload CSV**.")
        return

    with st.expander("Report options", expanded=True):
        include_eda = st.checkbox("Include EDA summary", value=True)
        include_validation = st.checkbox("Include validation report", value=True)
        include_features = st.checkbox("Include feature intelligence", value=True)
        ts_col = st.text_input("Timestamp column (EDA)", value="time").strip() or None
        target = st.text_input("Target column (Feature Intelligence)", value="CAPE").strip() or None

    if st.button("Generate report bundle", type="primary", use_container_width=True):
        with st.spinner("Building reports …"):
            validation_result = validate_dataset(ds.df) if include_validation else None
            eda_result = run_eda(ds.df, timestamp_col=ts_col) if include_eda else None
            feature_result = score_features(ds.df, target_col=target) if include_features else None

            bundle = generate_reports_bundle(
                dataset_name=ds.name,
                df=ds.df,
                validation_result=validation_result,
                eda_result=eda_result,
                feature_result=feature_result,
            )

        st.success("Report bundle created.")
        st.write("Artifacts:")
        st.json({k: str(v) for k, v in bundle.items()}, expanded=False)

        st.divider()
        for label, path in bundle.items():
            with open(path, "rb") as f:
                st.download_button(
                    f"Download {label}",
                    data=f,
                    file_name=path.name,
                    use_container_width=True,
                )
