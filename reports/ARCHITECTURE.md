# Dashboard Architecture

## Overview

The dashboard is a Dash application for scenario-based cement inventory planning. It presents precomputed or on-demand forecast outputs, inventory simulation results, and reorder recommendations at site level.

## Components

### Entry Points

- `MIG_dash_app.py`: Primary Dash application definition, layout, and callbacks.
- `app.py`: Thin entrypoint shim for deployment or alternate launch conventions.

### Data Utilities

- `utils.py`: Cached loaders and helper functions for:
  - KPI summary loading
  - forecast result loading
  - on-demand forecast generation from SQLite via the modeling pipeline
  - scenario label formatting
  - site/scenario/date filtering

### Data Sources

- `../data/processed/MIG_kpi_summary.csv`: Site-level KPI summary artifact.
- `../data/processed/cement_forecast_results.parquet`: Scenario-aware inventory simulation artifact consumed by Dash.
- `../data/raw/MIG_Cement_Records.db`: SQLite source used for raw operational history and optional on-demand regeneration.

### Modeling Pipeline Dependencies

- `src/data_loader.py`: Reads raw operational data from SQLite.
- `src/pipeline_gb.py`: Builds forecasts, scenario simulations, reorder logic, turnover, coverage days, and safety stock metrics.

## Layout Responsibilities

- Header: product title and lightweight navigation.
- Control row: site selector, scenario selector, and date range picker.
- KPI cards: high-level summary for the filtered site/scenario/date window.
- Main chart: inventory levels, forecast demand, and reorder triggers.
- Recommendation table: delivery actions and rain-buffer information.

## Callback Responsibilities

- Main callback filters result data by site, scenario, and date range.
- It recomputes summary KPIs from the filtered slice.
- It updates the chart and reorder recommendation table.
- It returns an empty-state figure if the selected filter combination has no data.

## Caching Strategy

- `functools.lru_cache` is used in `utils.py` for loading KPI and result artifacts.
- On-demand forecast generation is also cached by parameter set to reduce repeated pipeline runs.
- Public utility functions return copies so the app can safely transform filtered data without mutating cached frames.

## Safe Extension Points

- Add more scenario controls by extending `src/pipeline_gb.py` and wiring new labels in `utils.py`.
- Add more KPIs by enriching the pipeline output and surfacing those fields in the callback.
- Replace processed parquet loading with on-demand regeneration if interactive recomputation is later required.
