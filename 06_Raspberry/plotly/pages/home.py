import dash
from dash import html, dcc
import dash_daq as daq

dash.register_page(__name__, path='/')

# Define the layout for the app
layout = html.Div(
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
        html.Div(
            style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(2, 2fr)',
                'gap': '50px',
                'padding': '50px' # Add some padding to the buttons
            },
            children=[
                dcc.Link(html.Button('USER', style={'fontSize': '20px', 'height': '80px', 'width': '120px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}), href='/user', refresh=True),
                dcc.Link(html.Button('RIDE', style={'fontSize': '20px', 'height': '80px', 'width': '120px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}), href='/ride', refresh=True),
                dcc.Link(html.Button('SET',  style={'fontSize': '20px', 'height': '80px', 'width': '120px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}), href='/set', refresh=True),
                dcc.Link(html.Button('VIEW', style={'fontSize': '20px', 'height': '80px', 'width': '120px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}), href='/view', refresh=True),
                dcc.Link(html.Button('SAVE', style={'fontSize': '20px', 'height': '80px', 'width': '120px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}), href='/save', refresh=True),
                dcc.Link(html.Button('HELP', style={'fontSize': '20px', 'height': '80px', 'width': '120px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}), href='/help', refresh=True)
            ]
        )
    ]
)