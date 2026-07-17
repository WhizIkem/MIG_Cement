# XGBoost Feature Engineering Results

## Overview

This report documents the feature-engineered XGBoost model and compares its performance against the baseline SARIMAX model.

## Engineered Features

The following feature groups were added:

- Date features: `day_of_week`, `month`, `quarter`, `is_weekend`, `is_holiday`
- Consumption lags: `lag_1`, `lag_3`, `lag_7`, `lag_14`, `lag_28`
- Rolling averages: `rolling_avg_7`, `rolling_avg_28`
- Inventory metric: `days_of_coverage`
- Weather features: `rain_total_3d`, `temp_avg_3d`, `temp_trend_3d`

## Feature Importance

![XGBoost Feature Importance](xgboost_feature_importance.png)

### Top Features

| feature             |   importance |
|:--------------------|-------------:|
| planned_pour_tonnes |    0.481363  |
| rain_mm             |    0.183804  |
| days_of_coverage    |    0.0744202 |
| avg_temp_c          |    0.0466673 |
| lag_1               |    0.0262351 |
| rain_3day_total     |    0.0215465 |
| temp_trend_3day     |    0.0205917 |
| lag_3               |    0.0192573 |
| lag_14              |    0.0189703 |
| temp_avg_3day       |    0.0177708 |

## Performance Comparison Matrix

| site_id   |   SARIMAX MAPE |   SARIMAX RMSE |   XGBoost MAPE |   XGBoost RMSE | Better_MAPE_Model   | Better_RMSE_Model   | Overall_Better_Model   |
|:----------|---------------:|---------------:|---------------:|---------------:|:--------------------|:--------------------|:-----------------------|
| SITE_001  |          53.88 |          13.21 |          39.52 |          10.59 | XGBoost             | XGBoost             | XGBoost                |
| SITE_002  |           3.78 |           0.5  |           1.23 |           0.18 | XGBoost             | XGBoost             | XGBoost                |
| SITE_003  |          27.52 |          10.44 |          16.35 |           6.85 | XGBoost             | XGBoost             | XGBoost                |
| SITE_004  |           3.35 |           0.44 |           4.63 |           0.93 | SARIMAX             | SARIMAX             | SARIMAX                |
| SITE_005  |          30.6  |          11.85 |          20.1  |           8.73 | XGBoost             | XGBoost             | XGBoost                |
| SITE_006  |          25.61 |          10.04 |          10.86 |           5.95 | XGBoost             | XGBoost             | XGBoost                |
| SITE_007  |          37.55 |          10.95 |          21.39 |           7.41 | XGBoost             | XGBoost             | XGBoost                |
| SITE_008  |          35.72 |          11.57 |          26.85 |           8.04 | XGBoost             | XGBoost             | XGBoost                |
| SITE_009  |           3.37 |           0.48 |           1.25 |           0.16 | XGBoost             | XGBoost             | XGBoost                |
| SITE_010  |          45.32 |          13.46 |          34.6  |           9.4  | XGBoost             | XGBoost             | XGBoost                |
| SITE_011  |          32.05 |          10.95 |          23.74 |           8.19 | XGBoost             | XGBoost             | XGBoost                |
| SITE_012  |           3.1  |           0.44 |           0.84 |           0.13 | XGBoost             | XGBoost             | XGBoost                |
| SITE_013  |          19.25 |           7.13 |           4.08 |           2.99 | XGBoost             | XGBoost             | XGBoost                |
| SITE_014  |          12.86 |           5.12 |           3.92 |           2.91 | XGBoost             | XGBoost             | XGBoost                |
| SITE_015  |           2.67 |           0.45 |           2.74 |           0.67 | SARIMAX             | SARIMAX             | SARIMAX                |
| SITE_016  |          16.65 |           6.93 |           8.77 |           2.81 | XGBoost             | XGBoost             | XGBoost                |
| SITE_017  |          39.68 |          11.55 |          28.6  |           8.13 | XGBoost             | XGBoost             | XGBoost                |
| SITE_018  |          34.87 |          11.5  |          24    |           8.2  | XGBoost             | XGBoost             | XGBoost                |
| SITE_019  |           3.65 |           0.58 |           1.4  |           0.29 | XGBoost             | XGBoost             | XGBoost                |
| SITE_020  |          36.59 |          11.08 |          29.23 |           9.37 | XGBoost             | XGBoost             | XGBoost                |
| SITE_021  |          35.76 |          11.69 |          29.57 |           9.4  | XGBoost             | XGBoost             | XGBoost                |
| SITE_022  |          44.46 |          12.67 |          32.35 |           9.57 | XGBoost             | XGBoost             | XGBoost                |
| SITE_023  |           3.25 |           0.55 |           3.82 |           0.78 | SARIMAX             | SARIMAX             | SARIMAX                |
| SITE_024  |           8.93 |           3.94 |           2.93 |           1.58 | XGBoost             | XGBoost             | XGBoost                |
| SITE_025  |          44.39 |          13.46 |          28.86 |          10.08 | XGBoost             | XGBoost             | XGBoost                |
| SITE_026  |          13.66 |           7.4  |           2.74 |           1.99 | XGBoost             | XGBoost             | XGBoost                |
| SITE_027  |           3.29 |           0.5  |           0.96 |           0.13 | XGBoost             | XGBoost             | XGBoost                |
| SITE_028  |           8.55 |           4.18 |           2.32 |           1.14 | XGBoost             | XGBoost             | XGBoost                |
| SITE_029  |           3.21 |           0.43 |           2.8  |           0.63 | XGBoost             | SARIMAX             | Mixed                  |
| SITE_030  |          55.57 |          13.23 |          37.5  |           9.95 | XGBoost             | XGBoost             | XGBoost                |

## Artifacts

- Feature importance plot: `xgboost_feature_importance.png`
- Performance comparison matrix: `model_performance_comparison.csv`
- Markdown report: `xgboost_feature_engineering_report.md`
