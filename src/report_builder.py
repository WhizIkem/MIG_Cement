

# Report builder for MIG Cement KPI analysis
def build_kpi_report(kpi_summary, problem_sites, output_path="../reports/kpi_analysis.html"):
    total_sites = kpi_summary["site_id"].nunique()
    problem_sites_count = problem_sites["site_id"].nunique()

    avg_stockout = round(kpi_summary["end_of_day_stockout_pct"].mean(), 2)
    avg_pour_failure = round(kpi_summary["pour_readiness_failure_pct"].mean(), 2)
    avg_overcapacity = round(kpi_summary["overcapacity_pct"].mean(), 2)
    avg_waste_risk = round(kpi_summary["waste_risk_pct"].mean(), 2)
    avg_idle = round(kpi_summary["idle_pct"].mean(), 2)
    avg_pour_disrupt = round(kpi_summary["pour_disrupt_pct"].mean(), 2)

    top_sites = problem_sites["site_id"].head(5).tolist()
    top_sites_text = ", ".join(top_sites)

    html = f"""
<html>
<head>
    <title>MIG Cement KPI Analysis Report</title>
</head>
<body>

<h1>MIG Cement KPI Analysis Report</h1>

<h2>Business Impact Summary</h2>

<p>
The KPI analysis covers {total_sites} sites. Based on the composite problem score,
{problem_sites_count} sites were identified as problem sites.
</p>

<p>
Across all sites, average end-of-day stockout is {avg_stockout}%, average pour readiness
failure is {avg_pour_failure}%, average overcapacity is {avg_overcapacity}%, average
waste risk is {avg_waste_risk}%, average idle rate is {avg_idle}%, and average pour
disruption is {avg_pour_disrupt}%.
</p>

<p>
The top problem sites are: {top_sites_text}.
</p>

<h2>Problem Site Identification</h2>

<p>
Problem sites were identified using a composite problem score. Each site received one point
for each triggered risk indicator, including stockout, pour readiness failure, overcapacity,
waste risk, low inventory, reactive ordering, and pour disruption.
</p>

<h2>Problem Sites</h2>
{problem_sites.to_html(index=False)}

<h2>Site-Level KPI Scorecard</h2>
{kpi_summary.to_html(index=False)}

</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html)

    print("kpi_analysis.html created successfully.")