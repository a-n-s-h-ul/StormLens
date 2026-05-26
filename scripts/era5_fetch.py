from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from app.era5_fetcher import ERA5Request, fetch_era5, SUPPORTED_SINGLE_LEVEL_VARS


def _parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def main() -> None:
    p = argparse.ArgumentParser(description="StormLens ERA5 fetch (Phase-1)")
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--start", type=_parse_date, required=True, help="YYYY-MM-DD")
    p.add_argument("--end", type=_parse_date, required=True, help="YYYY-MM-DD")
    p.add_argument("--out", type=Path, default=Path("data/raw"))
    p.add_argument(
        "--vars",
        nargs="+",
        default=["CAPE", "CIN", "temperature", "humidity", "u wind", "v wind", "pressure", "precipitation"],
        choices=list(SUPPORTED_SINGLE_LEVEL_VARS.keys()),
    )
    p.add_argument("--pressure-levels", nargs="*", type=int, default=[850, 700, 500])
    p.add_argument("--area-pad", type=float, default=0.25)

    args = p.parse_args()
    req = ERA5Request(
        latitude=args.lat,
        longitude=args.lon,
        start_date=args.start,
        end_date=args.end,
        variables=list(args.vars),
        pressure_levels=list(args.pressure_levels),
        area_pad_deg=float(args.area_pad),
    )
    result = fetch_era5(req, out_dir=args.out)
    print("Manifest:", result["manifest_path"])
    for pth in result["csv_paths"]:
        print("CSV:", pth)


if __name__ == "__main__":
    main()

