# User Guide and Training Notes

## Intended Users

- operations planners
- inventory coordinators
- site operations leads
- business stakeholders reviewing scenario outcomes

## Dashboard Views

### Planner
Use this view to answer: what should we do next?

Features:
- inventory projection line chart
- reorder recommendation table
- utilization gauge
- alert banner for scenario risk

### Forecast
Use this view to answer: what demand should we expect?

Features:
- forecast demand trend
- lead-time demand context
- forecast demand summary table
- coverage and turnover KPIs

### Operations
Use this view to answer: where are the operational risks?

Features:
- dynamic reorder point visualization
- safety stock visualization
- threshold breach markers
- operations detail table
- cross-site status table with drill-down

## Main Controls

- Site selector: focus on a single site
- Scenario selector: switch among baseline, demand_90, demand_110, delayed_deliveries
- Date range picker: narrow the period under review
- Tabs: switch between Planner, Forecast, and Operations views

## How to Use the Dashboard

1. Start with the scenario selector
- baseline for normal planning
- demand_110 for stress testing higher demand
- delayed_deliveries for logistics disruption review

2. Review alert banner
- red means urgent risk
- yellow means caution
- green means no immediate threshold issue

3. Use Planner for action
- check projected inventory trend
- review upcoming reorder dates and quantities

4. Use Forecast for demand understanding
- review forecast magnitude and coverage behavior

5. Use Operations for risk management
- inspect reorder point versus actual inventory
- use the status table to identify risky sites
- click a status row to drill down to the selected site

## Training Walkthrough

### 15-minute session outline

1. Explain each scenario and when to use it
2. Show how alerts are triggered
3. Demonstrate site drill-down
4. Compare Planner, Forecast, and Operations views
5. Review how to interpret reorder recommendations

## Common Interpretation Guidance

- Reorder Trigger: inventory has crossed the planning threshold
- Coverage Days: estimated number of days the current inventory can support expected demand
- Inventory Turnover: relative measure of inventory movement efficiency across the selected scenario window
- Safety Stock: protection buffer driven by demand variability and lead time
- Baseline comparison: Random Forest baseline, with the feature-engineered Gradient Boosting model showing the uplift

## Troubleshooting for Users

- If a site shows no data, confirm scenario and date range selections
- If data looks stale, request a processed artifact refresh
- If scenario results seem unexpected, compare baseline versus stress scenarios before escalating
