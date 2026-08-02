-- SQLite 

-- Query sqlite_master to list all tables and views
SELECT
  type,
  name,
  sql
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY type, name;

-- Create Cement_Demand
DROP TABLE IF EXISTS Cement_Demand;
CREATE TABLE Cement_Demand AS
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
  ON o.site_id = s.site_id;

SELECT *
FROM Cement_Demand
LIMIT 10;

-- Extract column definitions, data types, and constraints for Operations table
PRAGMA table_info(Cement_Demand);
PRAGMA foreign_key_list(Cement_Demand);

-- date range assessment
SELECT
  COUNT(*) AS total_rows,
  MIN(date) AS first_date,
  MAX(date) AS last_date
FROM Cement_Demand;

-- distinct values for categorical columns
SELECT DISTINCT site_id
FROM Cement_Demand
ORDER BY site_id;

SELECT DISTINCT cement_type
FROM Cement_Demand
ORDER BY cement_type;

-- Count records each value has
SELECT
  site_id,
  COUNT(*) AS record_count
FROM Cement_Demand
GROUP BY site_id
ORDER BY site_id;

SELECT
  cement_type,
  COUNT(*) AS record_count
FROM Cement_Demand
GROUP BY cement_type
ORDER BY cement_type;

-- Check for NULL
SELECT *
FROM Cement_Demand
WHERE date IS NULL
   OR site_id IS NULL
   OR region IS NULL
   OR cement_type IS NULL
   OR planned_pour_tonnes IS NULL
   OR consumed_tonnes IS NULL
   OR opening_inventory_tonnes IS NULL
   OR deliveries_tonnes IS NULL
   OR closing_inventory_tonnes IS NULL
   OR rain_mm IS NULL
   OR avg_temp_c IS NULL
   OR operation_silo_capacity IS NULL
   OR site_silo_capacity IS NULL
   OR behavior IS NULL;

-- Check for duplicate records
SELECT
  date,
  site_id,
  cement_type,
  COUNT(*) AS record_count
FROM Cement_Demand
GROUP BY
  date,
  site_id,
  cement_type
HAVING COUNT(*) > 1
ORDER BY record_count DESC;

SELECT COUNT(*) AS duplicate_key_groups
FROM (
    SELECT
        date,
        site_id,
        cement_type
    FROM Cement_Demand
    GROUP BY
        date,
        site_id,
        cement_type
    HAVING COUNT(*) > 1
);

-- inventory equation validation check
SELECT *
FROM Cement_Demand
WHERE ABS(
      closing_inventory_tonnes -
      (opening_inventory_tonnes + deliveries_tonnes - consumed_tonnes)
) > 0.01;

-- Records where consumed_tonnes is greater than planned_pour_tonnes
SELECT
    AVG(((consumed_tonnes - planned_pour_tonnes) / planned_pour_tonnes) * 100) AS avg_variance_percent,
    MIN(((consumed_tonnes - planned_pour_tonnes) / planned_pour_tonnes) * 100) AS min_variance_percent,
    MAX(((consumed_tonnes - planned_pour_tonnes) / planned_pour_tonnes) * 100) AS max_variance_percent
FROM Cement_Demand
WHERE planned_pour_tonnes > 0;

-- identify negative values
SELECT *
FROM Cement_Demand
WHERE consumed_tonnes < 0
  OR opening_inventory_tonnes < 0
  OR deliveries_tonnes < 0
  OR closing_inventory_tonnes < 0;

-- Detect outlier
SELECT
  MIN(consumed_tonnes) AS min_consumed,
  MAX(consumed_tonnes) AS max_consumed,
  MIN(opening_inventory_tonnes) AS min_opening_inventory,
  MAX(opening_inventory_tonnes) AS max_opening_inventory,
  MIN(closing_inventory_tonnes) AS min_closing_inventory,
  MAX(closing_inventory_tonnes) AS max_closing_inventory
FROM Cement_Demand;

-- reasonable ranges for rain and temperature
SELECT *
FROM Cement_Demand
WHERE rain_mm < 0
  OR avg_temp_c < -5
  OR avg_temp_c > 35;

SELECT COUNT(*) AS rainy_records
FROM Cement_Demand
WHERE rain_mm > 0;

-- Data quality scorecard with issue counts
SELECT
  site_id,
  COUNT(*) AS total_records,

  SUM(
    CASE
      WHEN date IS NULL
        OR site_id IS NULL
        OR cement_type IS NULL
        OR consumed_tonnes IS NULL
        OR planned_pour_tonnes IS NULL
        OR opening_inventory_tonnes IS NULL
        OR deliveries_tonnes IS NULL
        OR closing_inventory_tonnes IS NULL
        OR rain_mm IS NULL
        OR avg_temp_c IS NULL
      THEN 1 ELSE 0
    END
  ) AS records_with_nulls,

  SUM(
    CASE 
      WHEN ABS(
        closing_inventory_tonnes -
        (opening_inventory_tonnes + deliveries_tonnes - consumed_tonnes)
      ) > 0.01
      THEN 1 ELSE 0
    END
  ) AS inventory_balance_errors,

  SUM(
    CASE
      WHEN consumed_tonnes > planned_pour_tonnes
      THEN 1 ELSE 0
    END
  ) AS high_consumption_variance,

  SUM(
    CASE
      WHEN rain_mm < 0
        OR avg_temp_c < -5
        OR avg_temp_c > 35
      THEN 1 ELSE 0
    END
  ) AS weather_range_errors

FROM Cement_Demand
GROUP BY site_id
ORDER BY site_id;