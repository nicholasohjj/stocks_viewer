import dash
from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import plotly.graph_objs as go
import pandas as pd
import os
import json
from plotly.subplots import make_subplots
from getters.get_data import lookup
from getters.check_update import check_outdated
from setters.chart import chart
from getters.get_news import lookup_news

INTERVAL_OPTIONS = ['Intraday', 'Daily', 'Weekly', 'Monthly']
CHART_TYPE_OPTIONS = ['Candlestick', 'Line']
                      
load_dotenv()

symbol = None
stored_symbol = None
df = None

time_frames = []
with open("time_frames.json") as file:
    data = json.load(file)
    for item in data:
        time_frames.append(data[item]["time"])

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/styles.css'])
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
        html.Div([
            dcc.Dropdown(
                id='time-frame-dropdown',
                options=time_frames,
                value='Intraday',
                className='dropdown'
            ),
            dcc.Dropdown(
                id='chart-type-dropdown',
                options=[{'label': 'Candlestick', 'value': 'candlestick'},
                         {'label': 'Line', 'value': 'line'}],
                value='candlestick',
                className='dropdown'
            ),
            dbc.Button('Company Info', id='company-info-button', color="primary", n_clicks=0, className='info-button'),
        ], className='input-container'),
    ], className='input-wrapper'),
    
    html.Div(id='graph-wrapper', children=[
        dcc.Loading(
            id="loading",
            type="default",
            children=dcc.Graph(id='graph-content', className='stock-graph')
        )
    ]),
    html.Div(id='output-news', className='news-container'),
    dbc.Modal(
        [
            dbc.ModalHeader("Company Info"),
            dbc.ModalBody(id='company-info-modal-body'),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-company-info-button", className="ml-auto", color="secondary")
            ),
        ],
        id="company-info-modal",
    ),
])

@app.callback(
    Output("company-info-modal", "is_open"),
    [Input("company-info-button", "n_clicks"), Input("close-company-info-button", "n_clicks")],
    [State("company-info-modal", "is_open")],
)
def toggle_company_info_modal(n, n2, is_open):
    if n or n2:
        return not is_open
    return is_open

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
        data = lookup_news(symbol)
        if data == None:
            return html.Div()
    else:
        data = None
        with open('/assets/ticker_news/'+stored_symbol.upper()+'.json', 'r') as file:
            data = json.load(file)
    
    feed = data["feed"]
    news_divs = [
        html.Div(
            [
                html.Img(src=item['banner_image'], className='news-image'),
                html.H3(children=truncate_title(item['title']), className='news-title', style={'margin': '10px 0'}),
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

    folder_path = "/assets/tickers/"
    if trigger == "fetch-data-button":
        stored_symbol = symbol
        file_path = folder_path+stored_symbol.upper()+".csv"
        if not os.path.isfile(file_path):
            error = lookup(stored_symbol)
            if error:
                return error
        df = pd.read_csv(folder_path+stored_symbol+".csv")

        if check_outdated(stored_symbol, df):
            error = lookup(stored_symbol)
    
    df = pd.read_csv(folder_path+stored_symbol+".csv")
        
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
    app.run_server(debug=True)