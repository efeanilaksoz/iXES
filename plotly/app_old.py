import dash
from dash import dcc, html
import dash_daq as daq
import webbrowser
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Define the layout for the app
app.layout = html.Div(
    style={
        'backgroundImage': 'url(https://raw.githubusercontent.com/efeanilaksoz/iXES/main/ixes_background.png)',
        #'backgroundImage': 'url(https://i.pinimg.com/564x/b1/3d/12/b13d120d8dafddf1d79c6318dd7ebbc5.jpg)',
        'backgroundRepeat': 'no-repeat',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center',
        'height': '100vh', 
    },
    children=[
        html.H1(
            children='iXES',
            style={
                'color': 'white', # Set text color to white
                'textAlign': 'center',
                'padd': '80px',
                'fontFamily': 'Helvetica',
                'fontSize': 40,
                'fontWeight': 'bold',
                'textShadow': '2px 2px black',
                'opacity': '0.4'
            }
        ),
        html.Div(
            style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(2, 2fr)',
                'gap': '50px',
                'padding': '50px' # Add some padding to the buttons
            },
            children=[
                html.Button('ACCOUNT', id='btn-acco', n_clicks=0, style={'fontSize': '20px', 'height': '80px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}),
                html.Button('RIDE',    id='btn-ride', n_clicks=0, style={'fontSize': '20px', 'height': '80px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}),
                html.Button('SET',     id='btn-set',  n_clicks=0, style={'fontSize': '20px', 'height': '80px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}),
                html.Button('VIEW',    id='btn-view', n_clicks=0, style={'fontSize': '20px', 'height': '80px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}),
                html.Button('SAVE',    id='btn-save', n_clicks=0, style={'fontSize': '20px', 'height': '80px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}),
                html.Button('HELP',    id='btn-help', n_clicks=0, style={'fontSize': '20px', 'height': '80px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}),
                daq.LEDDisplay(id='led_HR', label='Heart Rate',labelPosition='bottom', backgroundColor = "black", value='80', color='blue', size=60),
                daq.LEDDisplay(id='led_Cadence', label='Cadence', labelPosition='bottom', backgroundColor = "black", value='20', color='blue', size=60),
            ]
        )
    ]
)

if __name__ == '__main__':
    #webbrowser.open('http://0.0.0.0:8050/')
    app.run_server(debug=True, host='0.0.0.0', port=8050)

