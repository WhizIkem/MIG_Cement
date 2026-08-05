# MIG Cement Schema Report

## Overview

- Tables discovered: 3
- Focus: table definitions, field descriptions, date range coverage, record counts, distinct value summaries, and data completeness metrics
- Created Cement_Demand Table
- Total records across tables: 65793

## Table: CementTypes

### Definition

```sql
CREATE TABLE CementTypes (
    cement_type TEXT PRIMARY KEY
)
```

- Row count: 3

### Date range coverage

- No date-like column detected for this table.

### Fields

| Column | Type | Description | Null/empty | Completeness | Distinct values | Sample values |
| --- | --- | --- | ---: | ---: | ---: | --- |
| cement_type | TEXT | Categorical type or classification field | 0 | 100.0% | 3 | CEM_I, CEM_II, CEM_III |

## Table: Cement_Demand

### Definition

```sql
CREATE TABLE Cement_Demand(
  date TEXT,
  site_id TEXT,
  cement_type TEXT,
  planned_pour_tonnes REAL,
  consumed_tonnes REAL,
  opening_inventory_tonnes REAL,
  deliveries_tonnes REAL,
  closing_inventory_tonnes REAL,
  rain_mm REAL,
  avg_temp_c REAL,
  operation_silo_capacity INT,
  region TEXT,
  site_silo_capacity INT,
  behavior TEXT
)
```

- Row count: 32880

### Date range coverage

- Date column: date
- Min: 2022-01-01
- Max: 2024-12-31

### Fields

| Column | Type | Description | Null/empty | Completeness | Distinct values | Sample values |
| --- | --- | --- | ---: | ---: | ---: | --- |
| date | TEXT | Date or timestamp field | 0 | 100.0% | 1096 | 2022-01-01, 2022-01-02, 2022-01-03, 2022-01-04, 2022-01-05 |
| site_id | TEXT | Identifier field | 0 | 100.0% | 30 | SITE_001, SITE_002, SITE_003, SITE_004, SITE_005 |
| cement_type | TEXT | Categorical type or classification field | 0 | 100.0% | 3 | CEM_I, CEM_II, CEM_III |
| planned_pour_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 5753 | 0.0, 5.0, 5.01, 5.02, 5.03 |
| consumed_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 5810 | 0.0, 0.86, 1.67, 1.76, 2.07 |
| opening_inventory_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 19423 | 0.0, 0.01, 0.02, 0.03, 0.04 |
| deliveries_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 4002 | 0.0, 10.0, 10.01, 10.02, 10.03 |
| closing_inventory_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 19424 | 0.0, 0.01, 0.02, 0.03, 0.04 |
| rain_mm | REAL | Numeric measure or metric | 0 | 100.0% | 2389 | 0.0, 0.01, 0.02, 0.03, 0.04 |
| avg_temp_c | REAL | Numeric measure or metric | 0 | 100.0% | 3526 | -5.0, -4.99, -4.98, -4.97, -4.96 |
| operation_silo_capacity | INT | Numeric measure or metric | 0 | 100.0% | 27 | 120, 152, 153, 154, 158 |
| region | TEXT | Categorical attribute | 0 | 100.0% | 4 | East, North, South, West |
| site_silo_capacity | INT | Numeric measure or metric | 0 | 100.0% | 27 | 120, 152, 153, 154, 158 |
| behavior | TEXT | Categorical attribute | 0 | 100.0% | 3 | aggressive, chaotic, conservative |

## Table: Operations

### Definition

```sql
CREATE TABLE Operations (
    date TEXT,
    site_id TEXT,
    cement_type TEXT,
    planned_pour_tonnes REAL,
    consumed_tonnes REAL,
    opening_inventory_tonnes REAL,
    deliveries_tonnes REAL,
    closing_inventory_tonnes REAL,
    rain_mm REAL,
    avg_temp_c REAL,
    silo_capacity INTEGER,
    FOREIGN KEY(site_id) REFERENCES Sites(site_id),
    FOREIGN KEY(cement_type) REFERENCES CementTypes(cement_type)
)
```

- Row count: 32880

### Date range coverage

- Date column: date
- Min: 2022-01-01
- Max: 2024-12-31

### Fields

| Column | Type | Description | Null/empty | Completeness | Distinct values | Sample values |
| --- | --- | --- | ---: | ---: | ---: | --- |
| date | TEXT | Date or timestamp field | 0 | 100.0% | 1096 | 2022-01-01, 2022-01-02, 2022-01-03, 2022-01-04, 2022-01-05 |
| site_id | TEXT | Identifier field | 0 | 100.0% | 30 | SITE_001, SITE_002, SITE_003, SITE_004, SITE_005 |
| cement_type | TEXT | Categorical type or classification field | 0 | 100.0% | 3 | CEM_I, CEM_II, CEM_III |
| planned_pour_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 5753 | 0.0, 5.0, 5.01, 5.02, 5.03 |
| consumed_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 5810 | 0.0, 0.86, 1.67, 1.76, 2.07 |
| opening_inventory_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 19423 | 0.0, 0.01, 0.02, 0.03, 0.04 |
| deliveries_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 4002 | 0.0, 10.0, 10.01, 10.02, 10.03 |
| closing_inventory_tonnes | REAL | Numeric measure or metric | 0 | 100.0% | 19424 | 0.0, 0.01, 0.02, 0.03, 0.04 |
| rain_mm | REAL | Numeric measure or metric | 0 | 100.0% | 2389 | 0.0, 0.01, 0.02, 0.03, 0.04 |
| avg_temp_c | REAL | Numeric measure or metric | 0 | 100.0% | 3526 | -5.0, -4.99, -4.98, -4.97, -4.96 |
| silo_capacity | INTEGER | Numeric measure or metric | 0 | 100.0% | 27 | 120, 152, 153, 154, 158 |

### Relationships

- Operations.cement_type -> CementTypes.cement_type
- Operations.site_id -> Sites.site_id

## Table: Sites

### Definition

```sql
CREATE TABLE Sites (
    site_id TEXT PRIMARY KEY,
    region TEXT,
    silo_capacity INTEGER,
    behavior TEXT
)
```

- Row count: 30

### Date range coverage

- No date-like column detected for this table.

### Fields

| Column | Type | Description | Null/empty | Completeness | Distinct values | Sample values |
| --- | --- | --- | ---: | ---: | ---: | --- |
| site_id | TEXT | Identifier field | 0 | 100.0% | 30 | SITE_001, SITE_002, SITE_003, SITE_004, SITE_005 |
| region | TEXT | Categorical attribute | 0 | 100.0% | 4 | East, North, South, West |
| silo_capacity | INTEGER | Numeric measure or metric | 0 | 100.0% | 27 | 120, 152, 153, 154, 158 |
| behavior | TEXT | Categorical attribute | 0 | 100.0% | 3 | aggressive, chaotic, conservative |
