import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

def engineer_features(df, site_id):
  site_df = df[df['site_id'] == site_id].copy().sort_values(by='date')
  site_df.set_index('date', inplace=True)
  site_df = site_df.sort_index()

  # create lag features for lag 1, 3, 7
  site_df['lag_1'] = site_df['consumed_tonnes'].shift(1)
  site_df['lag_3'] = site_df['consumed_tonnes'].shift(3)
  site_df['lag_7'] = site_df['consumed_tonnes'].shift(7)

  # rolling mean and standard deviation features
  site_df['rolling_mean_3'] = site_df.groupby('site_id')['consumed_tonnes'].rolling(3).mean().reset_index(level=0, drop=True)
  site_df['rolling_std_7'] = site_df.groupby('site_id')['consumed_tonnes'].rolling(7).std().reset_index(level=0, drop=True)

  # check rain and temperature on planned pour days
  site_df['rain_x_pour'] = site_df['rain_mm'] * site_df['planned_pour_tonnes']
  site_df['temp_x_pour'] = site_df['avg_temp_c'] * site_df['planned_pour_tonnes']

  # inventory features
  site_df['inventory_gap'] = site_df['opening_inventory_tonnes'] + site_df['deliveries_tonnes'] - site_df['planned_pour_tonnes']

  # calculate opening inventory ratio

  site_df['inventory_ratio'] = np.where(
    site_df['silo_capacity'] > 0,
    site_df['opening_inventory_tonnes'] / site_df['silo_capacity'],
    np.nan
  )

  site_df.dropna(inplace=True)
  return site_df


def train_gb_forecast(site_df):
  features = ['planned_pour_tonnes', 'rain_mm', 'avg_temp_c',
       'lag_1', 'lag_3', 'lag_7', 'rolling_mean_3', 'rolling_std_7', 
       'rain_x_pour', 'temp_x_pour', 'inventory_gap',
       'inventory_ratio'
]

  X = site_df[features]
  y = site_df['consumed_tonnes']

  split_index = int(len(site_df) * 0.8)
  X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
  y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

  gb = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=10, 
    random_state=42
    )
  gb.fit(X_train, y_train)

  forecast=gb.predict(X_test)

  test_results = site_df.iloc[split_index:].copy()
  test_results['forecasted_consumption'] = forecast

  return gb, test_results


def build_forecast_horizon(site_df, model, horizon_days=56):
  """
  Build a forward demand forecast horizon using recursive predictions.
  Exogenous drivers are projected from recent weekday profiles.
  """
  if horizon_days <= 0:
    return pd.DataFrame(columns=['consumed_tonnes', 'forecasted_consumption', 'rain_mm'])

  history = site_df.copy().sort_index()
  if history.empty:
    return pd.DataFrame(columns=['consumed_tonnes', 'forecasted_consumption', 'rain_mm'])

  profile_cols = [
    'planned_pour_tonnes',
    'rain_mm',
    'avg_temp_c',
    'opening_inventory_tonnes',
    'deliveries_tonnes',
    'silo_capacity',
  ]

  recent_window = min(56, len(history))
  recent = history.tail(recent_window).copy()
  recent['dow'] = recent.index.dayofweek
  weekday_profile = recent.groupby('dow')[profile_cols].mean()
  fallback_profile = recent[profile_cols].mean()

  feature_cols = [
    'planned_pour_tonnes',
    'rain_mm',
    'avg_temp_c',
    'lag_1',
    'lag_3',
    'lag_7',
    'rolling_mean_3',
    'rolling_std_7',
    'rain_x_pour',
    'temp_x_pour',
    'inventory_gap',
    'inventory_ratio',
  ]

  future_rows = []
  last_date = history.index.max()

  for step in range(1, horizon_days + 1):
    forecast_date = last_date + pd.Timedelta(days=step)
    dow = forecast_date.dayofweek

    if dow in weekday_profile.index:
      profile = weekday_profile.loc[dow]
    else:
      profile = fallback_profile

    planned_pour = float(profile['planned_pour_tonnes'])
    rain_mm = float(profile['rain_mm'])
    avg_temp_c = float(profile['avg_temp_c'])
    opening_inventory = float(profile['opening_inventory_tonnes'])
    deliveries = float(profile['deliveries_tonnes'])
    silo_capacity = float(profile['silo_capacity'])

    lag_1 = float(history['consumed_tonnes'].iloc[-1])
    lag_3 = float(history['consumed_tonnes'].iloc[-3]) if len(history) >= 3 else lag_1
    lag_7 = float(history['consumed_tonnes'].iloc[-7]) if len(history) >= 7 else lag_1

    rolling_mean_3 = float(history['consumed_tonnes'].tail(3).mean())
    rolling_std_7 = float(history['consumed_tonnes'].tail(7).std())
    if np.isnan(rolling_std_7):
      rolling_std_7 = 0.0

    rain_x_pour = rain_mm * planned_pour
    temp_x_pour = avg_temp_c * planned_pour
    inventory_gap = opening_inventory + deliveries - planned_pour
    inventory_ratio = opening_inventory / silo_capacity if silo_capacity > 0 else 0.0

    feature_row = pd.DataFrame([
      {
        'planned_pour_tonnes': planned_pour,
        'rain_mm': rain_mm,
        'avg_temp_c': avg_temp_c,
        'lag_1': lag_1,
        'lag_3': lag_3,
        'lag_7': lag_7,
        'rolling_mean_3': rolling_mean_3,
        'rolling_std_7': rolling_std_7,
        'rain_x_pour': rain_x_pour,
        'temp_x_pour': temp_x_pour,
        'inventory_gap': inventory_gap,
        'inventory_ratio': inventory_ratio,
      }
    ])[feature_cols]

    forecasted_consumption = float(model.predict(feature_row)[0])
    forecasted_consumption = max(forecasted_consumption, 0.0)

    future_rows.append({
      'date': forecast_date,
      'consumed_tonnes': np.nan,
      'forecasted_consumption': forecasted_consumption,
      'rain_mm': rain_mm,
    })

    history.loc[forecast_date, 'consumed_tonnes'] = forecasted_consumption

  horizon_df = pd.DataFrame(future_rows).set_index('date')
  return horizon_df


