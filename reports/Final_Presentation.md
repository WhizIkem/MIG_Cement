# Final Presentation Deck

## Slide 1: Title

MIG Cement Inventory Optimization and Forecasting Dashboard

- Scope: 30 cement-consuming sites
- Horizon: 56-day forecast and planning window
- Deliverables: forecasting model, scenario planning dashboard, operational handover package

## Slide 2: Business Problem

- Cement inventory decisions were reactive and difficult to standardize across sites.
- Sites faced meaningful stockout, overcapacity, and reactive-ordering risk.
- Existing workflow lacked a unified planning view for demand, replenishment, safety stock, and scenario stress tests.

Evidence from project artifacts:
- Average end-of-day stockout rate: 24.18%
- Average overcapacity rate: 34.79%
- Average reactive ordering rate: 50.80%

| KPI | Value | Meaning |
| --- | ---: | --- |
| Stockout rate | 24.18% | Inventory ran out too often |
| Overcapacity rate | 34.79% | Storage was too often overfilled |
| Reactive ordering rate | 50.80% | Orders were triggered too late |

## Slide 3: Project Approach

- Load and normalize operational history from SQLite.
- Engineer forecast features from demand, weather, and inventory signals.
- Compare the Random Forest baseline against the fine-tuned Gradient Boosting planning model.
- Simulate 56-day inventory behavior using reorder logic, lead times, and safety stock.
- Expose results in an interactive Dash dashboard with scenario analysis.

## Slide 4: Solution Architecture

- Data source: SQLite operational records
- Forecasting: Random Forest baseline and fine-tuned Gradient Boosting model
- Planning layer: dynamic reorder points, safety stock, coverage, turnover, and scenario simulation
- Delivery layer: Dash app with Planner, Forecast, and Operations views

## Slide 5: Model Performance Summary

Fine-tuned Gradient Boosting model improvement versus the Random Forest baseline across 30 sites:

- Better MAPE on 27/30 sites
- Better RMSE on 26/30 sites
- Average MAPE improved from 34.86 to 14.93
- Average RMSE improved from 11.45 to 4.91
- Average percentage improvement:
  - MAPE: 39.12%
  - RMSE: 28.34%

![Model comparison chart](presentation_model_comparison.png)

| Model | Average MAPE | Average RMSE | Notes |
| --- | ---: | ---: | --- |
| Random Forest baseline | 34.86% | 11.45 tonnes | Baseline planning reference |
| Gradient Boosting | 14.93% | 4.91 tonnes | Feature-engineered delivered model |
| Improvement | 39.12% | 28.34% | Relative uplift versus baseline |

![Top site-level uplift](presentation_site_uplift_top10.png)

## Slide 6: Inventory Planning Capability

The delivered planning workflow includes:
- 56-day forward inventory projection
- Dynamic reorder point calculation using forecast variability and lead time
- Safety stock estimation per site and scenario
- Scenario planning:
  - baseline
  - demand_90
  - demand_110
  - delayed_deliveries

![Planning summary table](presentation_summary_table.png)

## Slide 7: Dashboard Demonstration

Planner view:
- inventory projection line chart
- reorder recommendations
- utilization gauge
- alert banner

Forecast view:
- forecast demand trend
- forecast summary
- turnover and coverage KPIs

Operations view:
- reorder point and safety stock visualization
- threshold breach markers
- site status table and drill-down

## Slide 8: Business Impact Summary

Operational benefits expected from the solution:
- lower forecast error improves planning confidence
- earlier risk detection reduces emergency replenishment
- dynamic reorder logic improves consistency across sites
- scenario analysis supports proactive decision-making under demand and delivery stress

## Slide 9: ROI and 12-Month Outlook

Illustrative ROI framework:
- savings from fewer emergency deliveries
- savings from lower avoidable stockouts
- working-capital improvement from better inventory positioning
- planner time saved through centralized dashboard workflow

12-month outlook:
- stabilize dashboard adoption
- monitor model performance monthly
- retrain periodically using latest operational data
- expand features to exception tracking and delivery scheduling integration

## Slide 10: Handover and Next Steps

Delivered package:
- codebase
- models
- reports
- architecture and deployment documentation
- user guide and training notes
- feedback / enhancement backlog

Recommended next steps:
- formal retraining schedule
- production deployment hardening
- richer business cost model
- stakeholder adoption review after first operating cycle
