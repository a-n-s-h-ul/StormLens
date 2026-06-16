from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd
import xarray as xr

from utils.config import DATA_RAW_DIR, ensure_project_dirs
from utils.logger import get_logger


logger = get_logger(__name__)


SUPPORTED_SINGLE_LEVEL_VARS = {
    "CAPE": "convective_available_potential_energy",
    "CIN": "convective_inhibition",
    "temperature": "2m_temperature",
    # NOTE: CDS does NOT support requesting "2m_relative_humidity" directly.
    # Relative humidity is derived from 2m temperature + 2m dewpoint temperature.
    "humidity": "2m_relative_humidity",
    "u wind": "10m_u_component_of_wind",
    "v wind": "10m_v_component_of_wind",
    "pressure": "surface_pressure",
    "precipitation": "total_precipitation",
}


SUPPORTED_PRESSURE_LEVEL_VARS = {
    "temperature": "temperature",
    "humidity": "relative_humidity",
    "u wind": "u_component_of_wind",
    "v wind": "v_component_of_wind",
}


@dataclass(frozen=True)
class ERA5Request:
    latitude: float
    longitude: float
    start_date: dt.date
    end_date: dt.date
    variables: list[str]
    pressure_levels: list[int]
    time_step: str = "01:00"
    area_pad_deg: float = 0.25


def _date_range_days(start: dt.date, end: dt.date) -> list[dt.date]:
    if end < start:
        raise ValueError("end_date must be >= start_date")
    days = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += dt.timedelta(days=1)
    return days


def _era5_area_bbox(lat: float, lon: float, pad: float) -> list[float]:
    north = min(90.0, lat + pad)
    south = max(-90.0, lat - pad)
    west = max(-180.0, lon - pad)
    east = min(180.0, lon + pad)
    return [north, west, south, east]


def _times_hourly() -> list[str]:
    return [f"{h:02d}:00" for h in range(0, 24)]


def _safe_slug(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in text).strip("_")


def netcdf_to_dataframe(netcdf_path: Path, aggregate_area: bool = True) -> pd.DataFrame:
    ds = xr.open_dataset(netcdf_path, engine="netcdf4")
    try:
        if aggregate_area:
            for dim in ["latitude", "longitude"]:
                if dim in ds.dims:
                    ds = ds.mean(dim=dim, skipna=True)
        df = ds.to_dataframe().reset_index()
    finally:
        ds.close()

    df = df.replace([np.inf, -np.inf], np.nan)
    return df


