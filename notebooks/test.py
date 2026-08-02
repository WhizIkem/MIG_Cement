# pip install pandas plotly dash

from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv('../data/raw/dummy_sales_dataset.csv')

df['date'] = pd.to_datetime(df['date'])

total_sales = f"${df['sales'].sum():,.0f}"
total_orders = len(df)
average_sales = f"${df['sales'].mean():,.2f}"

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
      'Sales Analytics Dashboard',
      style={'textAlign': 'center'}
    ),

    html.Hr(),

    html.Div([
        html.Div([
            html.H3('Total Sales'),
            html.H2(total_sales)
        ]),
        html.Div([
            html.H3('Total Orders'),
            html.H2(total_orders)
        ]),
        html.Div([
            html.H3('Average Sales'),
            html.H2(average_sales)
        ])
    ], style={
            'display': 'flex', 
            'justify-content': 'space-around'
            }),
    
])

@app.callback(
  Output('total-sales', 'children'),
  Output('total-orders', 'children'),
  Output('average-sales', 'children'),
)

if __name__ == '__main__':
    app.run_server(debug=True)