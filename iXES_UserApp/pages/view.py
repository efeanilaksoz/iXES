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
        )
    ]
)