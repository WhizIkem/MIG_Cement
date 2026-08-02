import sqlite3
from pathlib import Path
import pandas as pd

# Path to MIG Cement database file
base_dir = Path(__file__).resolve().parent
db_path = base_dir / "data" / "raw" / "MIG_Cement_Records.db"

# Connect to the database
conn = sqlite3.connect(db_path)

# Create a cursor object to run SQL script
cursor = conn.cursor()

print("Connected to SQLite database successfully.")

# Query sqlite_master to list all tables and views
cursor.execute("""
SELECT
               type,
               name,
               sql
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY type, name;
""")

# Create Cement_demand Table
sql = """
  CREATE TABLE IF NOT EXISTS Cement_Demand AS
  SELECT
    o.date,
    o.site_id,
    o.cement_type,
    o.planned_pour_tonnes,
    o.consumed_tonnes,
    o.opening_inventory_tonnes,
    o.deliveries_tonnes,
    o.closing_inventory_tonnes,
    o.rain_mm,
    o.avg_temp_c,
    o.silo_capacity AS operation_silo_capacity,
    s.region,
    s.silo_capacity AS site_silo_capacity,
    s.behavior
  FROM Operations AS o
  LEFT JOIN CementTypes AS ct
    ON o.cement_type = ct.cement_type
  LEFT JOIN Sites AS s
    ON o.site_id = s.site_id
"""
conn.commit()

cursor.execute("SELECT COUNT(*) FROM Cement_Demand;")
print("\nRows in Cement_Demand:", cursor.fetchone()[0])

# Extract column definitions, data types, and constraints for Cement_Demand table
cursor.execute("PRAGMA table_info(Cement_Demand)")
columns = cursor.fetchall()
print("\nColumn definition:")
for column in columns:
  print(column)
cursor.execute("PRAGMA foreign_key_list(Cement_Demand)")
foreign_keys = cursor.fetchall()
print("\nForeign keys constraints:")
for fk in foreign_keys:
  print(fk)
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name= 'Operations'")
create_table = cursor.fetchone()
print("\nCREATE TABLE Statement:")
print(create_table[0])

# date range assessment
cursor.execute("""
  SELECT
    COUNT(*) AS total_rows,
    MIN(date) AS first_date,
    MAX(date) AS last_date
  FROM Cement_Demand;
""")
total_rows, first_date, last_date = cursor.fetchone()
print("\nRows:", total_rows)
print("Date range:", first_date, "to", last_date )

# Distinct values for categorical columns
# Site ID
cursor.execute("""
  SELECT DISTINCT site_id
  FROM Cement_Demand
  ORDER BY site_id;
  """)
site_ids = cursor.fetchall()
print("\nDistinct site IDs:")
for site in site_ids:
  print(site[0])

# Cement type
cursor.execute("""
  SELECT DISTINCT cement_type
  FROM Cement_Demand
  ORDER BY cement_type;
  """)
cement_types = cursor.fetchall()
print("\nDistinct Cement types:")
for cement in cement_types:
  print(cement[0])

# Descriptive Statistics
df = pd.read_sql_query("SELECT * FROM Cement_Demand;", conn)

describe = df.describe(include="all")
print(f"\nDescriptive analysis: {describe}")

info = df.info()
print(f"\nData information: {info}")

# check for Null
null = df.isnull().sum()

print(f"\nnull value: {null}")

# Check for duplicate records
duplicates = df[df.duplicated(subset=["date", "site_id", "cement_type"], keep=False)]
print(f"\nduplicates: {duplicates}")

# inventory equation validation check
invalid_rows = df[
  abs(
    df["closing_inventory_tonnes"] -
    (df["opening_inventory_tonnes"] + df["deliveries_tonnes"] - df["consumed_tonnes"])
  ) > 0.01
]
print(f"\ninvalid rows: {invalid_rows}")

# Records where consumed_tonnes is greater than planned_pour_tonnes
df["variance_percent"] = None # where planned tonnes > 0

df.loc[df["planned_pour_tonnes"] > 0, "variance_percent"] = (
  (df["consumed_tonnes"] - df["planned_pour_tonnes"])
  / df["planned_pour_tonnes"]
) * 100
print(df["variance_percent"].describe())

