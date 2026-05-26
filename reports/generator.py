from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Optional

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from utils.config import DATA_REPORTS_DIR, ensure_project_dirs


def _ts() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in name).strip("_")


def _df_to_table(df: pd.DataFrame, max_rows: int = 40) -> Table:
    head = df.head(max_rows)
    data = [head.columns.tolist()] + head.astype(str).values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B1F3A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]
        )
    )
    return table


def generate_pdf_report(
    path: Path,
    dataset_name: str,
    df: pd.DataFrame,
    validation_result=None,
    eda_result=None,
    feature_result=None,
) -> Path:
    ensure_project_dirs()
    path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"<b>StormLens Scientific Report</b>", styles["Title"]))
    story.append(Paragraph(f"Dataset: <b>{dataset_name}</b>", styles["Normal"]))
    story.append(Paragraph(f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Dataset overview</b>", styles["Heading2"]))
    overview = pd.DataFrame(
        [
            {"metric": "rows", "value": len(df)},
            {"metric": "columns", "value": df.shape[1]},
            {"metric": "missing_fraction_mean", "value": float(df.isna().mean().mean()) if len(df) else 0.0},
        ]
    )
    story.append(_df_to_table(overview, max_rows=20))
    story.append(Spacer(1, 12))

    if validation_result is not None:
        story.append(Paragraph("<b>Validation</b>", styles["Heading2"]))
        story.append(Paragraph(f"Quality score: <b>{validation_result.quality_score:.1f}/100</b>", styles["Normal"]))
        story.append(Spacer(1, 6))
        story.append(_df_to_table(validation_result.summary_table, max_rows=40))
        if getattr(validation_result, "warnings", None):
            story.append(Spacer(1, 8))
            story.append(Paragraph("<b>Warnings</b>", styles["Heading3"]))
            for w in validation_result.warnings[:20]:
                story.append(Paragraph(f"- {w}", styles["Normal"]))
        story.append(Spacer(1, 12))

    if eda_result is not None:
        story.append(Paragraph("<b>EDA summary</b>", styles["Heading2"]))
        story.append(_df_to_table(eda_result.stats_table, max_rows=30))
        story.append(Spacer(1, 12))

    if feature_result is not None:
        story.append(Paragraph("<b>Feature intelligence</b>", styles["Heading2"]))
        story.append(_df_to_table(feature_result.ranking.head(30), max_rows=30))
        story.append(Spacer(1, 12))

    doc = SimpleDocTemplate(str(path), pagesize=A4, title="StormLens Report")
    doc.build(story)
    return path


def generate_reports_bundle(
    dataset_name: str,
    df: pd.DataFrame,
    validation_result=None,
    eda_result=None,
    feature_result=None,
) -> dict[str, Path]:
    ensure_project_dirs()
    stamp = _ts()
    base = _safe_name(Path(dataset_name).stem)

    out_pdf = DATA_REPORTS_DIR / f"stormlens_report_{base}_{stamp}.pdf"
    out_stats = DATA_REPORTS_DIR / f"stats_{base}_{stamp}.csv"
    out_validation = DATA_REPORTS_DIR / f"validation_summary_{base}_{stamp}.csv"
    out_features = DATA_REPORTS_DIR / f"feature_ranking_{base}_{stamp}.csv"

    # Core CSV summaries
    df.describe(include="all").T.to_csv(out_stats)
    if validation_result is not None:
        validation_result.summary_table.to_csv(out_validation, index=False)
    if feature_result is not None:
        feature_result.ranking.to_csv(out_features, index=False)

    generate_pdf_report(
        out_pdf,
        dataset_name=dataset_name,
        df=df,
        validation_result=validation_result,
        eda_result=eda_result,
        feature_result=feature_result,
    )

    bundle: dict[str, Path] = {"PDF report": out_pdf, "CSV stats": out_stats}
    if validation_result is not None:
        bundle["CSV validation summary"] = out_validation
    if feature_result is not None:
        bundle["CSV feature ranking"] = out_features
    return bundle

