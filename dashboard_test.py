from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

df = pd.read_csv('AAPL.csv')

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='AAPL Prices', style={'textAlign':'center'}),
    dcc.Dropdown(options=[{'label':x, 'value':x} for x in df.time_frame.unique()], value='Intraday', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.time_frame==value]
    return {
        'data': [go.Candlestick(x=dff['date'],
                                 open=dff['1. open'],
                                 high=dff['2. high'],
                                 low=dff['3. low'],
                                 close=dff['4. close'])],
        'layout': go.Layout(title=f'{value} Prices')
    }
if __name__ == '__main__':
    app.run_server(debug=True)
