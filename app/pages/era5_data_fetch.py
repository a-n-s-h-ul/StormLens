from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import streamlit as st

from app.era5_fetcher import ERA5Request, fetch_era5, list_raw_csv_files, SUPPORTED_SINGLE_LEVEL_VARS
from app.state import set_dataset
from app.ui import card, hero, next_step_button
from utils.config import DATA_RAW_DIR
from utils.io import load_csv_cached


def _progress_adapter(bar):
    def cb(p: float, msg: str) -> None:
        bar.progress(max(0.0, min(1.0, p)), text=msg)

    return cb


def _cds_config_path() -> Path:
    return Path.home() / ".cdsapirc"


def _read_cds_config() -> tuple[str, str]:
    secrets_url = ""
    secrets_key = ""
    try:
        secrets_url = st.secrets.get("CDSAPI_URL", "") or st.secrets.get("cds", {}).get("url", "")
        secrets_key = st.secrets.get("CDSAPI_KEY", "") or st.secrets.get("cds", {}).get("key", "")
    except Exception:
        secrets_url = ""
        secrets_key = ""

    env_url = os.getenv("CDSAPI_URL", "")
    env_key = os.getenv("CDSAPI_KEY", "")
    hosted_url = secrets_url or env_url
    hosted_key = secrets_key or env_key
    if hosted_key:
        return hosted_url or "https://cds.climate.copernicus.eu/api", hosted_key

    path = _cds_config_path()
    if not path.exists():
        return "https://cds.climate.copernicus.eu/api", ""

    url = "https://cds.climate.copernicus.eu/api"
    key = ""
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        if k.strip() == "url":
            url = v.strip()
        elif k.strip() == "key":
            key = v.strip()
    return url, key


def _write_cds_config(url: str, key: str) -> Path:
    path = _cds_config_path()
    content = f"url: {url.strip()}\nkey: {key.strip()}\n"
    path.write_text(content, encoding="utf-8")
    return path


