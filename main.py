from __future__ import annotations

import streamlit as st

from app.pages import (
    home,
    about_the_project,
    era5_data_fetch,
    upload_csv,
    validation_page,
    eda_page,
    dimensionality_page,
    feature_intelligence_page,
    model_readiness_page,
    model_selector_preview,
    pipeline_status_page,
    catalog_page,
    reports_page,
)
from app.ui import app_header, apply_global_style
from utils.config import APP_NAME
from utils.logger import configure_logging


def main() -> None:
    configure_logging()
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="⛈️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_global_style()
    if "stormlens_page" not in st.session_state:
        st.session_state["stormlens_page"] = "Home Dashboard"

    pages = [
        "Home Dashboard",
        "Mission & Architecture",
        "Pipeline Status",
        "ERA5 Data Fetch",
        "Upload CSV",
        "Dataset Catalog",
        "Validation",
        "EDA",
        "Dimensionality Reduction",
        "Feature Intelligence",
        "Model Readiness",
        "Model Selector Preview",
        "Reports",
    ]
    
    # Sync selectbox with session state
    current_page = st.session_state["stormlens_page"]
    if current_page not in pages:
        current_page = pages[0]
        
    app_header(current_page)
    nav_left, nav_right = st.columns([1.5, 2.5], gap="large")
    with nav_left:
        selected_page = st.selectbox(
            "Module",
            options=pages,
            index=pages.index(current_page),
            key="module_nav_selectbox"
        )
        # Update session state if user manually changes the selectbox
        if selected_page != st.session_state["stormlens_page"]:
            st.session_state["stormlens_page"] = selected_page
            st.rerun()

    with nav_right:
        st.caption("Recommended Workflow")
        st.write("Fetch/Upload → Catalog → Validate → EDA → Reduction → Features → Readiness → Models → Reports")

    if selected_page == "Home Dashboard":
        home.render()
    elif selected_page == "Mission & Architecture":
        about_the_project.render()
    elif selected_page == "Pipeline Status":
        pipeline_status_page.render()
    elif selected_page == "ERA5 Data Fetch":
        era5_data_fetch.render()
    elif selected_page == "Upload CSV":
        upload_csv.render()
    elif selected_page == "Dataset Catalog":
        catalog_page.render()
    elif selected_page == "Validation":
        validation_page.render()
    elif selected_page == "EDA":
        eda_page.render()
    elif selected_page == "Dimensionality Reduction":
        dimensionality_page.render()
    elif selected_page == "Feature Intelligence":
        feature_intelligence_page.render()
    elif selected_page == "Model Readiness":
        model_readiness_page.render()
    elif selected_page == "Model Selector Preview":
        model_selector_preview.render()
    elif selected_page == "Reports":
        reports_page.render()
    else:
        st.error("Unknown page.")


if __name__ == "__main__":
    main()
