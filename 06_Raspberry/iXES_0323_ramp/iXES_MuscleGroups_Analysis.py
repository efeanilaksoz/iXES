# %%
# from cmath import pi
from re import template
from statistics import mean
from tkinter import E
from turtle import title
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy
import os
import plotly.io as pio
import matplotlib

import dash
from dash import dcc
from dash import html

#from signal import signal, SIGPIPE, SIG_DFL
#signal(SIGPIPE, SIG_DFL)

# Control variables for plots
pio.templates.default = "plotly_dark" #['ggplot2', 'seaborn', 'simple_white', 'plotly', 'plotly_white', 'plotly_dark', 'presentation', 'xgridoff','ygridoff', 'gridon', 'none']
html_path =""

def add_to_dataframe(muscle, rpm, resistance, sensor):
    # muscle = "ns", "quads", "hams", "glutes", "tibialis", "calves", "ext", "flex"
    # rpm    = "30", "40", "50"
    # resistance = "R1", "R2", "R3"
    # sensor = "ll", "rl", "la", "ra"
    global html_path

    # define the path for the raw data
    path = os.path.dirname(os.path.abspath(__file__))
    html_path = path + "/2cloud/results.html"
    path = path + "/results/" + "binary_" + sensor + ".txt" 

    if os.path.exists(path):
        print("Path exists, adding to the data frame")
        df = pd.read_csv(path, sep="\t", header=7)
        print(path)

        rpm_str = str(round(df["AngularVelocity"].mean()*9.549297))
        Ftan_mean_str = str(round(df["Ftan"].mean()))
        sensor_str = path[-6:-4].upper()
        
        return [df, rpm_str, Ftan_mean_str, sensor_str]
    else:
        print("Path does NOT exist, terminating")

def stimulation_range(muscle, sensor):
    # muscle = "ns", "quads", "hams", "glutes", "tibialis", "calves", "ext", "flex"
    global html_path

    Start_Quad = 310
    Stop_Quad = Start_Quad+100
    Start_calf = Start_Quad+40
    Stop_calf = Start_calf+210
    Start_Ham = Start_Quad+100
    Stop_Ham = Start_Ham+80
    Start_Glut = Start_Quad+30
    Stop_Glut = Start_Glut+125

    if muscle == "quads":
        stimx = [Start_Quad%360, Start_Quad%360 , Stop_Quad%360, Stop_Quad%360]
        fig = go.Figure(go.Scatter(x=stimx, y=[-90,-80,-80,-90], fill="toself", fillcolor="red", name="Q",
                        text=["","","","            QUADS"], textposition="top center", line_width=0, 
                        mode = 'lines+text', opacity=0.3, showlegend=False))

    if muscle == "hams":
        stimx = [Start_Ham%360, Start_Ham%360 , Stop_Ham%360, Stop_Ham%360]
        fig = go.Figure(go.Scatter(x=stimx, y=[-90,-80,-80,-90], fill="toself", fillcolor="red", name="H",
                        text=["","","","            HAMS"], textposition="top center", line_width=0, 
                        mode = 'lines+text', opacity=0.3, showlegend=False))
                    
    if muscle == "calves":
        stimx = [Start_calf%360, Start_calf%360 , Stop_calf%360, Stop_calf%360]
        fig = go.Figure(go.Scatter(x=stimx, y=[-90,-80,-80,-90], fill="toself", fillcolor="red", name="H",
                        text=["","","","            CALVES"], textposition="top center", line_width=0, 
                        mode = 'lines+text', opacity=0.3, showlegend=False))

    if muscle == "glutes":
        stimx = [Start_Glut%360, Start_Glut%360 , Stop_Glut%360, Stop_Glut%360]
        fig = go.Figure(go.Scatter(x=stimx, y=[-90,-80,-80,-90], fill="toself", fillcolor="red", name="H",
                        text=["","","","            CALVES"], textposition="top center", line_width=0, 
                        mode = 'lines+text', opacity=0.3, showlegend=False))

    return fig