def _test_cds_auth(url: str, key: str) -> tuple[bool, str]:
    try:
        import cdsapi

        client = cdsapi.Client(url=url.strip(), key=key.strip(), quiet=True, verify=True)
        target = DATA_RAW_DIR / "_cds_auth_test.nc"
        client.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": ["2m_temperature"],
                "year": "2023",
                "month": "06",
                "day": "01",
                "time": ["00:00"],
                "area": [22.7, 88.2, 22.4, 88.5],
                "format": "netcdf",
            },
            str(target),
        )
        if target.exists():
            target.unlink(missing_ok=True)
        return True, "CDS authentication and retrieval test passed."
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def render() -> None:
    hero(
        "ERA5 Data Fetch",
        "Automated ingestion via Copernicus Climate Data Store (CDS) using cdsapi.",
        "Outputs: NetCDF + CSV + JSON manifest into data/raw/",
    )

    with st.expander("CDS Credentials", expanded=True):
        card(
            "Credentials inside interface",
            "Manage your CDS URL and API key directly here. StormLens can save them to your local ~/.cdsapirc so fetch works without terminal setup.",
        )

        default_url, default_key = _read_cds_config()
        c1, c2 = st.columns([2, 3], gap="large")
        with c1:
            cds_url = st.text_input(
                "CDS URL",
                value=default_url,
                help="Usually: https://cds.climate.copernicus.eu/api",
            )
        with c2:
            show_key = st.checkbox("Show API key", value=False)
            cds_key = st.text_input(
                "CDS API key",
                value=default_key,
                type="default" if show_key else "password",
                help="Expected format is usually UID:APIKEY (some accounts may provide a token-style key).",
            )

        c3, c4 = st.columns(2)
        with c3:
            if st.button("Save credentials", use_container_width=True):
                if not cds_url.strip() or not cds_key.strip():
                    st.error("Both CDS URL and API key are required.")
                else:
                    path = _write_cds_config(cds_url, cds_key)
                    st.success(f"Saved credentials to `{path}`")
        with c4:
            if st.button("Test CDS connection", use_container_width=True):
                with st.spinner("Testing CDS authentication..."):
                    ok, msg = _test_cds_auth(cds_url, cds_key)
                if ok:
                    st.success(msg)
                else:
                    st.error(f"CDS test failed: {msg}")

    with st.expander("Request parameters", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            lat = st.number_input("Latitude", value=22.57, min_value=-90.0, max_value=90.0, format="%.4f")
            lon = st.number_input("Longitude", value=88.36, min_value=-180.0, max_value=180.0, format="%.4f")
        with c2:
            start = st.date_input("Start date", value=dt.date(2023, 6, 1))
            end = st.date_input("End date", value=dt.date(2023, 6, 3))
        with c3:
            area_pad = st.slider("Area pad (degrees)", min_value=0.0, max_value=2.0, value=0.25, step=0.05)
            st.caption("ERA5 returns gridded fields; StormLens requests a small box around the point and averages it.")

        variables = st.multiselect(
            "Variables",
            options=list(SUPPORTED_SINGLE_LEVEL_VARS.keys()),
            default=["CAPE", "CIN", "temperature", "humidity", "u wind", "v wind", "pressure", "precipitation"],
        )
        pressure_levels = st.multiselect(
            "Pressure levels (hPa) (optional)",
            options=[1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100],
            default=[850, 700, 500],
        )

    out_dir = DATA_RAW_DIR
    st.caption(f"Outputs save to: `{out_dir}`")

    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        if st.button("Fetch ERA5 dataset", type="primary", use_container_width=True):
            bar = st.progress(0.0, text="Initializing...")
            try:
                if cds_url.strip() and cds_key.strip():
                    _write_cds_config(cds_url, cds_key)
                with st.spinner("Downloading and processing ERA5..."):
                    req = ERA5Request(
                        latitude=float(lat),
                        longitude=float(lon),
                        start_date=start,
                        end_date=end,
                        variables=list(variables),
                        pressure_levels=[int(p) for p in pressure_levels],
                        area_pad_deg=float(area_pad),
                    )
                    result = fetch_era5(req, out_dir=out_dir, progress_cb=_progress_adapter(bar))

                csv_paths = result["csv_paths"]
                if csv_paths:
                    primary_csv: Path = csv_paths[0]
                    df = load_csv_cached(primary_csv)
                    set_dataset(df, name=primary_csv.name, path=primary_csv)
                    st.session_state["era5_fetch_msg"] = f"Successfully fetched and loaded: `{primary_csv.name}`"
                    st.session_state["era5_manifest"] = result["manifest"]
                    st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"ERA5 fetch failed: {exc}")
            finally:
                bar.empty()

    with col_b:
        st.subheader("Load existing raw CSV")
        raw_csvs = list_raw_csv_files()
        if raw_csvs:
            pick = st.selectbox(
                "Available data/raw/*.csv",
                options=raw_csvs,
                format_func=lambda p: p.name,
                key="era5_raw_csv_select"
            )
            if st.button("Load selected dataset", use_container_width=True):
                df = load_csv_cached(pick)
                set_dataset(df, name=pick.name, path=pick)
                st.session_state["era5_fetch_msg"] = f"Loaded dataset: `{pick.name}`"
                if "era5_manifest" in st.session_state:
                    del st.session_state["era5_manifest"]
                st.rerun()
        else:
            st.caption("No raw CSV files found yet.")

    ds = get_dataset()
    if ds is not None:
        st.divider()
        msg = st.session_state.get("era5_fetch_msg", f"Active dataset: **{ds.name}**")
        st.success(msg)
        
        manifest = st.session_state.get("era5_manifest")
        if manifest:
            with st.expander("Artifacts manifest", expanded=False):
                st.json(manifest, expanded=False)

        next_step_button(
            "Dataset Catalog",
            "Continue to dataset catalog",
            "next_catalog_after_era5_load_success",
        )
        with st.expander("Preview active dataset", expanded=False):
            st.dataframe(ds.df.head(200), use_container_width=True)
