from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.config import ensure_project_dirs


def _sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()  # noqa: S324 (non-crypto usage: caching key)


@st.cache_data(show_spinner=False)
def load_csv_cached(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def save_uploaded_file(uploaded_file, out_dir: Path) -> Path:
    ensure_project_dirs()
    out_dir.mkdir(parents=True, exist_ok=True)
    data = uploaded_file.getvalue()
    digest = _sha1_bytes(data)[:10]
    safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in uploaded_file.name)
    path = out_dir / f"{Path(safe_name).stem}_{digest}{Path(safe_name).suffix}"
    path.write_bytes(data)
    return path


def save_dataframe_csv(df: pd.DataFrame, path: Path) -> None:
    ensure_project_dirs()
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

