from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


@dataclass
class DatasetState:
    name: str
    path: Optional[Path]
    df: pd.DataFrame


def has_dataset() -> bool:
    return "dataset_df" in st.session_state and isinstance(
        st.session_state["dataset_df"], pd.DataFrame
    )


def set_dataset(df: pd.DataFrame, name: str, path: Optional[Path] = None) -> None:
    st.session_state["dataset_df"] = df
    st.session_state["dataset_name"] = name
    st.session_state["dataset_path"] = str(path) if path else None


def get_dataset() -> Optional[DatasetState]:
    if not has_dataset():
        return None
    path_str = st.session_state.get("dataset_path")
    return DatasetState(
        name=st.session_state.get("dataset_name", "Unnamed dataset"),
        path=Path(path_str) if path_str else None,
        df=st.session_state["dataset_df"],
    )

