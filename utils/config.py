from __future__ import annotations

from pathlib import Path


APP_NAME = "StormLens"
PROJECT_TAGLINE = "ERA5 meteorological data intelligence platform for thunderstorm prediction"

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_VALIDATED_DIR = DATA_DIR / "validated"
DATA_REPORTS_DIR = DATA_DIR / "reports"

PHASES = {
    "Phase-1": "Data Intelligence: Ingestion, Validation, and Feature Scoring",
    "Phase-2": "Whitebox Modeling: Interpretable ML for Scientific Trust",
    "Phase-3": "Operational MLOps: Cloud Deployment and Real-time Inference",
}


def ensure_project_dirs() -> None:
    for p in [
        DATA_RAW_DIR,
        DATA_PROCESSED_DIR,
        DATA_VALIDATED_DIR,
        DATA_REPORTS_DIR,
        ROOT_DIR / "assets",
    ]:
        p.mkdir(parents=True, exist_ok=True)

