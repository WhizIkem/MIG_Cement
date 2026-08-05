# Business Impact and ROI Analysis

## Current Operational Pain Points

Based on the KPI artifacts produced in this project:

- Average end-of-day stockout rate: 24.18%
- Average overcapacity rate: 34.79%
- Average reactive ordering rate: 50.80%
- Problem sites identified: 30 out of 30 reviewed sites

These indicators suggest meaningful opportunity in three areas:
- reducing stockout-driven disruption
- improving inventory positioning
- reducing reactive planning effort

## Model Uplift

Comparison between the Random Forest baseline and the fine-tuned Gradient Boosting model across 30 sites:

- Better MAPE on 27 of 30 sites
- Better RMSE on 26 of 30 sites
- Average MAPE improved from 34.86 to 14.93
- Average RMSE improved from 11.45 to 4.91
- Average relative improvement:
  - MAPE: 39.12%
  - RMSE: 28.34%

## Business Impact Logic

The dashboard can create value through:

1. Avoided emergency replenishment
- Earlier warning on threshold breaches reduces premium transport / rush delivery decisions.

2. Fewer stockout disruptions
- Better demand visibility and reorder logic reduce the likelihood of cement unavailability during planned pours.

3. Lower avoidable overstock
- Dynamic reorder logic and scenario views reduce excess stock exposure and storage strain.

4. Planning efficiency
- A centralized dashboard reduces manual review time for planners and operations managers.

## ROI Framework

Annual Benefit = Emergency Delivery Savings + Stockout Avoidance Savings + Inventory Efficiency Savings + Labor Time Savings

ROI = (Annual Benefit - Annual Operating Cost) / Annual Operating Cost

## Suggested Assumption Inputs

- Average emergency deliveries avoided per month
- Cost premium per emergency delivery
- Average avoidable stockout events per month
- Average cost per stockout / disrupted pour event
- Average reduction in excess inventory per site
- Cost of capital or carrying cost rate
- Planner hours saved per week
- Average loaded labor rate per hour
- Annual platform/support cost

## Example 12-Month Scenario Template

| Category | Example Driver | Annualized Formula |
| --- | --- | --- |
| Emergency delivery savings | fewer urgent replenishments | avoided_emergencies x premium_cost x 12 |
| Stockout avoidance | fewer missed / delayed pours | avoided_stockouts x event_cost x 12 |
| Inventory efficiency | lower average avoidable stock | inventory_reduction x carrying_cost_rate |
| Labor efficiency | fewer manual planning hours | hours_saved_per_week x labor_rate x 52 |

## 12-Month Outlook

### 0-3 Months
- deploy dashboard to pilot users
- validate alert thresholds against field feedback
- establish weekly usage review

### 3-6 Months
- refine assumptions with real operational savings data
- compare scenario behavior against actual execution outcomes
- tune retraining cadence and safety stock policies

### 6-12 Months
- formalize ROI measurement
- integrate dashboard into standard planning routine
- evaluate ERP or dispatch integration for automation

## Recommendation

Use the current model and dashboard as an operational decision-support layer first, then quantify realized savings over the next operating cycle to build a business-backed ROI case for broader rollout.