def fetch_era5(
    req: ERA5Request,
    out_dir: Optional[Path] = None,
    progress_cb=None,
) -> dict:
    """
    Fetch ERA5 NetCDF files using cdsapi.

    Returns a dict with paths and a minimal manifest.
    """
    ensure_project_dirs()
    out_dir = out_dir or DATA_RAW_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        import cdsapi  # local import so app can run without cds setup
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "cdsapi is not available. Install dependencies and configure CDS API (~/.cdsapirc)."
        ) from exc

    days = _date_range_days(req.start_date, req.end_date)

    area = _era5_area_bbox(req.latitude, req.longitude, req.area_pad_deg)
    times = _times_hourly()

    # Translate UI-level variable selections into CDS-native variables.
    # NOTE: "humidity" is derived (not natively available as 2m relative humidity).
    requested_single: list[str] = []
    requested_pressure: list[str] = []

    need_2m_rh = any(v == "humidity" for v in req.variables)

    for v in req.variables:
        if v == "humidity":
            # Fetch native prerequisites instead of requesting RH directly.
            requested_single.extend(["2m_temperature", "2m_dewpoint_temperature"])
            continue
        if v in SUPPORTED_SINGLE_LEVEL_VARS:
            requested_single.append(SUPPORTED_SINGLE_LEVEL_VARS[v])
        if v in SUPPORTED_PRESSURE_LEVEL_VARS:
            requested_pressure.append(SUPPORTED_PRESSURE_LEVEL_VARS[v])

    # De-duplicate while preserving order
    def _dedupe(seq: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    requested_single = _dedupe(requested_single)
    requested_pressure = _dedupe(requested_pressure)


    if not requested_single and not requested_pressure:
        raise ValueError("No supported variables selected.")

    client = cdsapi.Client()
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    slug_vars = _safe_slug("-".join(req.variables))

    manifest = {
        "request": {
            "latitude": req.latitude,
            "longitude": req.longitude,
            "start_date": req.start_date.isoformat(),
            "end_date": req.end_date.isoformat(),
            "variables": req.variables,
            "pressure_levels": req.pressure_levels,
            "area_bbox": area,
            "times": times,
        },
        "artifacts": [],
    }

    def _tick(p: float, msg: str) -> None:
        if callable(progress_cb):
            progress_cb(p, msg)

    _tick(0.05, "Preparing ERA5 request …")

    outputs = []

    # NOTE: CDS API will error if you pass "day" values that don't exist for a given month.
    # To avoid invalid (month, day) combinations, we request data per-day and concatenate later.
    def _retrieve_daily(dataset: str, payload_base: dict, kind: str) -> list[Path]:
        paths: list[Path] = []
        for i, d in enumerate(days):
            frac = i / max(1, len(days))
            _tick(0.15 + 0.55 * frac, f"Downloading {kind}: {d.isoformat()} …")
            out_nc = out_dir / f"era5_{kind}_{stamp}_{d.isoformat()}_{slug_vars}.nc"
            payload = dict(payload_base)
            payload.update(
                {
                    "year": f"{d.year}",
                    "month": f"{d.month:02d}",
                    "day": f"{d.day:02d}",
                }
            )
            client.retrieve(dataset, payload, str(out_nc))
            paths.append(out_nc)
            manifest["artifacts"].append({"type": "netcdf", "kind": kind, "path": str(out_nc)})
        return paths

    if requested_single:
        single_paths = _retrieve_daily(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": requested_single,
                "time": times,
                "area": area,
                "data_format": "netcdf",
            },
            kind="single",
        )
        outputs.extend(single_paths)

    if requested_pressure and req.pressure_levels:
        pressure_paths = _retrieve_daily(
            "reanalysis-era5-pressure-levels",
            {
                "product_type": "reanalysis",
                "variable": requested_pressure,
                "pressure_level": [str(p) for p in req.pressure_levels],
                "time": times,
                "area": area,
                "data_format": "netcdf",
            },
            kind="pressure",
        )
        outputs.extend(pressure_paths)

    _tick(0.80, "Converting NetCDF → DataFrame/CSV …")

    def _compute_2m_relative_humidity(df_in: pd.DataFrame) -> pd.DataFrame:
        """Derive 2m relative humidity from 2m temperature and 2m dewpoint temperature.

        Expects columns:
          - "2m_temperature"
          - "2m_dewpoint_temperature"

        Adds column "2m_relative_humidity".
        """
        if "2m_relative_humidity" in df_in.columns:
            return df_in
        if "2m_temperature" not in df_in.columns or "2m_dewpoint_temperature" not in df_in.columns:
            return df_in

        T = df_in["2m_temperature"].astype(float)
        Td = df_in["2m_dewpoint_temperature"].astype(float)

        # Magnus formula (in Kelvin -> convert to Celsius internally)
        T_c = T - 273.15
        Td_c = Td - 273.15
        a = 17.625
        b = 243.04

        # RH = 100 * exp( a*Td/(b+Td) ) / exp( a*T/(b+T) )
        rh = 100.0 * np.exp((a * Td_c) / (b + Td_c)) / np.exp((a * T_c) / (b + T_c))
        df_out = df_in.copy()
        df_out["2m_relative_humidity"] = rh
        df_out = df_out.replace([np.inf, -np.inf], np.nan)
        return df_out

    csv_paths = []
    need_derivation = any(v == "humidity" for v in req.variables)

    for nc in outputs:
        df = netcdf_to_dataframe(nc, aggregate_area=True)

        if need_derivation:
            df = _compute_2m_relative_humidity(df)

        csv_path = nc.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        csv_paths.append(csv_path)
        manifest["artifacts"].append({"type": "csv", "path": str(csv_path)})


    manifest_path = out_dir / f"era5_manifest_{stamp}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    _tick(1.0, "Done.")
    logger.info("ERA5 fetch completed: %s", manifest_path)

    return {
        "netcdf_paths": outputs,
        "csv_paths": csv_paths,
        "manifest_path": manifest_path,
        "manifest": manifest,
    }


def list_raw_csv_files(raw_dir: Optional[Path] = None) -> list[Path]:
    raw_dir = raw_dir or DATA_RAW_DIR
    if not raw_dir.exists():
        return []
    return sorted(raw_dir.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
