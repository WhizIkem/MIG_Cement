# import libraries
import pandas as pd
import dash
from dash import dcc, html, dash_table, callback, Input, Output, State, no_update
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import warnings
from utils import (
    filter_results,
    format_scenario_label,
    get_date_bounds,
    load_kpi_summary,
    load_results_df,
)
warnings.filterwarnings("ignore")

# Load the necessary data
kpi_summary = load_kpi_summary('../data/processed/MIG_kpi_summary.csv')
results_df = load_results_df('../data/processed/cement_forecast_results.parquet')

# Ensure correct data types for date columns
scenario_options = sorted(results_df['scenario'].dropna().unique())
default_scenario = 'baseline' if 'baseline' in scenario_options else scenario_options[0]
min_date, max_date = get_date_bounds(results_df)

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "MIG Cement Operational Planning Dashboard"
app.config.suppress_callback_exceptions = True
server = app.server

# Custom CSS for white theme with glass-morphism
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                font-family: 'Inter', sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #f0f4f8 0%, #e8edf3 50%, #dce4ed 100%);
                min-height: 100vh;
                margin: 0;
                padding: 0;
            }
            
            .main-container {
                min-height: 100vh;
                padding: 20px;
                background: rgba(255, 255, 255, 0.4);
                backdrop-filter: blur(10px);
            }
            
            .glass-card {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(21, 99, 116, 0.08);
                transition: all 0.3s ease;
                overflow: hidden;
                position: relative;
            }
            
            .glass-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, transparent 100%);
                pointer-events: none;
            }
            
            .glass-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 40px rgba(21, 99, 116, 0.15);
                border-color: rgba(21, 99, 116, 0.2);
            }
            
            .kpi-card {
                background: rgba(255, 255, 255, 0.75);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.9);
                border-radius: 16px;
                padding: 20px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow: 0 4px 16px rgba(21, 99, 116, 0.06);
            }
            
            .kpi-card::after {
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle, rgba(21, 99, 116, 0.03) 0%, transparent 70%);
                pointer-events: none;
            }
            
            .kpi-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(21, 99, 116, 0.12);
                border-color: rgba(21, 99, 116, 0.2);
            }
            
            .kpi-value {
                font-size: 28px;
                font-weight: 700;
                color: #1a2a3a;
                margin: 4px 0;
                letter-spacing: -0.5px;
            }
            
            .kpi-label {
                font-size: 13px;
                font-weight: 500;
                color: #5a6a7a;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .kpi-accent {
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: linear-gradient(180deg, #156374, #1a8a9e);
                border-radius: 4px 0 0 4px;
            }
            
            .title-primary {
                color: #1a2a3a;
                font-weight: 700;
                font-size: 2.2rem;
                letter-spacing: -1px;
            }
            
            .title-accent {
                color: #156374;
            }
            
            .subtitle {
                color: #5a6a7a;
                font-weight: 300;
                font-size: 16px;
            }
            
            .dropdown-container {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 12px;
                padding: 12px 16px;
                box-shadow: 0 4px 16px rgba(21, 99, 116, 0.06);
                position: relative;
                z-index: 1000;
            }
            
            .dropdown-container label {
                color: #2a3a4a;
                font-weight: 500;
                font-size: 14px;
                letter-spacing: 0.3px;
            }
            
            /* Fix for dropdown z-index */
            .Select {
                position: relative;
                z-index: 1000;
            }
            
            .Select-control {
                background: rgba(255, 255, 255, 0.8) !important;
                border: 1px solid rgba(21, 99, 116, 0.15) !important;
                border-radius: 8px !important;
                color: #1a2a3a !important;
                box-shadow: 0 2px 8px rgba(21, 99, 116, 0.04);
                position: relative;
                z-index: 1000;
            }
            
            .Select-control:hover {
                border-color: #156374 !important;
            }
            
            .Select-menu-outer {
                background: #ffffff !important;
                border: 1px solid rgba(21, 99, 116, 0.1) !important;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 24px rgba(21, 99, 116, 0.15);
                z-index: 9999 !important;
                position: absolute !important;
                max-height: 300px !important;
                overflow-y: auto !important;
            }
            
            .Select-menu {
                max-height: 280px !important;
                overflow-y: auto !important;
            }
            
            .Select-option {
                color: #1a2a3a !important;
                background: transparent !important;
                padding: 8px 12px !important;
                cursor: pointer !important;
            }
            
            .Select-option.is-focused {
                background: rgba(21, 99, 116, 0.08) !important;
                color: #156374 !important;
            }
            
            .Select-option.is-selected {
                background: rgba(21, 99, 116, 0.12) !important;
                color: #156374 !important;
            }
            
            .Select-value-label {
                color: #1a2a3a !important;
            }
            
            .Select-placeholder {
                color: #8a9aaa !important;
            }
            
            .Select-clear-zone, .Select-arrow-zone {
                color: #5a6a7a !important;
            }
            
            /* Fix for dropdown in modal/popup contexts */
            .is-open .Select-menu-outer {
                z-index: 9999 !important;
            }
            
            /* Ensure dropdown appears above all content */
            .Select.is-open {
                z-index: 9999 !important;
            }
            
            .chart-container {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 16px;
                padding: 20px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 16px rgba(21, 99, 116, 0.06);
                position: relative;
                z-index: 1;
            }
            
            .chart-container:hover {
                border-color: rgba(21, 99, 116, 0.2);
                box-shadow: 0 8px 32px rgba(21, 99, 116, 0.1);
            }
            
            .table-container {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 16px;
                padding: 20px;
                max-height: 450px;
                overflow-y: auto;
                box-shadow: 0 4px 16px rgba(21, 99, 116, 0.06);
                position: relative;
                z-index: 1;
            }
            
            .table-container::-webkit-scrollbar {
                width: 8px;
            }
            
            .table-container::-webkit-scrollbar-track {
                background: rgba(21, 99, 116, 0.05);
                border-radius: 4px;
            }
            
            .table-container::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, #156374, #1a8a9e);
                border-radius: 4px;
            }
            
            .table-container::-webkit-scrollbar-thumb:hover {
                background: #156374;
            }
            
            .section-title {
                color: #1a2a3a;
                font-weight: 600;
                font-size: 1.1rem;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .section-title::after {
                content: '';
                flex: 1;
                height: 2px;
                background: linear-gradient(90deg, rgba(21, 99, 116, 0.2), transparent);
            }
            
            .dash-table-container {
                background: transparent !important;
            }
            
            .dash-spreadsheet-container {
                background: transparent !important;
            }
            
            .dash-spreadsheet {
                background: transparent !important;
                color: #1a2a3a !important;
            }
            
            .dash-spreadsheet td {
                color: #2a3a4a !important;
                background: transparent !important;
                border-bottom: 1px solid rgba(21, 99, 116, 0.06) !important;
            }
            
            .dash-spreadsheet th {
                color: #1a2a3a !important;
                background: rgba(21, 99, 116, 0.06) !important;
                border-bottom: 2px solid rgba(21, 99, 116, 0.15) !important;
                font-weight: 600 !important;
            }
            
            .dash-spreadsheet tr:hover td {
                background: rgba(21, 99, 116, 0.04) !important;
            }
            
            .dash-spreadsheet tr:nth-child(even) td {
                background: rgba(21, 99, 116, 0.02) !important;
            }
            
            .section-spacing {
                margin-top: 24px;
            }
            
            @media (max-width: 768px) {
                .kpi-value {
                    font-size: 22px;
                }
                .title-primary {
                    font-size: 1.8rem;
                }
                .kpi-card {
                    height: 110px;
                    padding: 16px;
                }
                .Select-menu-outer {
                    max-width: 90vw !important;
                }
            }
            
            .status-badge {
                display: inline-block;
                padding: 3px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }
            
            .badge-success { background: rgba(21, 99, 116, 0.1); color: #156374; }
            .badge-warning { background: rgba(255, 193, 7, 0.15); color: #856404; }
            .badge-danger { background: rgba(220, 53, 69, 0.1); color: #721c24; }
            
            .glass-divider {
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(21, 99, 116, 0.1), transparent);
                margin: 20px 0;
            }
            
            /* Loading spinner */
            .loading-spinner {
                border: 3px solid rgba(21, 99, 116, 0.1);
                border-top: 3px solid #156374;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Ensure dropdown container has proper z-index context */
            .row:first-child {
                position: relative;
                z-index: 100;
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            {%app_entry%}
        </div>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


def build_kpi_card(value, label, accent_background=None):
    accent_style = {'background': accent_background} if accent_background else None
    return dbc.Col(
        html.Div([
            html.Div(className="kpi-accent", style=accent_style),
            html.Div(value, className="kpi-value"),
            html.Div(label, className="kpi-label")
        ], className="kpi-card"),
        width=6,
        md=3
    )


def build_empty_view(site_id, scenario):
    return html.Div([
        html.Div([
            html.Div("No data available for current filters", className="section-title"),
            html.P(
                f"No records found for {site_id} in {format_scenario_label(scenario)} within the selected date range.",
                className="subtitle"
            )
        ], className="chart-container")
    ])


def classify_inventory_status(sim_inventory, reorder_point, coverage_days):
    if pd.isna(sim_inventory) or pd.isna(reorder_point):
        return "Unknown"
    if sim_inventory < reorder_point:
        return "Urgent"
    if pd.notna(coverage_days) and coverage_days <= 3:
        return "Caution"
    return "OK"


def build_inventory_status_snapshot(results_df, scenario, start_date, end_date, kpi_summary):
    scenario_df = results_df[results_df["scenario"] == scenario].copy()
    if start_date is not None:
        scenario_df = scenario_df[scenario_df["date"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        scenario_df = scenario_df[scenario_df["date"] <= pd.to_datetime(end_date)]

    if scenario_df.empty:
        return pd.DataFrame(columns=[
            "site_id", "current_stock", "coverage_days", "reorder_flag",
            "dynamic_reorder_point", "status", "utilization_pct"
        ])

    latest_rows = (
        scenario_df.sort_values(["site_id", "date"])
        .groupby("site_id", as_index=False)
        .tail(1)
        .copy()
    )
    latest_rows = latest_rows.merge(
        kpi_summary[["site_id", "silo_capacity"]],
        on="site_id",
        how="left"
    )
    latest_rows["current_stock"] = latest_rows["sim_inventory"].round(2)
    latest_rows["coverage_days"] = latest_rows["coverage_days"].round(2)
    latest_rows["utilization_pct"] = (
        100 * latest_rows["sim_inventory"] / latest_rows["silo_capacity"]
    ).round(1)
    latest_rows["status"] = latest_rows.apply(
        lambda row: classify_inventory_status(
            row.get("sim_inventory"),
            row.get("dynamic_reorder_point"),
            row.get("coverage_days"),
        ),
        axis=1,
    )
    latest_rows["reorder_flag"] = latest_rows["reorder_flag"].map(lambda value: "Yes" if bool(value) else "No")

    return latest_rows[[
        "site_id", "current_stock", "coverage_days", "reorder_flag",
        "dynamic_reorder_point", "status", "utilization_pct"
    ]].sort_values(["status", "site_id"], ascending=[True, True])


def build_status_alert(status_df):
    if status_df.empty:
        return dbc.Alert("No scenario data available for the selected date range.", color="secondary", className="mb-0")

    urgent_sites = status_df[status_df["status"] == "Urgent"]["site_id"].tolist()
    caution_sites = status_df[status_df["status"] == "Caution"]["site_id"].tolist()

    if urgent_sites:
        return dbc.Alert(
            [
                html.Strong("Imminent stockout alert: "),
                f"{len(urgent_sites)} site(s) below reorder point: {', '.join(urgent_sites[:6])}",
            ],
            color="danger",
            className="mb-0",
        )

    if caution_sites:
        return dbc.Alert(
            [
                html.Strong("Caution: "),
                f"{len(caution_sites)} site(s) have low coverage days: {', '.join(caution_sites[:6])}",
            ],
            color="warning",
            className="mb-0",
        )

    return dbc.Alert("All sites are above reorder point for the selected scenario and date range.", color="success", className="mb-0")


def build_status_table(status_df, selected_site):
    status_styles = [
        {
            'if': {'filter_query': '{status} = "OK"', 'column_id': 'status'},
            'backgroundColor': 'rgba(21, 99, 116, 0.12)',
            'color': '#156374',
            'fontWeight': '600',
        },
        {
            'if': {'filter_query': '{status} = "Caution"', 'column_id': 'status'},
            'backgroundColor': 'rgba(255, 193, 7, 0.18)',
            'color': '#856404',
            'fontWeight': '600',
        },
        {
            'if': {'filter_query': '{status} = "Urgent"', 'column_id': 'status'},
            'backgroundColor': 'rgba(220, 53, 69, 0.18)',
            'color': '#721c24',
            'fontWeight': '600',
        },
        {
            'if': {'filter_query': f'{{site_id}} = "{selected_site}"'},
            'border': '1px solid rgba(21, 99, 116, 0.35)',
        },
    ]

    return html.Div([
        html.Div("Current Inventory Status", className="section-title"),
        html.Div(
            dash_table.DataTable(
                columns=[
                    {"name": "Site", "id": "site_id"},
                    {"name": "Current Stock (t)", "id": "current_stock"},
                    {"name": "Days Coverage", "id": "coverage_days"},
                    {"name": "Reorder Flag", "id": "reorder_flag"},
                    {"name": "Status", "id": "status"},
                ],
                data=status_df.to_dict("records"),
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "center", "padding": "12px 16px", "fontSize": "14px", "color": "#2a3a4a", "background": "transparent", "border": "none"},
                style_header={"backgroundColor": "rgba(21, 99, 116, 0.06)", "fontWeight": "600", "color": "#1a2a3a", "borderBottom": "2px solid rgba(21, 99, 116, 0.15)", "padding": "12px 16px"},
                page_size=8,
                cell_selectable=False,
                style_data_conditional=status_styles,
            ),
            className="table-container"
        )
    ], className="mb-4")


def build_utilization_gauge(current_inventory, silo_capacity, site_id):
    utilization_pct = 0 if not silo_capacity else max(min((current_inventory / silo_capacity) * 100, 100), 0)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=utilization_pct,
        number={"suffix": "%", "font": {"size": 32, "color": "#1a2a3a"}},
        title={"text": f"{site_id} Silo Utilization", "font": {"size": 15, "color": "#2a3a4a"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#5a6a7a"},
            "bar": {"color": "#156374"},
            "steps": [
                {"range": [0, 60], "color": "rgba(21, 99, 116, 0.15)"},
                {"range": [60, 85], "color": "rgba(255, 193, 7, 0.18)"},
                {"range": [85, 100], "color": "rgba(220, 53, 69, 0.18)"},
            ],
            "threshold": {
                "line": {"color": "#dc3545", "width": 4},
                "thickness": 0.75,
                "value": 85,
            },
        },
    ))
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        margin=dict(l=20, r=20, t=60, b=20),
        height=320,
    )
    return fig


def build_planner_view(site_df, site_id, scenario, silo_capacity, status_df):
    total_forecast = site_df["forecasted_consumption"].sum()
    total_reorders = int(site_df["reorder_flag"].sum())
    avg_inventory = site_df["sim_inventory"].mean()
    utilization = (avg_inventory / silo_capacity) * 100 if silo_capacity else 0
    current_inventory = site_df["sim_inventory"].iloc[-1]

    kpi_cards = dbc.Row([
        build_kpi_card(f"{total_forecast:,.0f}", "Total Forecasted Consumption"),
        build_kpi_card(f"{total_reorders}", "Planned Reorders", "linear-gradient(180deg, #1a8a9e, #156374)"),
        build_kpi_card(f"{avg_inventory:,.0f}", "Average Inventory (t)", "linear-gradient(180deg, #2a9aae, #1a7a8e)"),
        build_kpi_card(f"{utilization:.1f}%", "Capacity Utilization", "linear-gradient(180deg, #3aaaaa, #2a8a9e)"),
    ], className="mb-4 g-3", style={'position': 'relative', 'zIndex': 1})

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=site_df["date"],
        y=site_df["sim_inventory"],
        mode="lines",
        name="Inventory Level",
        line=dict(color="#156374", width=2.5),
        fill='tozeroy',
        fillcolor='rgba(21, 99, 116, 0.1)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Inventory: %{y:,.0f} t<extra></extra>'
    ))
    fig.add_hline(
        y=silo_capacity,
        line_dash="dash",
        line_color="#dc3545",
        line_width=1.5,
        annotation_text=f"Capacity: {silo_capacity:,.0f} t",
        annotation_position="top right",
        annotation_font=dict(color="#dc3545", size=11)
    )
    fig.add_trace(go.Bar(
        x=site_df["date"],
        y=site_df["forecasted_consumption"],
        name="Forecasted Demand",
        yaxis="y2",
        opacity=0.4,
        marker_color='rgba(255, 193, 7, 0.5)',
        marker_line_color='rgba(255, 193, 7, 0.3)',
        marker_line_width=1,
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Demand: %{y:,.0f} t<extra></extra>'
    ))
    reorder_points = site_df[site_df["reorder_flag"] == True]
    fig.add_trace(go.Scatter(
        x=reorder_points["date"],
        y=reorder_points["sim_inventory"],
        mode="markers",
        name="Reorder Trigger",
        marker=dict(color="#dc3545", size=10, symbol="diamond", line=dict(color="white", width=1.5)),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Reorder Trigger<br>Inventory: %{y:,.0f} t<extra></extra>'
    ))
    fig.update_layout(
        template="plotly_white",
        title=dict(
            text=f"<b>{site_id}</b> - Inventory and Demand Forecast ({format_scenario_label(scenario)})",
            font=dict(size=16, color="#1a2a3a"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(title=dict(text="Date", font=dict(color="#5a6a7a", size=12)), gridcolor="rgba(21, 99, 116, 0.06)", tickfont=dict(color="#5a6a7a"), zeroline=False),
        yaxis=dict(title=dict(text="Inventory (t)", font=dict(color="#5a6a7a", size=12)), gridcolor="rgba(21, 99, 116, 0.06)", tickfont=dict(color="#5a6a7a"), zeroline=False),
        yaxis2=dict(title=dict(text="Demand (t)", font=dict(color="#5a6a7a", size=12)), overlaying="y", side="right", gridcolor="rgba(21, 99, 116, 0.06)", tickfont=dict(color="#5a6a7a"), zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#2a3a4a", size=11), bgcolor="rgba(255,255,255,0.8)", bordercolor="rgba(21, 99, 116, 0.1)", borderwidth=1),
        hovermode="x unified",
        plot_bgcolor="rgba(255,255,255,0.3)",
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(l=60, r=60, t=80, b=50),
        height=450,
        font=dict(color="#2a3a4a")
    )

    reorder_data = site_df[site_df["reorder_flag"] == True][[
        "date", "sim_inventory", "recommended_delivery_date",
        "recommended_delivery_quantity", "buffer_applied"
    ]].copy()
    reorder_data['date'] = reorder_data['date'].dt.strftime('%Y-%m-%d')

    reorder_table = dash_table.DataTable(
        columns=[
            {"name": "Date", "id": "date"},
            {"name": "Inventory (t)", "id": "sim_inventory"},
            {"name": "Delivery Date", "id": "recommended_delivery_date"},
            {"name": "Quantity (t)", "id": "recommended_delivery_quantity"},
            {"name": "Rain Buffer", "id": "buffer_applied"}
        ],
        data=reorder_data.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "padding": "12px 16px", "fontSize": "14px", "color": "#2a3a4a", "background": "transparent", "border": "none"},
        style_header={"backgroundColor": "rgba(21, 99, 116, 0.06)", "fontWeight": "600", "color": "#1a2a3a", "borderBottom": "2px solid rgba(21, 99, 116, 0.15)", "padding": "12px 16px"},
        page_size=5,
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(21, 99, 116, 0.02)'},
            {'if': {'row_index': 'even'}, 'backgroundColor': 'transparent'}
        ]
    )

    return html.Div([
        html.Div(build_status_alert(status_df), className="mb-4"),
        kpi_cards,
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div("Inventory and Demand Analysis", className="section-title"),
                    dcc.Graph(figure=fig, config={'displayModeBar': False})
                ], className="chart-container")
            ], width=12, lg=8),
            dbc.Col([
                html.Div([
                    html.Div("Current Utilization", className="section-title"),
                    dcc.Graph(figure=build_utilization_gauge(current_inventory, silo_capacity, site_id), config={'displayModeBar': False})
                ], className="chart-container")
            ], width=12, lg=4)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div("Upcoming Reorder Recommendations", className="section-title"),
                    html.Div(reorder_table, className="table-container")
                ])
            ], width=12)
        ])
    ])


