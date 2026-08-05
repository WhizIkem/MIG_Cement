import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# Define a function to engineer features for a given site
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


def train_rf_forecast(site_df):
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

  rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=10, 
    random_state=42
    )
  rf.fit(X_train, y_train)

  forecast=rf.predict(X_test)

  test_results = site_df.iloc[split_index:].copy()
  test_results['forecasted_consumption'] = forecast

  return rf, test_results


def simulate_inventory(
  test_results, 
  site_meta, 
  lead_time_days=2, 
  buffer_rain_threshold=10, 
  buffer_increase=0.1
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

  silo_capacity = site_meta['silo_capacity']
  inventory = site_meta['initial_inventory']
  reorder_threshold = site_meta['reorder_threshold']
  target_inventory = site_meta['target_inventory']

  delivery_queue = {}

  # Iterate through the simulation dataframe
  for today, row, in df_sim.iterrows():
      
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
      if inventory < reorder_threshold:
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
          df_sim.loc[today, 'recommended_delivery_qty'] = round(delivery_qty, 2)

  return df_sim


def run_pipeline(df, site_metadata,):
    all_results = []

    # for site_id in df['site_id'].unique():
    for site_id in ['SITE_001', 'SITE_015', 'SITE_030']:
      print(f"Processing site: {site_id}..........")
      site_df = engineer_features(df, site_id)
      if len(site_df) < 50:
        print(f"Skipping {site_id}..........")
        continue
       
      rf, test_results = train_rf_forecast(site_df)
      sim_results = simulate_inventory(test_results, site_metadata[site_id])
      sim_results['site_id'] = site_id
   
      all_results.append(sim_results.reset_index())

    return pd.concat(all_results, ignore_index=True)