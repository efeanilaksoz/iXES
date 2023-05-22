import dash
from dash import dcc, html
import dash_daq as daq
import webbrowser
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True)

if __name__ == '__main__':
	app.run_server(debug=True, host='0.0.0.0', port=8050)