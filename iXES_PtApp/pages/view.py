import dash
from dash import html, dcc, callback, Input, Output


dash.register_page(__name__)

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
                html.H1('Select User:', style={'textAlign': 'right', 'color': 'white', 'textShadow': '2px 2px black'}), 
                dcc.Dropdown(['Sebastian Tobler', 'User 2', 'User 3'], id='user_name', style={'width': '160px'}),
                html.H1('Select Ride Data:', style={'textAlign': 'right', 'color': 'white', 'textShadow': '2px 2px black'}), 
                dcc.Dropdown(['05.03.2024 - Morning Ride', '29.02.2024 - Afternoon Ride', '27.02.2024 - Afternoon Ride'], id='previous_rides', style={'width': '200px'}),
                dcc.Link(html.Button('VIEW DETAILS', style={'fontSize': '20px', 'height': '80px', 'width': '120px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}), href='/view', refresh=True),
                dcc.Link(html.Button('CANCEL', style={'fontSize': '20px', 'height': '80px', 'width': '120px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}), href='/view', refresh=True),
            ],
        )
    ]
)


