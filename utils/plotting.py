from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def missing_values_bar(df: pd.DataFrame, top_n: int = 40):
    miss = df.isna().mean().sort_values(ascending=False).head(top_n)
    fig = px.bar(
        miss.reset_index(),
        x="index",
        y=0,
        labels={"index": "column", 0: "missing_fraction"},
        title="Physical Gaps: Missing Data Fraction",
        template="plotly_dark",
        color_discrete_sequence=["#ff7a73"]
    )
    fig.update_layout(xaxis_tickangle=-45, height=450)
    return fig


def correlation_heatmap(df: pd.DataFrame, title: str = "Feature Interaction Matrix"):
    corr = df.corr(numeric_only=True)
    fig = px.imshow(
        corr,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=title,
        template="plotly_dark",
        aspect="auto"
    )
    fig.update_layout(height=750)
    return fig


def histogram(df: pd.DataFrame, col: str):
    fig = px.histogram(
        df, x=col, nbins=60, 
        title=f"Distribution: {col}",
        template="plotly_dark",
        color_discrete_sequence=["#46d9ff"]
    )
    fig.update_layout(height=450)
    return fig


def boxplot(df: pd.DataFrame, col: str):
    fig = px.box(
        df, y=col, 
        title=f"Outlier Analysis: {col}",
        template="plotly_dark"
    )
    fig.update_layout(height=450)
    return fig


def time_series(df: pd.DataFrame, x: str, y: str, title: str | None = None):
    fig = px.line(
        df, x=x, y=y, 
        title=title or f"Temporal Trend: {y}",
        template="plotly_dark"
    )
    fig.update_traces(line_color="#77e3b1")
    fig.update_layout(height=450)
    return fig


def scatter_3d_diagnostic(df: pd.DataFrame, x: str, y: str, z: str, color: str | None = None):
    fig = px.scatter_3d(
        df, x=x, y=y, z=z, color=color,
        title=f"3D Multi-Variate Diagnostic: {x} vs {y} vs {z}",
        template="plotly_dark",
        opacity=0.7
    )
    fig.update_layout(height=800)
    return fig


def quality_gauge(score: float, title: str = "Data Integrity Score"):
    score = float(np.clip(score, 0, 100))
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "white"},
                "bar": {"color": "#46d9ff"},
                "steps": [
                    {"range": [0, 50], "color": "rgba(255, 122, 115, 0.3)"},
                    {"range": [50, 80], "color": "rgba(255, 209, 102, 0.3)"},
                    {"range": [80, 100], "color": "rgba(119, 227, 177, 0.3)"}
                ],
            },
        )
    )
    fig.update_layout(template="plotly_dark", height=350)
    return fig

