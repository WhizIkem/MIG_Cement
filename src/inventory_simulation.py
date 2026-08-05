# src/inventory_simulation.py

import pandas as pd
import numpy as np

# Define a function to build the simulation input dataframe from test features and forecasted values
def build_simulation_input(X_test, forecast, rain_col="rain_mm"):
    """
    Build the simulation input dataframe from test features and forecasted values.
    """
    df_sim = pd.DataFrame({
        "date": pd.to_datetime(X_test.index),
        "forecasted_consumption": np.asarray(forecast),
        "rain_forcast_mm": X_test[rain_col].to_numpy()
    })

    return df_sim.sort_values(by="date").reset_index(drop=True)

# Define a function to simulate inventory levels and generate delivery recommendations
def simulate_inventory(
    df_sim,
    initial_inventory,
    silo_capacity,
    reorder_threshold,
    target_inventory,
    lead_time_days=2,
    buffer_rain_threshold=10,
    buffer_increase=0.1,
    date_col="date",
    demand_col="forecasted_consumption",
    rain_col="rain_forcast_mm"
):

    """
    Simulate inventory levels and generate delivery recommendation
    """

    df_sim = df_sim.copy()
    df_sim[date_col] = pd.to_datetime(df_sim[date_col])
    df_sim = df_sim.sort_values(date_col).reset_index(drop=True)

    df_sim["sim_inventory"] = np.nan
    df_sim["reorder_flag"] = False
    df_sim["recommended_delivery_date"] = None
    df_sim["recommended_delivery_quantity"] = 0.0
    df_sim["buffer_applied"] = False

    inventory = initial_inventory
    delivery_queue = {}

    for i, row in df_sim.iterrows():
        today = row[date_col]

        if today in delivery_queue:
            inventory += delivery_queue[today]
            inventory = min(inventory, silo_capacity)
            del delivery_queue[today]

        consumption = row[demand_col]
        inventory -= consumption
        df_sim.loc[i, "sim_inventory"] = inventory

        if inventory < reorder_threshold:
            df_sim.loc[i, "reorder_flag"] = True

            delivery_date = today + pd.Timedelta(days=lead_time_days)
            delivery_quantity = target_inventory - inventory

            if row[rain_col] > buffer_rain_threshold:
                delivery_quantity *= (1 + buffer_increase)
                df_sim.loc[i, "buffer_applied"] = True

            delivery_quantity = min(delivery_quantity, silo_capacity - inventory)
            delivery_queue[delivery_date] = delivery_quantity

            df_sim.loc[i, "recommended_delivery_date"] = delivery_date.strftime("%Y-%m-%d")
            df_sim.loc[i, "recommended_delivery_quantity"] = round(delivery_quantity, 2)

    return df_sim

# Define a function to simulate inventory for all sites based on their forecasts and raw data
def simulate_inventory_all_sites(
    predictions_df,
    raw_df,
    lead_time_days=2,
    buffer_rain_threshold=10,
    buffer_increase=0.1,
    initial_inventory_pct=0.60,
    reorder_threshold_pct=0.20,
    target_inventory_pct=0.80,
    site_col="site_id",
    date_col="date",
    forecast_col="forecasted_consumed_tonnes",
    rain_col="rain_mm",
    capacity_col="silo_capacity",
):
    """
    Run inventory simulation for every site using the per-site forecast rows.

    Required columns:
    predictions_df: site_id, date, forecasted_consumed_tonnes (or configured names)
    raw_df: site_id, date, silo_capacity, rain_mm (or configured names)
    """
    all_inventory_simulations = []

    # Keep only needed columns from raw data to avoid duplicate/extra merge fields
    site_info = raw_df[[site_col, date_col, capacity_col, rain_col]].copy()
    site_info[date_col] = pd.to_datetime(site_info[date_col])

    for site_id in predictions_df[site_col].dropna().unique():
        pred_df = predictions_df[predictions_df[site_col] == site_id].copy()
        if pred_df.empty:
            continue

        pred_df[date_col] = pd.to_datetime(pred_df[date_col])

        # Merge capacity + rain by date/site
        site_pred_df = pred_df.merge(
            site_info[site_info[site_col] == site_id],
            on=[site_col, date_col],
            how="left",
        ).sort_values(date_col).reset_index(drop=True)

        # Skip if capacity is missing
        if site_pred_df[capacity_col].isna().all():
            continue

        silo_capacity = float(site_pred_df[capacity_col].dropna().iloc[0])
        initial_inventory = initial_inventory_pct * silo_capacity
        reorder_threshold = reorder_threshold_pct * silo_capacity
        target_inventory = target_inventory_pct * silo_capacity

        # Reuse your single-site simulation function
        simulated_df = simulate_inventory(
            df_sim=site_pred_df,
            initial_inventory=initial_inventory,
            silo_capacity=silo_capacity,
            reorder_threshold=reorder_threshold,
            target_inventory=target_inventory,
            lead_time_days=lead_time_days,
            buffer_rain_threshold=buffer_rain_threshold,
            buffer_increase=buffer_increase,
            date_col=date_col,
            demand_col=forecast_col,
            rain_col=rain_col,  # pass explicitly to avoid default-name mismatches
        )

        all_inventory_simulations.append(simulated_df)

    if not all_inventory_simulations:
        return pd.DataFrame()

    return pd.concat(all_inventory_simulations, ignore_index=True)

# Define a function to summarize inventory metrics for each site
def summarize_inventory_metrics(
    inventory_simulations_df,
    site_col="site_id",
    inventory_col="sim_inventory",
    reorder_col="reorder_flag",
):
    """
    Build per-site stockouts, service level, and delivery count summary.
    """
    if inventory_simulations_df.empty:
        return pd.DataFrame(columns=[site_col, "stockouts", "service_level", "num_deliveries"])

    rows = []
    for site_id in inventory_simulations_df[site_col].dropna().unique():
        site_df = inventory_simulations_df[inventory_simulations_df[site_col] == site_id]
        stockouts = int((site_df[inventory_col] < 0).sum())
        service_level = 100 * (1 - stockouts / len(site_df))
        num_deliveries = int(site_df[reorder_col].sum())

        rows.append({
            site_col: site_id,
            "stockouts": stockouts,
            "service_level": round(service_level, 2),
            "num_deliveries": num_deliveries,
        })

    return pd.DataFrame(rows)