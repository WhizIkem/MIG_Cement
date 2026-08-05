# pip install pandas plotly dash

from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Load the dummy sales dataset
df = pd.read_csv('../data/raw/dummy_sales_dataset.csv')

# Convert the 'date' column to datetime format for proper handling
df['date'] = pd.to_datetime(df['date'])

# Calculate key metrics for the dashboard
total_sales = f"${df['sales'].sum():,.0f}"
total_orders = len(df)
average_sales = f"${df['sales'].mean():,.2f}"

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the dashboard
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

# Define the callback to update the metrics dynamically if needed
@app.callback(
  Output('total-sales', 'children'),
  Output('total-orders', 'children'),
  Output('average-sales', 'children'),
)

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)