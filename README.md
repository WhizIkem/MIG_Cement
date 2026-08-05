# MIG Cement — Inventory Forecasting & Planning System

A data-driven cement inventory management solution for MIG Cement, covering demand forecasting, KPI analysis, scenario simulation, and an interactive planning dashboard across 30 construction sites.

---

## Project Overview

MIG Cement faces significant operational inefficiencies across its site network:

| Pain Point | Rate |
|---|---|
| Average stockout rate | 24.18% |
| Average overcapacity rate | 34.79% |
| Reactive ordering rate | 50.80% |
| Problem sites identified | 30 / 30 |

This project delivers a full ML pipeline and interactive dashboard to shift from reactive to predictive inventory management.

---

## Key Results

### Model Performance (Gradient Boosting vs. SARIMAX Baseline)

| Metric | SARIMAX Baseline | Gradient Boosting | Improvement |
|---|---|---|---|
| Avg. MAPE |22.97% | 3.14% | **−86.33%** |
| Avg. RMSE | 7.22 tonnes | 1.23 tonnes | **−82.96%** |
| Sites improved (MAPE) | — | 27 / 30 | — |
| Sites improved (RMSE) | — | 26 / 30 | — |

### Business Value
- **Reduced emergency replenishment** costs through proactive reorder alerts
- **Fewer pour disruptions** via improved demand visibility
- **Lower overstock exposure** through dynamic safety stock and scenario planning
- **Centralised dashboard** reducing manual planning overhead across 30 sites

---

## Project Structure

```
MIG_Cement/
├── data/
│   ├── raw/                    # SQLite operational database (MIG_Cement_Records.db)
│   └── processed/              # KPI summary CSV
├── notebooks/
│   ├── 01_sql_pipeline.ipynb           # Data extraction via SQL
│   ├── 02_data_validation_kpi_analysis.ipynb
│   ├── 03_modeling.ipynb               # SARIMAX baseline
│   ├── 04_feature_engineering.ipynb    # Random Forest feature engineering
│   ├── 04_feature_engineering_gb.ipynb # Gradient Boosting features
│   └── 05_scaling.ipynb                # Full-scale 30-site pipeline
├── src/
│   ├── data_loader.py          # SQLite reader
│   ├── pipeline.py             # Random Forest pipeline
│   ├── pipeline_gb.py          # Gradient Boosting pipeline + scenario simulation
│   ├── inventory_simulation.py # Reorder logic and coverage metrics
│   ├── metric.py               # Evaluation metrics (MAPE, RMSE)
│   └── report_builder.py       # Automated report generation
├── dashboard/
│   ├── MIG_dash_app.py         # Dash application layout and callbacks
│   ├── app.py                  # Deployment entrypoint
│   └── utils.py                # Cached data loaders and helpers
├── reports/                    # Architecture docs, model results, business impact
└── artifacts/plots/            # Generated visualisations
```

---

## Models

### SARIMAX (Baseline)
- Per-site time-series model with exogenous variables: `planned_pour_tonnes`, `rain_mm`, `avg_temp_c`
- Best configuration: Order (0,0,2), Seasonal (0,2,2,7)
- Overall MAPE: **22.97%**, RMSE: **7.22 tonnes**

### Random Forest
- Engineered features: lag features (1, 3, 7 days), rolling mean/std, rain × pour interaction, temperature × pour, inventory gap, inventory ratio
- 80/20 train-test split per site

### Gradient Boosting (Primary Model)
- Extended feature engineering on top of Random Forest pipeline
- Scenario-aware simulation: Conservative, Baseline, and Aggressive demand scenarios
- Computes: reorder triggers, coverage days, safety stock, inventory turnover

---

## Dashboard

An interactive Dash application for site-level inventory planning:

- **Site & scenario selector** — filter by any of 30 sites and demand scenario
- **Date range picker** — drill into specific planning windows
- **KPI cards** — real-time stockout rate, overcapacity rate, reactive order rate
- **Inventory chart** — actual levels, forecast demand, reorder trigger points
- **Reorder recommendation table** — delivery actions with rain-buffer adjustments

### Running the Dashboard

```bash
cd dashboard
python app.py
```

---

## Setup

### Requirements

```bash
pip install pandas numpy scikit-learn xgboost statsmodels dash plotly
```

### Data

Place the raw SQLite database at:
```
data/raw/MIG_Cement_Records.db
```

### Run the Pipeline

```bash
# Feature engineering and model training (Gradient Boosting)
python src/pipeline_gb.py

# Generate schema report
python schema_report.py
```

---

## Reports

| Document | Description |
|---|---|
| [ARCHITECTURE.md](reports/ARCHITECTURE.md) | System and dashboard architecture |
| [baseline_model_results.md](reports/baseline_model_results.md) | SARIMAX model diagnostics |
| [Business_Impact_and_ROI.md](reports/Business_Impact_and_ROI.md) | ROI framework and business value |
| [Deployment_and_Maintenance_Guide.md](reports/Deployment_and_Maintenance_Guide.md) | Production deployment steps |
| [User_Guide_and_Training.md](reports/User_Guide_and_Training.md) | End-user documentation |
| [Project_Handover.md](reports/Project_Handover.md) | Handover and ownership notes |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data storage | SQLite |
| Data processing | Python, Pandas, NumPy |
| Modelling | Scikit-learn, XGBoost, Statsmodels (SARIMAX) |
| Dashboard | Plotly Dash |
| Notebooks | Jupyter |
