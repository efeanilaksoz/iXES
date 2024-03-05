import dash
from dash import html, dcc, callback, Input, Output, State, callback_context as ctx
import dash_daq as daq
import os

dash.register_page(__name__)

# Define the layout for the app
layout = html.Div(
    style={
        'backgroundImage': 'url(https://raw.githubusercontent.com/efeanilaksoz/iXES/main/ride_background.png)',
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
                'gap': '20px',
                'padding': '20px' # Add some padding to the buttons
            },
            children=[html.Button('START', id='button-start', n_clicks=0, style={'fontSize': '20px', 'height': '80px', 'width': '140px', 'backgroundColor': 'black', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}),
                      html.Button('STOP',  id='button-stop', n_clicks=0, style={'fontSize': '20px', 'height': '80px', 'width': '140px', 'backgroundColor': 'red', 'color': 'white', 'opacity': '0.8', 'border-radius': '20%'}),
            ]),
        html.Div(
            style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(4, 1fr)',
                'gap': '5px',
                'padding': '15px' # Add some padding to the buttons
            },
            children=[daq.LEDDisplay(id='led_HR', label='HR', labelPosition='bottom', backgroundColor = "black" ,value='00', color='red', size=35),
                      daq.LEDDisplay(id='led_RPM', label='RPM', labelPosition='bottom', backgroundColor = "black", value='00', color='red', size=35),
                      daq.LEDDisplay(id='led_Speed', label='Speed',labelPosition='bottom', backgroundColor = "black" ,value='00', color='red', size=35),
                      daq.LEDDisplay(id='led_Distance', label='Distance', labelPosition='bottom', backgroundColor = "black", value='00', color='red', size=35),
            ]
        ),
        html.H1('ARM FORCE', style={'fontSize': '20', 'color': 'black', 'opacity': '0.8', 'padding': '15px'}),
        daq.Slider(id='slider_arm', min=-100, max=100, value=1, handleLabel={"showCurrentValue": True, "label": "ARMS"}, step=1),
        html.H1('LEG FORCE', style={'fontSize': '20', 'color': 'black', 'opacity': '0.8', 'padding': '15px'}),
        daq.Slider(id='slider_leg',min=-100, max=100, value=-1, handleLabel={"showCurrentValue": True, "label": "LEGS"}, step=1),
    ]
)

@callback(
    Output('led_HR', 'color'),
    Output('led_RPM', 'color'),
    Output('led_Speed', 'color'),
    Output('led_Distance', 'color'),
    Output('button-start', 'children'),
    Output('slider_arm', 'value'),
    Output('slider_leg', 'value'),
    Input('button-start', 'n_clicks'),
)
def start_recording(n_clicks):
    if ctx.triggered_id == 'button-start' and n_clicks % 2 == 1:
        return ["white", "white", "white", "white", "PAUSE", 0, 0]
    else:
        return ["red", "red", "red", "red", "START", -100, -100]    