def simulate_inventory(
  test_results, 
  site_meta, 
  lead_time_days=2, 
  buffer_rain_threshold=10, 
  buffer_increase=0.1,
  service_level_z=1.65,
  min_reorder_floor_pct=0.0,
  ):

  df_sim = test_results[[
    'consumed_tonnes', 
    'forecasted_consumption', 
    'rain_mm'
    ]].copy()

  df_sim['sim_inventory'] = np.nan
  df_sim['reorder_flag'] = False
  df_sim['recommended_delivery_date'] = None
  df_sim['recommended_delivery_quantity'] = 0.0
  df_sim['buffer_applied'] = False
  df_sim['dynamic_reorder_point'] = np.nan
  df_sim['dynamic_safety_stock'] = np.nan
  df_sim['lead_time_demand_mean'] = np.nan

  silo_capacity = site_meta['silo_capacity']
  inventory = site_meta['initial_inventory']
  reorder_threshold = site_meta['reorder_threshold']
  target_inventory = site_meta['target_inventory']

  lead_time_days = max(int(lead_time_days), 1)
  demand_forecast = df_sim['forecasted_consumption'].fillna(0.0).to_numpy(dtype=float)
  min_reorder_floor = min_reorder_floor_pct * silo_capacity

  delivery_queue = {}

  # Iterate through the simulation dataframe
  for i, (today, row) in enumerate(df_sim.iterrows()):

      # Build a rolling lead-time demand window from forecast.
      lead_window = demand_forecast[i:i + lead_time_days]
      lead_demand_mean = float(lead_window.sum())
      lead_demand_std = float(np.std(lead_window, ddof=0))
      dynamic_safety_stock = service_level_z * lead_demand_std * np.sqrt(lead_time_days)
      dynamic_reorder_point = lead_demand_mean + dynamic_safety_stock
      dynamic_reorder_point = max(dynamic_reorder_point, reorder_threshold, min_reorder_floor)
      dynamic_reorder_point = min(dynamic_reorder_point, silo_capacity)

      df_sim.loc[today, 'lead_time_demand_mean'] = lead_demand_mean
      df_sim.loc[today, 'dynamic_safety_stock'] = dynamic_safety_stock
      df_sim.loc[today, 'dynamic_reorder_point'] = dynamic_reorder_point
      
      # Check if there are any deliveries scheduled for today
      if today in delivery_queue:
          inventory += delivery_queue[today]
          inventory = min(inventory, silo_capacity)  
          del delivery_queue[today]

      # Update inventory based on forecasted consumption
      consumption = row['forecasted_consumption']
      inventory -= consumption
      
      df_sim.loc[today, 'sim_inventory'] = inventory

      # Check if inventory is below the reorder threshold
      if inventory < dynamic_reorder_point:
          df_sim.loc[today, 'reorder_flag'] = True
          delivery_date = today + pd.Timedelta(days=lead_time_days)

          # Calculate the delivery quantity needed to reach the target inventory
          delivery_qty = target_inventory - inventory
          if row['rain_mm'] > buffer_rain_threshold:
              delivery_qty *= (1 + buffer_increase)
              df_sim.loc[today, 'buffer_applied'] = True

          # Ensure that the delivery quantity does not exceed the silo capacity
          delivery_qty = min(delivery_qty, silo_capacity - inventory)
          delivery_queue[delivery_date] = delivery_qty

          # Update the dataframe with the recommended delivery date and quantity
          df_sim.loc[today, 'recommended_delivery_date'] = delivery_date.strftime('%Y-%m-%d')
          df_sim.loc[today, 'recommended_delivery_quantity'] = round(delivery_qty, 2)

  return df_sim


