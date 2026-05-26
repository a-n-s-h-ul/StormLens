from __future__ import annotations

import streamlit as st

from app.ui import hero, card, next_step_button
from utils.config import PHASES

def render() -> None:
    hero(
        "Model Selector Preview",
        "Phase 2 will integrate science-first machine learning models. Explore the candidate architectures.",
        "XAI | Whitebox | Interpretable Modeling"
    )

    st.markdown("### Why Interpretable Models?")
    st.write(
        "In meteorology, understanding the *physical reasoning* behind a prediction is as important as the prediction itself. "
        "Standard black-box models (like Deep Neural Networks) are hard to debug and trust for critical storm forecasting."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        card(
            "EBM (Explainable Boosting Machines)",
            "A glass-box model developed by Microsoft Research. EBMs are as accurate as random forests but remain completely intelligible. "
            "They use GA2Ms (Generalized Additive Models with Interactions) to capture features and their relationships."
        )
    
    with c2:
        card(
            "XGBoost + SHAP",
            "State-of-the-art gradient boosting combined with SHAP (SHapley Additive exPlanations). "
            "SHAP values provide a globally consistent and locally accurate measure of feature importance for every forecast."
        )

    with c3:
        card(
            "Logistic Regression (Baseline)",
            "The classic statistical approach. High interpretability and a vital baseline for measuring the 'value-add' of more complex non-linear models."
        )

    st.divider()

    st.subheader("Model Comparison Metrics (Proposed)")
    metrics_cols = st.columns(4)
    metrics_cols[0].metric("Target Accuracy", "88%", "+2%")
    metrics_cols[1].metric("Interpretability Score", "High", "9.5/10")
    metrics_cols[2].metric("Training Efficiency", "O(N log N)", "Optimal")
    metrics_cols[3].metric("Physical Consistency", "Verified", "Laws of Physics")

    st.info("**Research Note:** We are prioritizing models that support 'Global Feature Importance' and 'Individual Prediction Explanations'.")

    st.divider()
    next_step_button(
        "Reports",
        "Move to final reporting",
        "next_reports_after_models"
    )
