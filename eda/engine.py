from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd
import plotly.express as px

from utils.plotting import boxplot, correlation_heatmap, histogram, missing_values_bar, time_series


@dataclass(frozen=True)
class EDAResult:
    stats_table: pd.DataFrame
    missing_table: pd.DataFrame
    figures: list[object]


def _try_parse_timestamp(df: pd.DataFrame, col: Optional[str]) -> Optional[str]:
    if not col or col not in df.columns:
        return None
    try:
        parsed = pd.to_datetime(df[col], errors="coerce", utc=True)
        if parsed.notna().sum() == 0:
            return None
        return col
    except Exception:  # noqa: BLE001
        return None


def run_eda(
    df: pd.DataFrame,
    timestamp_col: Optional[str] = None,
    max_corr_cols: int = 30,
    focus_vars: Optional[Iterable[str]] = None,
) -> EDAResult:
    dfc = df.copy()
    numeric = dfc.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan)

    desc = numeric.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    desc["skewness"] = numeric.skew(numeric_only=True)
    desc["kurtosis"] = numeric.kurtosis(numeric_only=True)
    stats = desc.reset_index().rename(columns={"index": "feature"})

    missing = (
        dfc.isna()
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"index": "column", 0: "missing_fraction"})
    )

    figs: list[object] = []
    figs.append(missing_values_bar(dfc))

    corr_cols = numeric.columns[: max_corr_cols]
    if len(corr_cols) >= 2:
        figs.append(correlation_heatmap(numeric[corr_cols], title="Correlation heatmap (numeric subset)"))

    # Generic distributions for first few numeric columns
    for col in list(numeric.columns)[:6]:
        figs.append(histogram(numeric, col))
        figs.append(boxplot(numeric, col))

    ts = _try_parse_timestamp(dfc, timestamp_col)
    if ts:
        # Thunderstorm-focused diagnostics (if present)
        focus_vars = list(focus_vars or [])
        for col in focus_vars:
            if col in dfc.columns:
                figs.append(time_series(dfc, x=ts, y=col, title=f"{col} over time"))

    # CAPE/CIN specific if available
    if "CAPE" in dfc.columns:
        figs.append(px.ecdf(pd.to_numeric(dfc["CAPE"], errors="coerce"), title="CAPE ECDF"))
    if "CIN" in dfc.columns:
        figs.append(px.histogram(pd.to_numeric(dfc["CIN"], errors="coerce"), nbins=60, title="CIN distribution"))

    # Wind pattern analysis: wind speed and direction if u/v present
    if "u wind" in dfc.columns and "v wind" in dfc.columns:
        u = pd.to_numeric(dfc["u wind"], errors="coerce")
        v = pd.to_numeric(dfc["v wind"], errors="coerce")
        ws = np.sqrt(u**2 + v**2)
        wd = (np.degrees(np.arctan2(-u, -v)) + 360) % 360
        wind_df = pd.DataFrame({"wind_speed": ws, "wind_dir_deg": wd}).dropna()
        figs.append(px.histogram(wind_df, x="wind_speed", nbins=60, title="Wind speed distribution", template="plotly_dark"))
        figs.append(px.histogram(wind_df, x="wind_dir_deg", nbins=36, title="Wind direction distribution (deg)", template="plotly_dark"))

    # 3D Diagnostic for storm precursors
    potential_3d = ["CAPE", "temperature", "humidity", "2m_temperature", "total_precipitation", "2m_dewpoint_temperature"]
    found_3d = [c for c in potential_3d if c in dfc.columns]
    if len(found_3d) >= 3:
        from utils.plotting import scatter_3d_diagnostic
        figs.append(scatter_3d_diagnostic(dfc.sample(min(2000, len(dfc))), found_3d[0], found_3d[1], found_3d[2], color=found_3d[0]))

    return EDAResult(stats_table=stats, missing_table=missing, figures=figs)

