from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.config import DATA_PROCESSED_DIR, DATA_RAW_DIR, DATA_REPORTS_DIR, DATA_VALIDATED_DIR


def scan_data_catalog() -> pd.DataFrame:
    buckets = {
        "raw": DATA_RAW_DIR,
        "processed": DATA_PROCESSED_DIR,
        "validated": DATA_VALIDATED_DIR,
        "reports": DATA_REPORTS_DIR,
    }
    rows = []
    for bucket, directory in buckets.items():
        directory.mkdir(parents=True, exist_ok=True)
        for path in sorted(directory.glob("*")):
            if path.name == ".gitkeep" or not path.is_file():
                continue
            stat = path.stat()
            rows.append(
                {
                    "bucket": bucket,
                    "file_name": path.name,
                    "extension": path.suffix.lower() or "(none)",
                    "size_mb": round(stat.st_size / (1024 * 1024), 4),
                    "modified": pd.Timestamp(stat.st_mtime, unit="s"),
                    "path": str(path),
                }
            )
    return pd.DataFrame(rows)


def catalog_summary(catalog: pd.DataFrame) -> pd.DataFrame:
    if catalog.empty:
        return pd.DataFrame(columns=["bucket", "files", "total_size_mb"])
    return (
        catalog.groupby("bucket", as_index=False)
        .agg(files=("file_name", "count"), total_size_mb=("size_mb", "sum"))
        .sort_values("bucket")
    )
