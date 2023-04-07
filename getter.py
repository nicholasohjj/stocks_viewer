from dotenv import load_dotenv
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objects as go
import os
import time
import json

load_dotenv()

ts = TimeSeries(key="K2J7THYH6AB78L5M",output_format="pandas")

TIME_FRAMES = None
with open("time_frames.json") as file:
    TIME_FRAMES = json.load(file)

def get_data(symbol, time_frame, ts_function, interval=None, outputsize="compact"):
    if ts_function == ts.get_intraday:
        data, meta_data = ts_function(symbol=symbol, outputsize=outputsize, interval=interval)
    else:
        data, meta_data = ts_function(symbol=symbol)
    data.index = pd.to_datetime(data.index)
    data = data.sort_index(ascending=True)
    data['time_frame'] = time_frame
    return data

def init():
    print("Stocks Visualiser")
    print("========")
    symbol = input("Enter symbol to lookup: ").strip().upper()
    try:
        get_data(symbol, ts.get_intraday, interval='60min')
        return symbol
    except:
        print("Invalid symbol")
        init()


def lookup(symbol):
    print("LOOKUP")

    intraday_data = get_data(symbol, "Intraday", ts.get_intraday, interval='60min')
    daily_data = get_data(symbol, "Daily adjusted",  ts.get_daily_adjusted)
    weekly_data = get_data(symbol, "Weekly adjusted",  ts.get_weekly_adjusted)
    monthly_data = get_data(symbol, "Monthly adjusted",  ts.get_monthly_adjusted)

    data = pd.concat([intraday_data, daily_data, weekly_data, monthly_data])

    data.to_csv(f'{symbol}.csv', index=True)
    return data

## TO-DO modify writing into csv to fit all options

def display_data(data):
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['1. open'], high=data['2. high'],
                low=data['3. low'], close=data['4. close'])
                     ])
    return fig

def display_solo(value,symbol):
    data = lookup(value,symbol)
    display_data(data, value,symbol)
    return data,symbol

lookup("AAPL")