# Identify negative values
negative_rows = df[
  (df["consumed_tonnes"] < 0) |
  (df["opening_inventory_tonnes"] < 0) |
  (df["deliveries_tonnes"] < 0) |
  (df["closing_inventory_tonnes"] < 0)
]
print("\nNegative rows:", negative_rows)

# Detect outlier using IQR method
columns = [
  "consumed_tonnes",
  "opening_inventory_tonnes",
  "deliveries_tonnes",
  "closing_inventory_tonnes"
]
for col in columns:
  q1 = df[col].quantile(0.25)
  q3 = df[col].quantile(0.75)
  iqr = q3 - q1
  
  lower_limit = q1 - 1.5 * iqr
  upper_limit = q3 + 1.5 * iqr

  outliers = df[(df[col] < lower_limit) | (df[col] > upper_limit)]

  print(f"\n{col}")
  print("Lower limit:", lower_limit)
  print("Upper limit:", upper_limit)
  print("Outlier count:", len(outliers))

# reasonable ranges for rain and temperature
print("\nWeather Null counts:")
print(df[["rain_mm", "avg_temp_c"]].isnull().sum())

bad_weather = df[
  (df["rain_mm"] < 0) |
  (df["avg_temp_c"] < -5) |
  (df["avg_temp_c"] > 35)
]
print("\nWeather records outside reasonable range:")
print(bad_weather)

rainy_count = (df["rain_mm"] > 0).sum()
print("\nRecords with rain > 0:", rainy_count)

# Data quality scorecard with issue counts
original_columns = [
  "date", "site_id", "cement_type",
  "planned_pour_tonnes", "consumed_tonnes",
  "opening_inventory_tonnes", "deliveries_tonnes",
  "closing_inventory_tonnes", "rain_mm", "avg_temp_c",
  "operation_silo_capacity", "region",
  "site_silo_capacity", "behavior"
]

df["has_nulls"] = df[original_columns].isnull().any(axis=1)

df["has_negative_values"] = (
    (df["consumed_tonnes"] < 0) |
    (df["opening_inventory_tonnes"] < 0) |
    (df["deliveries_tonnes"] < 0) |
    (df["closing_inventory_tonnes"] < 0)
)

df["inventory_balance_error"] = (
    abs(
        df["closing_inventory_tonnes"] -
        (df["opening_inventory_tonnes"] + df["deliveries_tonnes"] - df["consumed_tonnes"])
    ) > 0.01
)

df["high_consumption_variance"] = (
  (df["planned_pour_tonnes"] > 0) &
  (df["consumed_tonnes"] > df["planned_pour_tonnes"] * 1.20)
)

df["weather_range_error"] = (
    (df["rain_mm"] < 0) |
    (df["avg_temp_c"] < -5) |
    (df["avg_temp_c"] > 35)
)

scorecard = df.groupby("site_id").agg(
    total_records=("site_id", "count"),
    records_with_nulls=("has_nulls", "sum"),
    negative_value_records=("has_negative_values", "sum"),
    inventory_balance_errors=("inventory_balance_error", "sum"),
    high_consumption_variance=("high_consumption_variance", "sum"),
    weather_range_errors=("weather_range_error", "sum")
).reset_index()

print("\nScorecard:", scorecard)

def describe_issues(row):
  issues = []
  if row["has_nulls"]:
    issues.append("Missing value")

  if row["has_negative_values"]:
    issues.append("Negative quantity value")
  
  if row["inventory_balance_error"]:
    issues.append("Inventory balance mismatch")

  if row["high_consumption_variance"]:
    issues.append("Consumption more than 20% above planned pour")

  if row["weather_range_error"]:
    issues.append("Weather value outside expected range")

  return "; ".join(issues)

df["issue_description"] = df.apply(describe_issues, axis=1)
flagged_df = df[df["issue_description"] != ""].copy()
print("\nFlagged errors:", flagged_df)

# Saved flagged error
flagged_df.to_csv("reports/flagged_records.csv", index=False)

conn.close()
