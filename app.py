import dash
from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
from dotenv import load_dotenv
import plotly.graph_objs as go
import alpha_vantage.timeseries as ts
import pandas as pd
import os
import json
from datetime import datetime as dt

load_dotenv()
api_key = os.getenv("api_key")
symbol = None
stored_symbol = None
df = None

time_frames = []
with open("time_frames.json") as file:
    data = json.load(file)
    for item in data:
        time_frames.append(data[item]["time"])

ts = ts.TimeSeries(api_key, output_format='pandas')

def get_data(symbol, time_frame, ts_function, interval=None, outputsize="compact"):

    if ts_function == "ts.get_intraday":
        data, meta_data = ts.get_intraday(symbol=symbol, outputsize=outputsize, interval=interval)
    else:
        data, meta_data = ts_function(symbol=symbol)
    data.index = pd.to_datetime(data.index)
    data = data.sort_index(ascending=True)
    data['time_frame'] = time_frame
    return data

def lookup(symbol):
    try:
        intraday_data = get_data(symbol, "Intraday", "ts.get_intraday", interval='60min')
        daily_data = get_data(symbol, "Daily adjusted",  ts.get_daily_adjusted)
        weekly_data = get_data(symbol, "Weekly adjusted",  ts.get_weekly_adjusted)
        monthly_data = get_data(symbol, "Monthly adjusted",  ts.get_monthly_adjusted)

        data = pd.concat([intraday_data, daily_data, weekly_data, monthly_data])

        data.to_csv(symbol.upper()+'.csv', index=True)
        return data
    except ValueError:
        print("Invalid symbol or API key")
        return pd.DataFrame()

def check_outdated(df):
    date = df[df.time_frame == "Daily adjusted"].iloc[-1]["date"]
    date = str(date)
    date = dt.strptime(date,"%Y-%m-%d %H:%M:%S")
    diff = date-dt.now()
    diff = abs(int(diff.days))

    return diff>4


app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='StockVision', style={'textAlign':'center'}),
    html.Div([
    html.Div([
        dcc.Input(
            id='symbol-input',
            type='search',
            placeholder='Enter stock symbol',
            style={'width': '30%', 'marginRight': '10px'}
        ),
        dbc.Button('Fetch Data', id='fetch-data-button',color="success", n_clicks=0),
    ]),
        dcc.Dropdown(
            id='time-frame-dropdown',
            options=time_frames,
            value='Intraday'
        ),
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[{'label': 'Candlestick', 'value': 'candlestick'},
                     {'label': 'Line', 'value': 'line'}],
            value='candlestick'
        )
    ], style={'width': '50%', 'display': 'inline-block'}),
    html.Div(id='graph-wrapper', children=[
        dcc.Loading(
            id="loading",
            type="default",
            children=dcc.Graph(id='graph-content')
        )
    ]),
    html.Div(id='output-container', children=[
    html.P(id='output-text', children='Output will be displayed here')
    ])  
])

@app.callback(
    Output("symbol-input","value"),
    Input('symbol-input', 'value')
)

def update_symbol(input):
    global symbol
    symbol = input
    return symbol


@app.callback(
    Output('graph-content', 'figure'),
    [
        Input('fetch-data-button', 'n_clicks'),
        Input('time-frame-dropdown', 'value'),
        Input('chart-type-dropdown', 'value')
                ],
)
def update_graph(n_clicks, time_frame_value, chart_type_value):
    global stored_symbol
    global clicks
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger == "fetch-data-button":
        stored_symbol = symbol
        file_path = stored_symbol.upper()+".csv"
        if not os.path.isfile(file_path):
            try:
                lookup(stored_symbol)
            except Exception as e:
                return make_subplots().update_layout(title_text='Error: '+str(e), title_font_color='red',
                plot_bgcolor='rgb(250, 242, 242)',
                paper_bgcolor='rgb(250, 242, 242)',
                font=dict(
                    family="Courier New, monospace",
                    size=12,
                    color="black"
                ))
        try:
            df = pd.read_csv(file_path)
        except:
            return make_subplots().update_layout(title_text='Error: Invalid symbol', title_font_color='red',
                plot_bgcolor='rgb(250, 242, 242)',
                paper_bgcolor='rgb(250, 242, 242)',
                font=dict(
                    family="Courier New, monospace",
                    size=12,
                    color="black"
                ))

        if check_outdated(df):
            try:
                lookup(stored_symbol)
            except Exception as e:
                return make_subplots().update_layout(title_text='Error: '+str(e), title_font_color='red',
                plot_bgcolor='rgb(250, 242, 242)',
                paper_bgcolor='rgb(250, 242, 242)',
                font=dict(
                    family="Courier New, monospace",
                    size=12,
                    color="black"
                ))
    else:
        df = pd.read_csv(stored_symbol+".csv")
    stock_data = df[df.time_frame == time_frame_value]

    if chart_type_value == 'candlestick':
        data = [go.Candlestick(
            x=stock_data['date'],
            open=stock_data['1. open'],
            high=stock_data['2. high'],
            low=stock_data['3. low'],
            close=stock_data['4. close']
        )]
        title = stored_symbol.upper() + " - " + time_frame_value + " Prices"
    elif chart_type_value == 'line':
        data = [go.Scatter(
            x=stock_data['date'],
            y=stock_data['4. close'],
            mode='lines'
        )]
        title = stored_symbol.upper() + " - " + time_frame_value + " Prices"

    return {
        'data': data,
        'layout': go.Layout(
            title=title,
            yaxis=dict(
                title='Price ($)',
                titlefont=dict(size=16),
                tickfont=dict(size=14),
                gridcolor='rgba(0, 0, 0, 0.1)',
                zerolinecolor='rgba(0, 0, 0, 0.1)'
            ),
            plot_bgcolor='rgb(250, 242, 242)',
            paper_bgcolor='rgb(250, 242, 242)',
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="black"
            ),
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)