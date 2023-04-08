from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.graph_objs as go
import alpha_vantage.timeseries as ts
import pandas as pd
import os
import time


def get_data(symbol, time_frame, ts_function, interval=None, outputsize="compact"):
    api_key = 'K2J7THYH6AB78L5M'

    ts = ts.TimeSeries(api_key, output_format='pandas')

    if ts_function == ts.get_intraday:
        data, meta_data = ts_function(symbol=symbol, outputsize=outputsize, interval=interval)
    else:
        data, meta_data = ts_function(symbol=symbol)
    data.index = pd.to_datetime(data.index)
    data = data.sort_index(ascending=True)
    data['time_frame'] = time_frame
    return data

def lookup(symbol):
    print(f"LOOKUP {symbol}")
    try:
        intraday_data = get_data(symbol, "Intraday", ts.get_intraday, interval='60min')
        daily_data = get_data(symbol, "Daily adjusted",  ts.get_daily_adjusted)
        weekly_data = get_data(symbol, "Weekly adjusted",  ts.get_weekly_adjusted)
        monthly_data = get_data(symbol, "Monthly adjusted",  ts.get_monthly_adjusted)

        data = pd.concat([intraday_data, daily_data, weekly_data, monthly_data])

        data.to_csv(f'{symbol}.csv', index=True)
        return data
    except ValueError:
        print("Invalid symbol or API key")
        return pd.DataFrame()


symbol = 'AAPL'
file_path = f'{symbol}.csv'
if not os.path.isfile(file_path):
    lookup(symbol)
df = pd.read_csv(file_path)
clicks = 0

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='AAPL', style={'textAlign':'center'}),
    html.Div([
        dcc.Input(
            id='symbol-input',
            type='text',
            value='AAPL',
            style={'width': '30%', 'marginRight': '10px'}
        ),
        html.Button('Fetch Data', id='fetch-data-button', n_clicks=0),

        dcc.Dropdown(
            id='time-frame-dropdown',
            options=[{'label':x, 'value':x} for x in df.time_frame.unique()],
            value='Intraday'
        ),
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[{'label': 'Candlestick', 'value': 'candlestick'},
                     {'label': 'Line', 'value': 'line'}],
            value='candlestick'
        )
    ], style={'width': '50%', 'display': 'inline-block'}),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('symbol-input', 'value'),
    Input('fetch-data-button', 'n_clicks'),
    Input('time-frame-dropdown', 'value'),
    Input('chart-type-dropdown', 'value'),
    State('fetch-data-button', 'n_clicks_timestamp')

)
def update_graph(stock_symbol, n_clicks, time_frame_value, chart_type_value,timestamp):
    global df
    global clicks
    if n_clicks>clicks:
        clicks = n_clicks
        file_path = f'{stock_symbol}.csv'
        if not os.path.isfile(file_path):
            try:
                lookup(stock_symbol)
            except Exception as e:
                return {'data': [], 'layout': go.Layout(title=str(e))}
        df = pd.read_csv(file_path)
    else:
        df = pd.read_csv('AAPL.csv')
    print(n_clicks,clicks)
    stock_data = df[df.time_frame == time_frame_value]
    
    if chart_type_value == 'candlestick':
        data = [go.Candlestick(x=stock_data['date'],
                               open=stock_data['1. open'],
                               high=stock_data['2. high'],
                               low=stock_data['3. low'],
                               close=stock_data['4. close'])]
    elif chart_type_value == 'line':
        data = [go.Scatter(x=stock_data['date'], y=stock_data['4. close'], mode='lines')]
    
    return {
        'data': data,
        'layout': go.Layout(title=f'{stock_symbol} - {time_frame_value} Prices')
    }

if __name__ == '__main__':
    app.run_server(debug=True)