def build_site_metadata_from_data(
    df,
    initial_inventory_pct=0.60,
    reorder_threshold_pct=0.20,
    target_inventory_pct=0.80,
    site_col='site_id',
    date_col='date',
    capacity_col='silo_capacity',
):
    required_cols = {site_col, date_col, capacity_col}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns for metadata derivation: {sorted(missing_cols)}")

    site_capacity_df = (
        df[[site_col, date_col, capacity_col]]
        .dropna(subset=[site_col, capacity_col])
        .copy()
    )
    site_capacity_df[date_col] = pd.to_datetime(site_capacity_df[date_col])
    site_capacity_df = site_capacity_df.sort_values([site_col, date_col])

    # Use each site's latest non-null silo capacity from the data.
    latest_capacity = site_capacity_df.groupby(site_col)[capacity_col].last()

    site_metadata = {}
    for site_id, silo_capacity in latest_capacity.items():
        silo_capacity = float(silo_capacity)
        site_metadata[site_id] = {
            'silo_capacity': silo_capacity,
            'initial_inventory': initial_inventory_pct * silo_capacity,
            'reorder_threshold': reorder_threshold_pct * silo_capacity,
            'target_inventory': target_inventory_pct * silo_capacity,
        }

    return site_metadata


def get_default_what_if_scenarios(base_lead_time_days=2, delayed_extra_days=2):
  """
  Convenience scenario set for planning stress tests.
  """
  base_lead_time_days = max(int(base_lead_time_days), 1)
  delayed_lead_time_days = max(base_lead_time_days + int(delayed_extra_days), base_lead_time_days + 1)

  return [
    {'scenario': 'baseline', 'demand_multiplier': 1.0, 'lead_time_days': base_lead_time_days},
    {'scenario': 'demand_90', 'demand_multiplier': 0.9, 'lead_time_days': base_lead_time_days},
    {'scenario': 'demand_110', 'demand_multiplier': 1.1, 'lead_time_days': base_lead_time_days},
    {'scenario': 'delayed_deliveries', 'demand_multiplier': 1.0, 'lead_time_days': delayed_lead_time_days},
  ]


def _normalize_scenario_configs(scenario_configs, base_lead_time_days=2):
  """
  Normalize user-provided scenario configs into a strict internal format.
  """
  base_lead_time_days = max(int(base_lead_time_days), 1)

  if scenario_configs is None:
    return [
      {
        'scenario': 'baseline',
        'demand_multiplier': 1.0,
        'lead_time_days': base_lead_time_days,
      }
    ]

  normalized = []
  for idx, cfg in enumerate(scenario_configs, start=1):
    if cfg is None:
      continue

    scenario_name = cfg.get('scenario') or cfg.get('name') or f'scenario_{idx}'
    demand_multiplier = float(cfg.get('demand_multiplier', 1.0))
    lead_time_days = max(int(cfg.get('lead_time_days', base_lead_time_days)), 1)

    normalized.append(
      {
        'scenario': str(scenario_name),
        'demand_multiplier': demand_multiplier,
        'lead_time_days': lead_time_days,
      }
    )

  if not normalized:
    normalized.append(
      {
        'scenario': 'baseline',
        'demand_multiplier': 1.0,
        'lead_time_days': base_lead_time_days,
      }
    )

  return normalized


