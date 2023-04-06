from dotenv import load_dotenv
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
import time
import json

load_dotenv()

ts = TimeSeries(key=os.getenv("api_key"),output_format="pandas")

TIME_FRAMES = None
with open("time_frames.json") as file:
    TIME_FRAMES = json.load(file)

def get_data(symbol,ts_function, outputsize="compact"):
    data, meta_data = ts_function(ts, symbol=symbol)
    print(data)
    data.index = pd.to_datetime(data.index)
    data = data.sort_index(ascending=True)

    return data

def lookup():

    symbol = input("Enter symbol to lookup: ").strip().upper()

    print("--------")
    time_frame_chosen = None
    while not time_frame_chosen:
        print("Select time frame (Enter digit)")
        print("Enter digit followed by info for more details on time frame (E.g: 1 info)")
        print("--------")
        for bullet, details in TIME_FRAMES.items():
            time_frame = details["time"]
            print(f"{bullet}: {time_frame}")
        option = input("Option: ").strip()
        if "info" in option.lower():
            response = option.split()
            print(TIME_FRAMES[response[0]]["info"])
            move = input("Press any key to continue")
        else:
            try:
                int(option)
            except:
                print("Enter a valid digit")
                continue
            if int(option) > len(TIME_FRAMES):
                print("Enter a valid digit")
            else:
                time_frame_chosen = option

    if time_frame_chosen == "1":
        data = get_data(symbol,TimeSeries.get_intraday,outputsize="compact")
    elif time_frame_chosen == "2":
        data = get_data(symbol,TimeSeries.get_daily_adjusted,outputsize="compact")
    elif time_frame_chosen == "3":
        data = get_data(symbol,TimeSeries.get_weekly_adjusted)
    elif time_frame_chosen == "4":
        data = get_data(symbol,TimeSeries.get_monthly_adjusted)
    time_frame_header = TIME_FRAMES[time_frame_chosen]["time"]
    return data,time_frame_chosen,symbol,time_frame_header

## TO-DO modify writing into csv to fit all options

def display_data(data, header,symbol):
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['1. open'], high=data['2. high'],
                low=data['3. low'], close=data['4. close'])
                     ])
    fig.update_layout(title=f'{symbol} Stock Price ({time_frame_header})', xaxis_rangeslider_visible=False)
    fig.show()


print("Stocks Visualiser")
print("========")
time.sleep(0.5)
data,time_frame_chosen,symbol,time_frame_header = lookup()
display_data(data, time_frame_header,symbol)


