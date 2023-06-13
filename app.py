import dash
from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from flask import Flask
from dotenv import load_dotenv
import plotly.graph_objs as go
import pandas as pd
import os
import io
import json
from datetime import datetime
from plotly.subplots import make_subplots
from getters.get_data import lookup
from getters.check_update import check_outdated
from setters.chart import chart
from getters.fetch_news_sentiment import fetch_news_sentiment
import boto3

load_dotenv()

aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
bucket_name = 'stockvision'

symbol = None
stored_symbol = None
df = None

time_frames = []
with open("time_frames.json") as file:
    data = json.load(file)
    for item in data:
        time_frames.append(data[item]["time"])

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/styles.css'])

server = app.server

app.title = "StockVision - Stock Data Visualization"  # Set the title of the HTML page

app.layout = html.Div([
    html.H1(children='StockVision', className='main-title'),
    html.Div([
        html.Div([
            dcc.Input(
                id='symbol-input',
                type='search',
                placeholder='Enter stock symbol',
                className='symbol-input'
            ),
            dbc.Button('Fetch Data', id='fetch-data-button', color="success", n_clicks=0, className='fetch-button'),
        ], className='input-container'),
    ], className='input-wrapper'),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='time-frame-dropdown',
                options=time_frames,
                value='Intraday',
                className='dropdown'
            ),
        ], className='dropdown-wrapper'),
        html.Div([
            dcc.Dropdown(
                id='chart-type-dropdown',
                options=[{'label': 'Candlestick', 'value': 'candlestick'},
                         {'label': 'Line', 'value': 'line'}],
                value='candlestick',
                className='dropdown'
            ),
        ], className='dropdown-wrapper'),
        html.Div(children=[
        html.Label('Select a technical indicator:'),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[
                {'label': 'No Indicator', 'value': 'none'},  # Add "No Indicator" option
                {'label': 'SMA (Simple Moving Average)', 'value': 'SMA'},
                {'label': 'EMA (Exponential Moving Average)', 'value': 'EMA'},
            ],
            value='none', 
            ),
    html.Div(children=[
        html.Label('Select the period for Moving Average:'),
        dcc.Slider(
            id='period-slider',
            min=5,
            max=50,
            step=5,
            value=20,
            marks={i: f'{i} days' if i % 10 == 0 else '' for i in range(5, 55, 5)},
            tooltip={'always_visible': True, 'placement': 'bottom'},
            className='slider',
        ),
    ], style={'margin-top': '20px', 'font-size': '12px'}),
        ]),
        
        dbc.Button('Company Info', id='company-info-button', color="primary", n_clicks=0, className='info-button'),
    ], className='input-wrapper'),

    html.Div(id='graph-wrapper', children=[
        dcc.Loading(
            id="loading",
            type="default",
            children=dcc.Graph(id='graph-content', className='stock-graph')
        )
    ]),
    dcc.Loading(
        id="news-loading",
        type="default",
        children=html.Div(id='output-news', className='news-container'),
    ),
], className='container-fluid')




@app.callback(
    Output("company-info-modal-body", "children"),
    [Input("company-info-button", "n_clicks")],
    [State("symbol-input", "value")],
)
def update_company_info_modal_body(n, symbol):
    if n:
        return "Test (TO-D0)"
    return ""

@app.callback(
    Output("symbol-input","value"),
    Input('symbol-input', 'value')
)

def update_symbol(input):
    global symbol
    symbol = input
    return symbol

def truncate_title(title, max_words=20):
    words = title.split()
    if len(words) > max_words:
        truncated_title = ' '.join(words[:max_words]) + '...'
        return truncated_title
    else:
        return title
    
@app.callback(
        Output("output-news", "children"),
        Input('fetch-data-button', 'n_clicks')
)

def load_news(click):
    if symbol == None:
        return
    if stored_symbol != symbol:
        data = fetch_news_sentiment(symbol)
        if data == None:
            return html.Div()
    else:
        data = None
        s3_object_key = "ticker_news/"+symbol.upper()+'.json'
        response = s3.get_object(Bucket=bucket_name, Key=s3_object_key)
        data = json.loads(response['Body'].read().decode('utf-8'))

    
    feed = data["feed"]
    news_divs = [
        html.Div(
            [
                html.Img(src=item['banner_image'], className='news-image'),
                html.H3(children=truncate_title(item['title']), className='news-title', style={'margin': '10px 0'}),
                html.P(children = datetime.strptime(item['time_published'],"%Y%m%dT%H%M%S"), className='news-source'),
                html.P(children=item['summary'], className='news-summary'),
                html.P('Source: ' + item['source'], className='news-source'),
                html.P('Sentiment: ' + item['overall_sentiment_label'], className='news-sentiment'),
                html.A('Read more', href=item['url'], target='_blank', className='news-link')
            ],
            className='news-item'
        ) 
        for item in feed
    ]
    return html.Div(news_divs, className='news-container')

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
    if stored_symbol == None and symbol == None:
        return make_subplots().update_layout(title_text='Enter a symbol to start', title_font_color='red',
            plot_bgcolor='rgb(250, 242, 242)',
            paper_bgcolor='rgb(250, 242, 242)',
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="black"
            ))  
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    s3_object_key = "tickers/"+symbol.upper()+'.csv'
    if trigger == "fetch-data-button":
        stored_symbol = symbol
        try:
            s3.head_object(Bucket=bucket_name, Key=s3_object_key)
        except:
            error = lookup(stored_symbol)
            if error:
                return error
        response = s3.get_object(Bucket=bucket_name, Key=s3_object_key)
        csv_data = response['Body'].read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data))

        if check_outdated(stored_symbol, df):
            error = lookup(stored_symbol)
    response = s3.get_object(Bucket=bucket_name, Key=s3_object_key)
    csv_data = response['Body'].read().decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_data))
        
    stock_data = df[df.time_frame == time_frame_value]

    data,title = chart(stored_symbol,stock_data,chart_type_value,time_frame_value)

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
    app.run_server(debug=False)