[df_la, df1_rpm, df1_Ftan_mean, df1_sensor] = add_to_dataframe("ns" , "40", "R3", "la")
[df_ra, df2_rpm, df2_Ftan_mean, df2_sensor] = add_to_dataframe("hams", "40", "R3", "ra")
[df_ll, df1_rpm, df1_Ftan_mean, df1_sensor] = add_to_dataframe("ns" , "40", "R3", "ll")
[df_rl, df2_rpm, df2_Ftan_mean, df2_sensor] = add_to_dataframe("hams", "40", "R3", "rl")

#fig_StimAngles = stimulation_range("hams", "ll")

df_la["Ftan"] =  df_la["Ftan"]*-1
df_ra["Ftan"] =  df_ra["Ftan"]*-1

#df_la["Ftan"] =  df_la["Ftan"] + df_ra["Ftan"]
#df_ll["Ftan"] =  df_ll["Ftan"] + df_rl["Ftan"]


fig_la = px.scatter(df_la, x="Timer", y="Ftan", opacity=0.1, color="Ftan",
                    #trendline="rolling", trendline_options=dict(window=5), 
                    trendline="lowess", trendline_options=dict(frac=0.05),
                    trendline_color_override="white",
                    labels={"Angle": "Angle (\u00B0)", "Ftan": "Tangential Force (N)"},
                    title= "Left ARM" + " | " + df1_rpm + "rpm" + " | " + df1_Ftan_mean + "N")

fig_ra = px.scatter(df_ra, x="Timer", y="Ftan", opacity=0.1, color="Ftan",
                    #trendline="rolling", trendline_options=dict(window=5), 
                    trendline="lowess", trendline_options=dict(frac=0.05), 
                    trendline_color_override="white", 
                    labels={"Angle": "Angle (\u00B0)", "Ftan": "Tangential Force (N)"},
                    title= "Right ARM" + " | " + df2_rpm + "rpm" + " | " + df2_Ftan_mean + "N")

fig_ll = px.scatter(df_ll, x="Timer", y="Ftan", opacity=0.1, color="Ftan",
                    #trendline="rolling", trendline_options=dict(window=5), 
                    trendline="lowess", trendline_options=dict(frac=0.05),
                    trendline_color_override="red",
                    labels={"Angle": "Angle (\u00B0)", "Ftan": "Tangential Force (N)"},
                    title= "Left LEG" + " | " + df1_rpm + "rpm" + " | " + df1_Ftan_mean + "N")

fig_rl = px.scatter(df_rl, x="Timer", y="Ftan", opacity=0.1, color="Ftan",
                    #trendline="rolling", trendline_options=dict(window=5), 
                    trendline="lowess", trendline_options=dict(frac=0.05), 
                    trendline_color_override="red", 
                    labels={"Angle": "Angle (\u00B0)", "Ftan": "Tangential Force (N)"},
                    title= "Right LEG" + " | " + df2_rpm + "rpm" + " | " + df2_Ftan_mean + "N")

fig_final = go.Figure(data = fig_la.data + fig_ra.data + fig_ll.data + fig_rl.data)

#fig_final = go.Figure(data = fig_la.data + fig_rl.data)
#fig_final.update_layout(hovermode='x unified')
#fig_final.add_trace(go.Scatter(x=df2["Angle"], y=df2["Ftan"], line_color='rgba(147,112,219,0.3)', fillcolor='yellow',opacity=0.1, fill='tonextx'))

#fig_final.show()
fig_final.write_html(html_path)

#https://plotly.com/python/hover-text-and-formatting/
# %%

app = dash.Dash()

colors = {
    'background': '#000000',
    'text': '#7FDBFF'
}

app.layout = html.Div(children=[
    html.H1(children='iXES | 21.02.2023'),
    html.Div(children='''5 Figures in total for arms and legs'''),
    dcc.Graph(figure=fig_la),
    dcc.Graph(figure=fig_ra),
    dcc.Graph(figure=fig_ll),
    dcc.Graph(figure=fig_rl),
    dcc.Graph(figure=fig_final),
    html.A(
        html.Button("Download as HTML"), 
        id="download",
        href="data:text/html;base64,",
        download="plotly_graph.html"
    )
])

app.run(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter
