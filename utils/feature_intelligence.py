from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import spearmanr
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression, VarianceThreshold


@dataclass(frozen=True)
class FeatureIntelligenceResult:
    ranking: pd.DataFrame
    figure: object
    insights: list[str]


def _numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.select_dtypes(include=[np.number]).copy()
    out = out.replace([np.inf, -np.inf], np.nan)
    return out


def score_features(
    df: pd.DataFrame,
    target_col: Optional[str] = None,
    mi_mode: str = "auto",
) -> FeatureIntelligenceResult:
    numeric = _numeric_df(df).dropna(axis=1, how="all")
    insights: list[str] = []

    if numeric.shape[1] < 2:
        ranking = pd.DataFrame({"feature": numeric.columns.tolist(), "score": []})
        fig = px.bar(title="Not enough numeric columns to score.")
        return FeatureIntelligenceResult(ranking=ranking, figure=fig, insights=["Insufficient numeric features."])

    target = None
    if target_col and target_col in numeric.columns:
        target = numeric[target_col]

    features = numeric.drop(columns=[target_col], errors="ignore")
    features_filled = features.fillna(features.median(numeric_only=True))

    pearson = pd.Series(index=features.columns, dtype=float)
    spearman = pd.Series(index=features.columns, dtype=float)
    mi = pd.Series(index=features.columns, dtype=float)

    if target is not None:
        t = target.fillna(target.median())
        pearson = features.corrwith(t, method="pearson").abs()
        for c in features.columns:
            try:
                r, _ = spearmanr(features[c], t, nan_policy="omit")
                spearman[c] = abs(r) if np.isfinite(r) else np.nan
            except Exception:  # noqa: BLE001
                spearman[c] = np.nan

        X = features_filled.values
        y = t.values
        mode = mi_mode
        if mode == "auto":
            mode = "regression"
        if mode == "classification":
            mi_vals = mutual_info_classif(X, y.astype(int), random_state=42)
        else:
            mi_vals = mutual_info_regression(X, y, random_state=42)
        mi = pd.Series(mi_vals, index=features.columns)
    else:
        insights.append("Target column not provided or not found; MI/correlation-to-target scores skipped.")

    vt = VarianceThreshold(threshold=0.0)
    vt.fit(features_filled)
    var = pd.Series(vt.variances_, index=features.columns)

    def _norm(s: pd.Series) -> pd.Series:
        s = s.replace([np.inf, -np.inf], np.nan)
        if s.dropna().empty:
            return s * np.nan
        mn, mx = s.min(skipna=True), s.max(skipna=True)
        if mx == mn:
            return pd.Series(0.0, index=s.index)
        return (s - mn) / (mx - mn)

    score = 0.4 * _norm(pearson).fillna(0) + 0.3 * _norm(spearman).fillna(0) + 0.2 * _norm(mi).fillna(0) + 0.1 * _norm(var).fillna(0)
    ranking = (
        pd.DataFrame(
            {
                "feature": features.columns,
                "pearson_abs": pearson.values,
                "spearman_abs": spearman.values,
                "mutual_info": mi.values,
                "variance": var.values,
                "composite_score": score.values,
            }
        )
        .sort_values("composite_score", ascending=False)
        .reset_index(drop=True)
    )

    fig = px.bar(
        ranking.head(25),
        x="composite_score",
        y="feature",
        orientation="h",
        title="Top feature signals (composite score)",
    )
    fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})

    if target is not None and not ranking.empty:
        insights.append(f"Top-ranked features are most associated with `{target_col}` by combined criteria.")
    if (var < 1e-6).sum() > 0:
        insights.append("Some features have near-zero variance; consider dropping them for modeling.")

    return FeatureIntelligenceResult(ranking=ranking, figure=fig, insights=insights)

