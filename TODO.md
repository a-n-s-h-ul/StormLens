# TODO - StormLens ERA5 fixes

- [x] Update `app/era5_fetcher.py`: replace deprecated CDS request key `format` with `data_format`.
- [x] Update `app/era5_fetcher.py`: stop requesting ambiguous `2m_relative_humidity` from CDS.
- [x] Update `app/era5_fetcher.py`: when `humidity` is selected, request `2m_temperature` + `2m_dewpoint_temperature` and derive `2m_relative_humidity` locally.

- [x] Smoke test via `python -m scripts.era5_fetch --vars humidity` for a small date range (2020-01-01) completed successfully.


