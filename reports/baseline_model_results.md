# Baseline Model Results

## Model

- Model type: SARIMAX
- Site ID: `SITE_001`
- Target variable: `consumed_tonnes`
- Exogenous variables: `planned_pour_tonnes`, `rain_mm`, `avg_temp_c`
- Forecast horizon: 56 days / 8 weeks
- Training observations: 876
- Test observations used for forecast: 56

## Hyperparameters

- order: `(0, 0, 2)`
- seasonal_order: `(0, 2, 2, 7)`
- AIC: 6696.3190
- enforce_stationarity: `False`
- enforce_invertibility: `False`

## Performance Metrics

| Metric | Value |
| --- | ---: |
| MAPE | 53.88% |
| RMSE | 10.48 |

## Forecast Visualization

![SARIMAX Forecast](sarimax_forecast.png)

## Diagnostic Tests

| Test | Value | Interpretation |
| --- | ---: | --- |
| Ljung-Box p-value, lag 10 | 0.573660 | Higher values suggest less remaining autocorrelation in residuals. |
| Jarque-Bera normality p-value | 0.000778 | Higher values suggest residuals are closer to normally distributed. |

## Artifacts

- Serialized model: `sarimax_model.pkl`
- Forecast visualization: `sarimax_forecast.png`
- Forecast values: `sarimax_forecast_values.csv`
