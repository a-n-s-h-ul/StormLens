# StormLens Deployment

StormLens can be hosted publicly as a Streamlit app. The easiest path is Streamlit Community Cloud.

## Option 1: Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Go to https://share.streamlit.io.
3. Click **New app**.
4. Choose your GitHub repository.
5. Set the main file path to:
   ```text
   main.py
   ```
6. Add secrets in the Streamlit Cloud app settings:
   ```toml
   CDSAPI_URL = "https://cds.climate.copernicus.eu/api"
   CDSAPI_KEY = "your-cds-api-key"
   ```
7. Deploy.

After deployment, Streamlit gives you a public URL that works from anywhere.

## Option 2: Render

1. Push this project to GitHub.
2. Create a new **Web Service** on Render.
3. Select the GitHub repository.
4. Use Docker deployment. Render will detect the included `Dockerfile`.
5. Add environment variables:
   ```text
   CDSAPI_URL=https://cds.climate.copernicus.eu/api
   CDSAPI_KEY=your-cds-api-key
   ```
6. Deploy.

## Important Notes

- Do not commit real CDS API keys.
- ERA5 fetch requests can be slow on free hosting tiers.
- Free hosting storage is often temporary, so generated datasets/reports may disappear after app restarts.
- For serious research usage, use a paid service with persistent storage.

