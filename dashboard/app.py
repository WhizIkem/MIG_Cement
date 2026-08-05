from MIG_dash_app import app, server

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)