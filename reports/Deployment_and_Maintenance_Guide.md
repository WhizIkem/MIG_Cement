# Deployment and Maintenance Guide

## Deployment Overview

The dashboard is a Dash application backed by processed artifacts and Python utilities.

Primary entrypoints:
- dashboard/MIG_dash_app.py
- dashboard/app.py

Primary data dependencies:
- data/processed/MIG_kpi_summary.csv
- data/processed/cement_forecast_results.parquet
- data/raw/MIG_Cement_Records.db

## Recommended Deployment Steps

1. Prepare Python environment
- install required Python packages used by the dashboard and pipeline
- verify Dash, Plotly, Pandas, scikit-learn, and dash-bootstrap-components are available

2. Validate artifacts
- confirm MIG_kpi_summary.csv exists in data/processed
- confirm cement_forecast_results.parquet exists in data/processed
- confirm raw SQLite database exists if regeneration is required

3. Start the application
- from the dashboard directory run:
  - python3 MIG_dash_app.py
or
  - python3 app.py

4. Access the dashboard
- default host: 0.0.0.0
- default port: 8050

## Artifact Refresh Process

To regenerate the main planning artifact:

1. Load raw SQLite data through src/data_loader.py
2. Run src/pipeline_gb.py with the desired horizon and scenario configuration
3. Write updated results to data/processed/cement_forecast_results.parquet
4. Restart the Dash app so the server reloads current artifacts

The documentation package assumes a Random Forest baseline and a fine-tuned Gradient Boosting planning model.

## Maintenance Requirements

### Daily / Per Refresh Cycle
- confirm processed data files are current
- confirm dashboard starts without callback errors
- inspect scenario output counts and date ranges

### Weekly
- review alert volume and threshold usefulness
- spot-check reorder logic against planner expectations
- review any runtime errors or dependency issues

### Monthly
- compare model output versus actual consumption outcomes
- review forecast drift by site
- confirm scenario behavior still reflects operational reality

### Quarterly
- retrain model candidates with latest data
- compare new model performance against current deployed version
- update dashboard metrics or business rules if needed

## Operational Risks

- stale parquet artifacts can make the dashboard appear out of date
- dependency mismatches can break imports or callbacks
- callback layout changes require validation before deployment
- scenario additions must be mirrored in both pipeline and dashboard filter logic

## Support Guidance

If the dashboard fails to start:
- verify Python dependencies
- verify artifact paths
- run a compile check on dashboard Python files
- verify the processed parquet contains required columns

If the dashboard shows outdated results:
- regenerate processed outputs
- restart the Dash app
- refresh the browser session
