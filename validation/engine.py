from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px

from utils.plotting import missing_values_bar, quality_gauge


@dataclass(frozen=True)
class ValidationResult:
    summary_table: pd.DataFrame
    warnings: list[str]
    quality_score: float
    flagged_rows: int
    figures: list[object]


def _find_timestamp_col(df: pd.DataFrame) -> Optional[str]:
    for cand in ["time", "timestamp", "datetime", "valid_time", "date"]:
        if cand in df.columns:
            return cand
    return None


def validate_dataset(df: pd.DataFrame) -> ValidationResult:
    warnings: list[str] = []
    dfc = df.copy()

    n_rows = len(dfc)
    missing_frac = float(dfc.isna().mean().mean()) if n_rows else 0.0
    dup_count = int(dfc.duplicated().sum()) if n_rows else 0

    # Attempt timestamp checks
    ts_col = _find_timestamp_col(dfc)
    ts_continuity_breaks = 0
    if ts_col:
        try:
            t = pd.to_datetime(dfc[ts_col], errors="coerce", utc=True)
            invalid_ts = int(t.isna().sum())
            if invalid_ts:
                warnings.append(f"{invalid_ts} invalid timestamps in `{ts_col}`.")
            dt_sorted = t.sort_values()
            diffs = dt_sorted.diff().dropna()
            if not diffs.empty:
                mode = diffs.mode()
                if not mode.empty:
                    expected = mode.iloc[0]
                    ts_continuity_breaks = int((diffs != expected).sum())
                    if ts_continuity_breaks > 0:
                        warnings.append(
                            f"Timestamp continuity issue: {ts_continuity_breaks} irregular intervals (expected ~{expected})."
                        )
        except Exception:  # noqa: BLE001
            warnings.append("Timestamp parsing failed; continuity checks skipped.")

    # Domain checks (only if columns exist)
    flagged = pd.Series(False, index=dfc.index)

    def flag_where(cond, message: str):
        nonlocal flagged
        if cond is None:
            return
        count = int(cond.fillna(False).sum())
        if count:
            flagged = flagged | cond.fillna(False)
            warnings.append(f"{message} ({count} rows).")

    if "CAPE" in dfc.columns:
        cape = pd.to_numeric(dfc["CAPE"], errors="coerce")
        flag_where(cape < 0, "Negative CAPE detected")
    if "humidity" in dfc.columns:
        rh = pd.to_numeric(dfc["humidity"], errors="coerce")
        flag_where((rh < 0) | (rh > 100), "Humidity outside 0–100%")
    if "pressure" in dfc.columns:
        p = pd.to_numeric(dfc["pressure"], errors="coerce")
        # Surface pressure typically around 70k–110k Pa; allow a broader scientific range.
        flag_where((p < 40_000) | (p > 120_000), "Potentially invalid surface pressure (Pa)")

    for wind_col in ["u wind", "v wind"]:
        if wind_col in dfc.columns:
            w = pd.to_numeric(dfc[wind_col], errors="coerce")
            flag_where(w.abs() > 80, f"Wind anomaly: |{wind_col}| > 80 m/s")

    # Outlier detection (robust z-score via MAD) on numeric cols
    numeric = dfc.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan)
    outlier_rows = 0
    if not numeric.empty:
        med = numeric.median()
        mad = (numeric - med).abs().median().replace(0, np.nan)
        robust_z = 0.6745 * (numeric - med) / mad
        outlier_mask = (robust_z.abs() > 8).any(axis=1)
        outlier_rows = int(outlier_mask.sum())
        if outlier_rows:
            warnings.append(f"Outlier detection flagged {outlier_rows} rows (robust z-score > 8).")
            flagged = flagged | outlier_mask.fillna(False)

    flagged_rows = int(flagged.sum())

    # Quality score (simple weighted heuristic for Phase-1)
    score = 100.0
    score -= 45.0 * min(1.0, missing_frac * 2.0)
    score -= 15.0 * min(1.0, dup_count / max(1, n_rows))
    score -= 20.0 * min(1.0, flagged_rows / max(1, n_rows))
    score -= 10.0 * min(1.0, ts_continuity_breaks / max(1, n_rows))
    score = float(np.clip(score, 0.0, 100.0))

    summary = pd.DataFrame(
        [
            {"check": "rows", "value": n_rows},
            {"check": "columns", "value": int(dfc.shape[1])},
            {"check": "missing_fraction_mean", "value": round(missing_frac, 6)},
            {"check": "duplicate_rows", "value": dup_count},
            {"check": "timestamp_column", "value": ts_col or "not_found"},
            {"check": "timestamp_irregular_intervals", "value": ts_continuity_breaks},
            {"check": "flagged_rows", "value": flagged_rows},
            {"check": "quality_score", "value": round(score, 2)},
        ]
    )

    figs: list[object] = [quality_gauge(score), missing_values_bar(dfc)]
    if "CAPE" in dfc.columns:
        cape = pd.to_numeric(dfc["CAPE"], errors="coerce")
        figs.append(px.histogram(cape, nbins=60, title="CAPE distribution"))

    return ValidationResult(
        summary_table=summary,
        warnings=warnings,
        quality_score=score,
        flagged_rows=flagged_rows,
        figures=figs,
    )

