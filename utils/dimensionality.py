from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.manifold import TSNE
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class ReductionResult:
    coordinates: pd.DataFrame
    loadings: pd.DataFrame
    explained_variance: pd.DataFrame
    scatter_figure: object
    variance_figure: object
    insights: list[str]


def _numeric_frame(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan)
    return numeric.dropna(axis=1, how="all")


def run_dimensionality_reduction(
    df: pd.DataFrame,
    method: str = "PCA",
    n_components: int = 2,
    color_col: Optional[str] = None,
    sample_size: int = 2500,
) -> ReductionResult:
    numeric = _numeric_frame(df)
    if numeric.shape[1] < 2:
        empty = pd.DataFrame()
        fig = px.scatter(title="Need at least two numeric columns for dimensionality reduction.")
        return ReductionResult(empty, empty, empty, fig, fig, ["Insufficient numeric features."])

    working = numeric.copy()
    if len(working) > sample_size:
        working = working.sample(sample_size, random_state=42)

    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    X = pipeline.fit_transform(working)
    n_components = max(2, min(int(n_components), X.shape[1], X.shape[0]))

    insights: list[str] = []
    method_upper = method.upper()

    if method_upper == "T-SNE":
        perplexity = min(30, max(5, (X.shape[0] - 1) // 3))
        reducer = TSNE(
            n_components=2,
            perplexity=perplexity,
            init="pca",
            learning_rate="auto",
            random_state=42,
        )
        reduced = reducer.fit_transform(X)
        coords = pd.DataFrame(reduced, columns=["Component 1", "Component 2"], index=working.index)
        explained = pd.DataFrame(
            {"component": ["Component 1", "Component 2"], "explained_variance_ratio": [np.nan, np.nan]}
        )
        loadings = pd.DataFrame()
        insights.append("t-SNE visualizes non-linear clusters in atmospheric data but does not preserve global variance.")
    else:
        pca = PCA(n_components=n_components, random_state=42)
        reduced = pca.fit_transform(X)
        coords = pd.DataFrame(
            reduced[:, :2],
            columns=["Component 1", "Component 2"],
            index=working.index,
        )
        explained = pd.DataFrame(
            {
                "component": [f"PC{i + 1}" for i in range(len(pca.explained_variance_ratio_))],
                "explained_variance_ratio": pca.explained_variance_ratio_,
                "cumulative_variance": np.cumsum(pca.explained_variance_ratio_),
            }
        )
        loadings = pd.DataFrame(
            pca.components_.T,
            index=working.columns,
            columns=[f"PC{i + 1}" for i in range(pca.components_.shape[0])],
        ).reset_index(names="feature")
        
        if not explained.empty:
            ev = explained["explained_variance_ratio"].head(2).sum() * 100
            insights.append(f"Physical variables are compressed: the first two components capture **{ev:.1f}%** of total variance.")
            
            # Identify top features for PC1
            top_pc1 = loadings.iloc[loadings["PC1"].abs().argsort()[::-1]].head(3)["feature"].tolist()
            insights.append(f"Dominant drivers for PC1: {', '.join(top_pc1)}.")

    if color_col and color_col in df.columns:
        color_values = df.loc[coords.index, color_col]
        coords[color_col] = color_values.values
        color_arg = color_col
    else:
        color_arg = None

    scatter = px.scatter(
        coords,
        x="Component 1",
        y="Component 2",
        color=color_arg,
        title=f"{method_upper} Atmospheric State Projection",
        opacity=0.75,
        template="plotly_dark"
    )

    # ADD LOADING VECTORS (BIPLOT) if PCA
    if method_upper == "PCA":
        # Scale loadings for visibility
        scale_factor = (coords["Component 1"].abs().max() + coords["Component 2"].abs().max()) / 2
        for _, row in loadings.iterrows():
            scatter.add_annotation(
                x=row["PC1"] * scale_factor,
                y=row["PC2"] * scale_factor,
                ax=0, ay=0, xanchor="center", yanchor="middle",
                text=row["feature"],
                showarrow=True,
                arrowhead=1,
                arrowcolor="rgba(255, 255, 255, 0.4)",
                font=dict(color="rgba(255, 255, 255, 0.8)", size=10)
            )

    scatter.update_layout(height=700)

    if "explained_variance_ratio" in explained.columns and explained["explained_variance_ratio"].notna().any():
        variance = px.bar(
            explained,
            x="component",
            y="explained_variance_ratio",
            text_auto=".2f",
            title="Explained Variance (Information Density)",
            template="plotly_dark"
        )
    else:
        variance = px.bar(title="Explained variance is not available for t-SNE.")
    variance.update_layout(height=450)

    return ReductionResult(
        coordinates=coords.reset_index(names="source_index"),
        loadings=loadings,
        explained_variance=explained,
        scatter_figure=scatter,
        variance_figure=variance,
        insights=insights,
    )