def build_forecast_view(site_df, site_id, scenario):
    total_forecast = site_df["forecasted_consumption"].sum()
    avg_daily_forecast = site_df["forecasted_consumption"].mean()
    turnover = site_df["inventory_turnover"].iloc[0] if "inventory_turnover" in site_df.columns else 0
    coverage = site_df["scenario_coverage_days_mean"].iloc[0] if "scenario_coverage_days_mean" in site_df.columns else 0

    kpi_cards = dbc.Row([
        build_kpi_card(f"{total_forecast:,.0f}", "Total Forecast Demand"),
        build_kpi_card(f"{avg_daily_forecast:,.1f}", "Avg Daily Forecast", "linear-gradient(180deg, #1a8a9e, #156374)"),
        build_kpi_card(f"{turnover:.2f}", "Inventory Turnover", "linear-gradient(180deg, #2a9aae, #1a7a8e)"),
        build_kpi_card(f"{coverage:.1f}", "Avg Coverage Days", "linear-gradient(180deg, #3aaaaa, #2a8a9e)"),
    ], className="mb-4 g-3")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=site_df["date"],
        y=site_df["forecasted_consumption"],
        mode="lines+markers",
        name="Forecast Demand",
        line=dict(color="#156374", width=3),
        marker=dict(size=6, color="#156374"),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Forecast: %{y:,.1f} t<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=site_df["date"],
        y=site_df.get("lead_time_demand_mean", pd.Series(index=site_df.index, dtype=float)),
        name="Lead-Time Demand",
        opacity=0.25,
        marker_color='rgba(255, 193, 7, 0.5)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Lead-Time Demand: %{y:,.1f} t<extra></extra>'
    ))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"<b>{site_id}</b> - Forecast View ({format_scenario_label(scenario)})", x=0.5, xanchor="center", font=dict(size=16, color="#1a2a3a")),
        xaxis=dict(title=dict(text="Date", font=dict(color="#5a6a7a", size=12))),
        yaxis=dict(title=dict(text="Forecast Demand (t)", font=dict(color="#5a6a7a", size=12))),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(255,255,255,0.3)",
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(l=60, r=30, t=80, b=50),
        height=450,
        font=dict(color="#2a3a4a")
    )

    forecast_summary = site_df[["date", "forecasted_consumption", "coverage_days"]].copy()
    forecast_summary["date"] = forecast_summary["date"].dt.strftime('%Y-%m-%d')
    forecast_summary["forecasted_consumption"] = forecast_summary["forecasted_consumption"].round(2)
    forecast_summary["coverage_days"] = forecast_summary["coverage_days"].round(2)

    summary_table = dash_table.DataTable(
        columns=[
            {"name": "Date", "id": "date"},
            {"name": "Forecast Demand (t)", "id": "forecasted_consumption"},
            {"name": "Coverage Days", "id": "coverage_days"},
        ],
        data=forecast_summary.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "padding": "12px 16px", "fontSize": "14px", "color": "#2a3a4a", "background": "transparent", "border": "none"},
        style_header={"backgroundColor": "rgba(21, 99, 116, 0.06)", "fontWeight": "600", "color": "#1a2a3a", "borderBottom": "2px solid rgba(21, 99, 116, 0.15)", "padding": "12px 16px"},
        page_size=7,
    )

    return html.Div([
        kpi_cards,
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div("Forecast Demand Profile", className="section-title"),
                    dcc.Graph(figure=fig, config={'displayModeBar': False})
                ], className="chart-container")
            ], width=12)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div("Forecast Summary", className="section-title"),
                    html.Div(summary_table, className="table-container")
                ])
            ], width=12)
        ])
    ])