def _enrich_simulation_metrics(sim_results, lead_time_days):
  """
  Add scenario/site-level metrics and row-level coverage days.
  """
  enriched = sim_results.copy()

  lead_time_days = max(int(lead_time_days), 1)
  daily_demand_proxy = enriched['lead_time_demand_mean'] / lead_time_days
  daily_demand_proxy = daily_demand_proxy.replace(0, np.nan)

  # Coverage days: how many days current inventory can sustain expected daily demand.
  enriched['coverage_days'] = np.where(
    daily_demand_proxy.notna(),
    np.maximum(enriched['sim_inventory'], 0) / daily_demand_proxy,
    np.nan,
  )

  avg_inventory = float(np.maximum(enriched['sim_inventory'], 0).mean())
  total_forecast_demand = float(enriched['forecasted_consumption'].sum())
  inventory_turnover = total_forecast_demand / avg_inventory if avg_inventory > 0 else np.nan

  # Site-specific safety stock level summaries (for this scenario).
  safety_stock_mean = float(enriched['dynamic_safety_stock'].mean())
  safety_stock_p95 = float(enriched['dynamic_safety_stock'].quantile(0.95))
  safety_stock_max = float(enriched['dynamic_safety_stock'].max())

  enriched['inventory_turnover'] = inventory_turnover
  enriched['scenario_avg_inventory'] = avg_inventory
  enriched['scenario_total_forecast_demand'] = total_forecast_demand
  enriched['scenario_coverage_days_mean'] = float(enriched['coverage_days'].mean())
  enriched['site_safety_stock_mean'] = safety_stock_mean
  enriched['site_safety_stock_p95'] = safety_stock_p95
  enriched['site_safety_stock_max'] = safety_stock_max

  return enriched

def run_pipeline(
  df,
  site_metadata=None,
  initial_inventory_pct=0.60,
  reorder_threshold_pct=0.20,
  target_inventory_pct=0.80,
  simulation_horizon_days=56,
  lead_time_days=2,
  scenario_configs=None,
):
    all_results = []

    auto_metadata = build_site_metadata_from_data(
      df,
      initial_inventory_pct=initial_inventory_pct,
      reorder_threshold_pct=reorder_threshold_pct,
      target_inventory_pct=target_inventory_pct,
    )

    if site_metadata is None:
      site_metadata = auto_metadata
    else:
      merged_metadata = dict(auto_metadata)
      merged_metadata.update(site_metadata)
      site_metadata = merged_metadata

    scenarios = _normalize_scenario_configs(
      scenario_configs=scenario_configs,
      base_lead_time_days=lead_time_days,
    )

    for site_id in df['site_id'].dropna().unique():
        print(f"Processing site: {site_id}..........")
        if site_id not in site_metadata:
            print(f"Skipping {site_id}: no derived/provided metadata available.")
            continue

        site_df = engineer_features(df, site_id)
        if len(site_df) < 50:
            print(f"Skipping {site_id}..........")
            continue
       
        gb, test_results = train_gb_forecast(site_df)

        if simulation_horizon_days and simulation_horizon_days > 0:
          forecast_input = build_forecast_horizon(
            site_df=site_df,
            model=gb,
            horizon_days=simulation_horizon_days,
          )
        else:
          forecast_input = test_results

        for scenario in scenarios:
          scenario_input = forecast_input.copy()
          scenario_input['forecasted_consumption'] = (
            scenario_input['forecasted_consumption'] * scenario['demand_multiplier']
          ).clip(lower=0)

          sim_results = simulate_inventory(
            scenario_input,
            site_metadata[site_id],
            lead_time_days=scenario['lead_time_days'],
          )
          sim_results = _enrich_simulation_metrics(
            sim_results,
            lead_time_days=scenario['lead_time_days'],
          )
          sim_results['site_id'] = site_id
          sim_results['scenario'] = scenario['scenario']
          sim_results['scenario_demand_multiplier'] = scenario['demand_multiplier']
          sim_results['scenario_lead_time_days'] = scenario['lead_time_days']

          all_results.append(sim_results.reset_index())

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)