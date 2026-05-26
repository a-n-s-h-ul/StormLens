# ⛈️ StormLens: Meteorological Intelligence Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MLOps](https://img.shields.io/badge/MLOps-Ready-green.svg)](https://en.wikipedia.org/wiki/MLOps)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**StormLens** is an end-to-end data engineering and intelligence framework designed for high-resolution atmospheric research and thunderstorm prediction. It automates the lifecycle of meteorological data from ERA5 reanalysis ingestion to interpretable feature intelligence.

---

## 🚀 Key Features

### 1. Ingestion & Data Lake
- **Automated ERA5 Pipeline:** Direct connectivity to the Copernicus CDS API with background polling and NetCDF-to-CSV conversion.
- **Structured Storage:** Automated cataloging of raw, validated, and processed datasets.

### 2. Scientific Validation
- **Quality Engine:** Automated meteorological range checks (e.g., CAPE > 0, Temp > -100C) and timestamp continuity verification.
- **Integrity Scoring:** Real-time data quality metrics and anomaly logging.

### 3. Advanced Intelligence
- **Automated EDA:** Interactive dashboards for distribution analysis, temporal trends, and correlation heatmaps.
- **Dimensionality Reduction:** 3D atmospheric state projections using PCA (with Biplots) and t-SNE.
- **Feature Scoring:** Statistical ranking of thunderstorm precursors using Mutual Information and Pearson scores.

### 4. MLOps & Reporting
- **Model Readiness:** Automated assessment of dataset suitability for interpretable ML models (EBM, GAM).
- **Research Export:** On-demand generation of comprehensive research summaries and data catalogs.

---

## 🛠️ Architecture

```mermaid
graph TD
    subgraph "Data Acquisition"
        A[ERA5 API] --> B[Ingest Engine]
        C[Local CSV] --> B
    end
    
    subgraph "Quality Layer"
        B --> D[Physical Range Validation]
        D --> E[Temporal Continuity Check]
        E --> F[(Validated Data Lake)]
    end
    
    subgraph "Intelligence Layer"
        F --> G[Interactive EDA]
        F --> H[PCA/t-SNE Projection]
        F --> I[Feature Scoring]
    end
    
    subgraph "Output"
        I --> J[Model-Ready Artifacts]
        G --> K[PDF Research Reports]
    end
```

---

## 💻 Tech Stack
- **Languages:** Python 3.9+
- **Frontend:** Streamlit (Custom CSS/JS)
- **Data:** Pandas, Xarray, Numpy, scikit-learn
- **Visualization:** Plotly (Interactive 3D/2D)
- **Deployment:** Docker, Streamlit Cloud

---

## 📝 CV / Portfolio Impact

If you are showcasing this project, emphasize these engineering highlights:
- **"Designed a modular meteorological data pipeline... "**
- **"Implemented a physical rule-based validation engine... "**
- **"Developed interactive 3D atmospheric projections... "**
- **"Built a research-ready reporting system... "**

---

## 🏁 Getting Started

1. **Clone the repo:** `git clone https://github.com/your-username/StormLens.git`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Set API Secrets:** Add your CDS API credentials to `.streamlit/secrets.toml`
4. **Run the App:** `streamlit run main.py`

---

*StormLens: Turning raw data into atmospheric insight.*
