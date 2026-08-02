from functools import lru_cache
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_loader import load_cement_data
from src.pipeline_gb import (
    build_site_metadata_from_data,
    get_default_what_if_scenarios,
    run_pipeline,
)


@lru_cache(maxsize=1)
def _load_kpi_summary_cached(csv_path):
    df = pd.read_csv(csv_path)
    if 'stockout_pct' not in df.columns and 'end_of_day_stockout_pct' in df.columns:
        df['stockout_pct'] = df['end_of_day_stockout_pct'].astype(float)
    if 'overcapacity_pct' in df.columns:
        df['overcapacity_pct'] = df['overcapacity_pct'].astype(float)
    return df


def load_kpi_summary(csv_path='../data/processed/MIG_kpi_summary.csv'):
    return _load_kpi_summary_cached(csv_path).copy()


@lru_cache(maxsize=4)
def _load_results_cached(parquet_path):
    df = pd.read_parquet(parquet_path)
    df['date'] = pd.to_datetime(df['date'])
    if 'scenario' not in df.columns:
        df['scenario'] = 'baseline'
    if 'scenario_demand_multiplier' not in df.columns:
        df['scenario_demand_multiplier'] = 1.0
    if 'scenario_lead_time_days' not in df.columns:
        df['scenario_lead_time_days'] = 2
    return df


def load_results_df(parquet_path='../data/processed/cement_forecast_results.parquet'):
    return _load_results_cached(parquet_path).copy()


@lru_cache(maxsize=8)
def generate_forecasts_on_demand(
    db_path='../data/raw/MIG_Cement_Records.db',
    simulation_horizon_days=56,
    include_scenarios=False,
    base_lead_time_days=2,
    delayed_extra_days=2,
):
    df = load_cement_data(db_path=db_path)
    site_metadata = build_site_metadata_from_data(df)

    scenario_configs = None
    if include_scenarios:
        scenario_configs = get_default_what_if_scenarios(
            base_lead_time_days=base_lead_time_days,
            delayed_extra_days=delayed_extra_days,
        )

    return run_pipeline(
        df,
        site_metadata=site_metadata,
        simulation_horizon_days=simulation_horizon_days,
        lead_time_days=base_lead_time_days,
        scenario_configs=scenario_configs,
    )


def format_scenario_label(scenario_name):
    return str(scenario_name).replace('_', ' ').title()


def get_date_bounds(results_df):
    return results_df['date'].min(), results_df['date'].max()


def filter_results(results_df, site_id, scenario, start_date=None, end_date=None):
    filtered = results_df[
        (results_df['site_id'] == site_id) & (results_df['scenario'] == scenario)
    ].copy()

    if start_date is not None:
        filtered = filtered[filtered['date'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        filtered = filtered[filtered['date'] <= pd.to_datetime(end_date)]

    return filtered.sort_values('date')