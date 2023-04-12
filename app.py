import dash
from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import plotly.graph_objs as go
import pandas as pd
import os
import json
from getters.get_data import lookup
from getters.check_update import check_outdated
from setters.chart import chart
from getters.get_news import lookup_news

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
        ], className='dropdown-container'),
    ], className='input-wrapper'),
    html.Div(id='graph-wrapper', children=[
        dcc.Loading(
            id="loading",
            type="default",
            children=dcc.Graph(id='graph-content', className='stock-graph')
        )
    ]),
    html.Div(id='output-news', className='news-container')
])

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
    if stored_symbol != symbol:
        data = lookup_news(symbol)
        if data == None:
            return html.Div()
        feed = data["feed"]
        news_divs = [
            html.Div(
                [
                    html.Img(src=item['banner_image'], className='news-image'),
                    html.H3(children=truncate_title(item['title']), className='news-title', style={'margin': '10px 0'}),
                    html.P(children=item['summary'], className='news-summary'),
                    html.P('Source: ' + item['source'], className='news-source'),
                    html.P('Category: ' + item['category_within_source'], className='news-category'),
                    html.P('Sentiment: ' + item['overall_sentiment_label'], className='news-sentiment'),
                    html.A('Read more', href=item['url'], target='_blank', className='news-link')
                ],
                className='news-item'
            ) 
            for item in feed
        ]

        # Add the last row if there are any remaining news items

        return html.Div(news_divs, className='news-container')
    else:
        return 

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

    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    folder_path = "tickers/"
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