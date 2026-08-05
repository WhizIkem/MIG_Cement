# Gradient Boosting Feature Engineering Results

## Overview

This report documents the feature-engineered Gradient Boosting model and compares its performance against the Random Forest baseline model.

## Engineered Features

The following feature groups were added:

- Date features: `day_of_week`, `month`, `quarter`, `is_weekend`, `is_holiday`
- Consumption lags: `lag_1`, `lag_3`, `lag_7`, `lag_14`, `lag_28`
- Rolling averages: `rolling_avg_7`, `rolling_avg_28`
- Inventory metric: `days_of_coverage`
- Weather features: `rain_total_3d`, `temp_avg_3d`, `temp_trend_3d`

## Feature Importance

![Gradient Boosting Feature Importance](xgboost_feature_importance.png)

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

## Performance Summary

- Baseline comparison: Random Forest baseline
- Delivered planning model: fine-tuned Gradient Boosting
- Detailed per-site metrics are captured in `gradient_boosting_kpi_summary.csv`

## Artifacts

- Feature importance plot: `xgboost_feature_importance.png`
- Performance comparison matrix: `gradient_boosting_kpi_summary.csv`
- Markdown report: `xgboost_feature_engineering_report.md`
