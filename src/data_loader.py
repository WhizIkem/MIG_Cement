import sqlite3
import pandas as pd

# Define a reusable function for loading the MIG cement dataset
def load_cement_data(db_path="../data/raw/MIG_Cement_Records.db"):
  conn = sqlite3.connect(db_path) # open a connection to the SQLite database

  # define the sql query that extracts the main analysis dataset
  query = """
  SELECT
    o.date,
    o.site_id,
    s.region,
    s.behavior,
    o.cement_type,
    o.planned_pour_tonnes,
    o.consumed_tonnes,
    o.opening_inventory_tonnes,
    o.deliveries_tonnes,
    o.closing_inventory_tonnes,
    o.rain_mm,
    o.avg_temp_c,
    o.silo_capacity
  FROM Operations o
  JOIN Sites s ON o.site_id = s.site_id
  """
  # run the SQL query and load result into pandas DataFrame
  df = pd.read_sql_query(query, conn)

  conn.close() # Close the database connection after loading the data
  
  # Convert date column from text into pandas datetime format.
  df["date"] = pd.to_datetime(
    df['date']
    )
  
  return df # return the final cleaned analysis