from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ModelReadinessResult:
    score: float
    checks: pd.DataFrame
    feature_table: pd.DataFrame
    recommendations: list[str]


def assess_model_readiness(df: pd.DataFrame, target_col: Optional[str] = None) -> ModelReadinessResult:
    rows = len(df)
    cols = df.shape[1]
    numeric = df.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan)
    numeric_cols = numeric.shape[1]
    missing_fraction = float(df.isna().mean().mean()) if rows else 1.0
    duplicate_fraction = float(df.duplicated().mean()) if rows else 1.0
    target_available = bool(target_col and target_col in df.columns)
    target_missing = float(df[target_col].isna().mean()) if target_available else np.nan

    checks = pd.DataFrame(
        [
            {"check": "Rows available", "value": rows, "status": "pass" if rows >= 500 else "watch"},
            {"check": "Columns available", "value": cols, "status": "pass" if cols >= 5 else "watch"},
            {"check": "Numeric features", "value": numeric_cols, "status": "pass" if numeric_cols >= 4 else "watch"},
            {
                "check": "Missing value fraction",
                "value": round(missing_fraction, 4),
                "status": "pass" if missing_fraction <= 0.1 else "watch",
            },
            {
                "check": "Duplicate row fraction",
                "value": round(duplicate_fraction, 4),
                "status": "pass" if duplicate_fraction <= 0.05 else "watch",
            },
            {
                "check": "Target column",
                "value": target_col if target_available else "not configured",
                "status": "pass" if target_available else "watch",
            },
            {
                "check": "Target missing fraction",
                "value": round(target_missing, 4) if target_available else "not available",
                "status": "pass" if target_available and target_missing <= 0.05 else "watch",
            },
        ]
    )

    score = 100.0
    score -= 25.0 if rows < 500 else 0.0
    score -= 15.0 if numeric_cols < 4 else 0.0
    score -= 30.0 * min(1.0, missing_fraction)
    score -= 15.0 * min(1.0, duplicate_fraction)
    score -= 15.0 if not target_available else 0.0
    if target_available:
        score -= 15.0 * min(1.0, target_missing)
    score = float(np.clip(score, 0.0, 100.0))

    feature_table = pd.DataFrame(
        {
            "feature": numeric.columns,
            "missing_fraction": numeric.isna().mean().values,
            "variance": numeric.var(numeric_only=True).values,
            "unique_values": numeric.nunique(dropna=True).values,
        }
    ).sort_values(["missing_fraction", "variance"], ascending=[True, False])

    recommendations: list[str] = []
    if rows < 500:
        recommendations.append("Collect more samples before training a robust ML model.")
    if numeric_cols < 4:
        recommendations.append("Add more atmospheric predictors such as CAPE, CIN, humidity, pressure, wind, and precipitation.")
    if missing_fraction > 0.1:
        recommendations.append("Add imputation or filtering before model training.")
    if not target_available:
        recommendations.append("Define a target label, such as thunderstorm occurrence or high-CAPE event class.")
    if duplicate_fraction > 0.05:
        recommendations.append("Remove duplicate rows before model training.")
    if not recommendations:
        recommendations.append("Dataset is suitable for baseline interpretable ML experiments.")

    return ModelReadinessResult(score=score, checks=checks, feature_table=feature_table, recommendations=recommendations)
