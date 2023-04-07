import getter
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

TIME_FRAMES = None
with open("time_frames.json") as file:
    TIME_FRAMES = json.load(file)

time_frames_list = [i["time"] for i in TIME_FRAMES.values()]
app = Dash(__name__)

symbol = "AAPL"
df = getter.lookup(symbol)


app.layout = html.Div([
    html.H1(children=f'{symbol}', style={'textAlign':'center'}),
    dcc.Dropdown([time_frames_list], 'Intraday', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df.loc[df['time_frame'] == value]
    return px.line(dff, x='date', y='4. close')


if __name__ == '__main__':
    app.run_server(debug=True)