def build_operations_view(site_df, site_id, scenario, status_df):
    total_reorders = int(site_df["reorder_flag"].sum())
    avg_safety_stock = site_df["site_safety_stock_mean"].iloc[0] if "site_safety_stock_mean" in site_df.columns else 0
    p95_safety_stock = site_df["site_safety_stock_p95"].iloc[0] if "site_safety_stock_p95" in site_df.columns else 0
    avg_coverage = site_df["coverage_days"].mean() if "coverage_days" in site_df.columns else 0

    kpi_cards = dbc.Row([
        build_kpi_card(f"{total_reorders}", "Reorder Triggers"),
        build_kpi_card(f"{avg_safety_stock:,.1f}", "Avg Safety Stock", "linear-gradient(180deg, #1a8a9e, #156374)"),
        build_kpi_card(f"{p95_safety_stock:,.1f}", "P95 Safety Stock", "linear-gradient(180deg, #2a9aae, #1a7a8e)"),
        build_kpi_card(f"{avg_coverage:.1f}", "Avg Coverage Days", "linear-gradient(180deg, #3aaaaa, #2a8a9e)"),
    ], className="mb-4 g-3")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=site_df["date"],
        y=site_df["sim_inventory"],
        mode="lines",
        name="Inventory",
        line=dict(color="#156374", width=2.5),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Inventory: %{y:,.0f} t<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=site_df["date"],
        y=site_df.get("dynamic_reorder_point", pd.Series(index=site_df.index, dtype=float)),
        mode="lines",
        name="Dynamic Reorder Point",
        line=dict(color="#dc3545", width=2, dash="dash"),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Reorder Point: %{y:,.1f} t<extra></extra>'
    ))
    alert_points = site_df[site_df["sim_inventory"] < site_df["dynamic_reorder_point"]]
    fig.add_trace(go.Scatter(
        x=alert_points["date"],
        y=alert_points["sim_inventory"],
        mode="markers",
        name="Threshold Breach",
        marker=dict(color="#dc3545", size=11, symbol="x"),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Alert: Inventory below reorder point<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=site_df["date"],
        y=site_df.get("dynamic_safety_stock", pd.Series(index=site_df.index, dtype=float)),
        name="Safety Stock",
        opacity=0.3,
        marker_color='rgba(42, 154, 174, 0.45)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Safety Stock: %{y:,.1f} t<extra></extra>'
    ))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"<b>{site_id}</b> - Operations View ({format_scenario_label(scenario)})", x=0.5, xanchor="center", font=dict(size=16, color="#1a2a3a")),
        xaxis=dict(title=dict(text="Date", font=dict(color="#5a6a7a", size=12))),
        yaxis=dict(title=dict(text="Tonnes", font=dict(color="#5a6a7a", size=12))),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(255,255,255,0.3)",
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(l=60, r=30, t=80, b=50),
        height=450,
        font=dict(color="#2a3a4a")
    )

    operations_table_df = site_df[[
        "date", "sim_inventory", "dynamic_reorder_point",
        "dynamic_safety_stock", "recommended_delivery_date",
        "recommended_delivery_quantity"
    ]].copy()
    operations_table_df["date"] = operations_table_df["date"].dt.strftime('%Y-%m-%d')
    for column in ["sim_inventory", "dynamic_reorder_point", "dynamic_safety_stock", "recommended_delivery_quantity"]:
        operations_table_df[column] = operations_table_df[column].round(2)

    operations_table = dash_table.DataTable(
        columns=[
            {"name": "Date", "id": "date"},
            {"name": "Inventory (t)", "id": "sim_inventory"},
            {"name": "Reorder Point (t)", "id": "dynamic_reorder_point"},
            {"name": "Safety Stock (t)", "id": "dynamic_safety_stock"},
            {"name": "Delivery Date", "id": "recommended_delivery_date"},
            {"name": "Delivery Qty (t)", "id": "recommended_delivery_quantity"},
        ],
        data=operations_table_df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "padding": "12px 16px", "fontSize": "14px", "color": "#2a3a4a", "background": "transparent", "border": "none"},
        style_header={"backgroundColor": "rgba(21, 99, 116, 0.06)", "fontWeight": "600", "color": "#1a2a3a", "borderBottom": "2px solid rgba(21, 99, 116, 0.15)", "padding": "12px 16px"},
        page_size=7,
    )

    return html.Div([
        html.Div(build_status_alert(status_df), className="mb-4"),
        kpi_cards,
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div("Operational Risk and Reorder Control", className="section-title"),
                    dcc.Graph(figure=fig, config={'displayModeBar': False})
                ], className="chart-container")
            ], width=12)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div("Operations Detail", className="section-title"),
                    html.Div(operations_table, className="table-container")
                ])
            ], width=12)
        ])
    ])


def build_dashboard_view(view_name, site_df, site_id, scenario, silo_capacity, status_df):
    if view_name == "forecast":
        return build_forecast_view(site_df, site_id, scenario)
    if view_name == "operations":
        return build_operations_view(site_df, site_id, scenario, status_df)
    return build_planner_view(site_df, site_id, scenario, silo_capacity, status_df)

# =======================
# App Layout
# =======================
app.layout = dbc.Container([
    # Header
    html.Div([
        dcc.Tabs(
            id="view-tabs",
            value="planner",
            className="mb-3",
            children=[
                dcc.Tab(label="Planner", value="planner"),
                dcc.Tab(label="Forecast", value="forecast"),
                dcc.Tab(label="Operations", value="operations"),
            ]
        ),
        html.H1([
            "MIG Cement ",
            html.Span("Operational Planner", className="title-accent")
        ], className="title-primary text-center mb-2"),
        html.P("Real-time inventory optimization and demand forecasting", 
               className="subtitle text-center mb-4")
    ], className="mb-4"),
    
    # Site/Scenario Selection - With higher z-index context
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Select Site", className="mb-2 d-block"),
                dcc.Dropdown(
                    id="site-dropdown",
                    options=[{"label": s, "value": s} for s in sorted(results_df["site_id"].unique())],
                    value=sorted(results_df["site_id"].unique())[0],
                    clearable=False,
                    style={'position': 'relative', 'zIndex': 9999}
                )
            ], className="dropdown-container", style={'position': 'relative', 'zIndex': 9999})
        ], width=6, lg=4, xl=3)
        ,dbc.Col([
            html.Div([
                html.Label("Select Scenario", className="mb-2 d-block"),
                dcc.Dropdown(
                    id="scenario-dropdown",
                    options=[{"label": format_scenario_label(s), "value": s} for s in scenario_options],
                    value=default_scenario,
                    clearable=False,
                    style={'position': 'relative', 'zIndex': 9999}
                )
            ], className="dropdown-container", style={'position': 'relative', 'zIndex': 9999})
        ], width=6, lg=4, xl=3)
        ,dbc.Col([
            html.Div([
                html.Label("Select Date Range", className="mb-2 d-block"),
                dcc.DatePickerRange(
                    id="date-range-picker",
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=min_date,
                    end_date=max_date,
                    display_format="YYYY-MM-DD",
                    style={'width': '100%'}
                )
            ], className="dropdown-container", style={'position': 'relative', 'zIndex': 9999})
        ], width=12, lg=4, xl=4)
    ], className="mb-4", style={'position': 'relative', 'zIndex': 1000}),
    html.Div(
        id="status-table-wrapper",
        children=[
            html.Div("Current Inventory Status", className="section-title"),
            html.Div(
                dash_table.DataTable(
                    id="status-table",
                    columns=[
                        {"name": "Site", "id": "site_id"},
                        {"name": "Current Stock (t)", "id": "current_stock"},
                        {"name": "Days Coverage", "id": "coverage_days"},
                        {"name": "Reorder Flag", "id": "reorder_flag"},
                        {"name": "Status", "id": "status"},
                    ],
                    data=[],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "center", "padding": "12px 16px", "fontSize": "14px", "color": "#2a3a4a", "background": "transparent", "border": "none"},
                    style_header={"backgroundColor": "rgba(21, 99, 116, 0.06)", "fontWeight": "600", "color": "#1a2a3a", "borderBottom": "2px solid rgba(21, 99, 116, 0.15)", "padding": "12px 16px"},
                    page_size=8,
                    cell_selectable=True,
                ),
                className="table-container"
            )
        ],
        className="mb-4",
        style={'display': 'none'}
    ),
    html.Div(id="dashboard-view-content")
], fluid=True, className="px-4 py-3")

# =======================
# Callbacks
# =======================
@app.callback(
    [Output("dashboard-view-content", "children"),
     Output("status-table", "data"),
     Output("status-table", "style_data_conditional"),
     Output("status-table-wrapper", "style")],
    [Input("view-tabs", "value"),
     Input("site-dropdown", "value"),
     Input("scenario-dropdown", "value"),
     Input("date-range-picker", "start_date"),
     Input("date-range-picker", "end_date")]
)
def update_planner_dashboard(view_name, site_id, scenario, start_date, end_date):
    site_df = filter_results(results_df, site_id, scenario, start_date, end_date)
    status_df = build_inventory_status_snapshot(results_df, scenario, start_date, end_date, kpi_summary)
    status_styles = [
        {
            'if': {'filter_query': '{status} = "OK"', 'column_id': 'status'},
            'backgroundColor': 'rgba(21, 99, 116, 0.12)',
            'color': '#156374',
            'fontWeight': '600',
        },
        {
            'if': {'filter_query': '{status} = "Caution"', 'column_id': 'status'},
            'backgroundColor': 'rgba(255, 193, 7, 0.18)',
            'color': '#856404',
            'fontWeight': '600',
        },
        {
            'if': {'filter_query': '{status} = "Urgent"', 'column_id': 'status'},
            'backgroundColor': 'rgba(220, 53, 69, 0.18)',
            'color': '#721c24',
            'fontWeight': '600',
        },
        {
            'if': {'filter_query': f'{{site_id}} = "{site_id}"'},
            'border': '1px solid rgba(21, 99, 116, 0.35)',
        },
    ]
    status_table_style = {'display': 'block'} if view_name == 'operations' else {'display': 'none'}

    if site_df.empty:
        return build_empty_view(site_id, scenario), status_df.to_dict("records"), status_styles, status_table_style

    silo_capacity = kpi_summary[kpi_summary['site_id'] == site_id]['silo_capacity'].values[0]
    return (
        build_dashboard_view(view_name, site_df, site_id, scenario, silo_capacity, status_df),
        status_df.to_dict("records"),
        status_styles,
        status_table_style,
    )


@app.callback(
    Output("site-dropdown", "value"),
    Input("status-table", "active_cell"),
    State("status-table", "data"),
    State("site-dropdown", "value"),
    prevent_initial_call=True,
)
def drill_down_to_site(active_cell, table_data, current_site):
    if not active_cell or not table_data:
        return no_update

    row_index = active_cell.get("row")
    if row_index is None or row_index >= len(table_data):
        return no_update

    selected_site = table_data[row_index].get("site_id")
    if not selected_site or selected_site == current_site:
        return no_update

    return selected_site


# ==========================
# Run the app
# ==========================
if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8050)