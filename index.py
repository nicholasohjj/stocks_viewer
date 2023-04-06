import requests
from dotenv import load_dotenv
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import csv
import os
import time
import datetime
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
    return data

def format_data(data, choice):
    if choice == "1":
        data = data.resample("1min").agg({
            "1. open": "first",
            "2. high": "max",
            "3. low": "min",
            "4. close": "last",
            "5. volume": "sum"
        })
    elif choice == "2":
        data = data[["1. open", "2. high", "3. low", "4. close"]]
        data.columns = ["Open", "High", "Low", "Close"]
    else:
        data = data[["1. open", "2. high", "3. low", "4. close", "5. adjusted close"]]
        data.columns = ["Open", "High", "Low", "Close", "Adjusted Close"]
    data = data.reset_index()
    data["date"] = data["date"].apply(mdates.date2num)
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
        data = get_data(symbol.TimeSeries.get_daily_adjusted,outputsize="compact")
    elif time_frame_chosen == "3":
        data = get_data(symbol,TimeSeries.get_weekly_adjusted)
    elif time_frame_chosen == "4":
        data = get_data(symbol,TimeSeries.get_monthly_adjusted)

    return data,time_frame_chosen,symbol

## TO-DO modify writing into csv to fit all options
def write_into_csv(symbol,data, header):

    with open(f"{symbol}.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        details = list(list(data.values())[0].keys())
        row_title = ["Date"]
        for detail in details:
            title = detail.split()[1].capitalize()
            row_title.append(title)
        row_title.append(header)
        writer.writerow(row_title)
        for date, values in data.items():
            contents = [date] + [values[detail] for detail in details]
            writer.writerow(contents)

def display_data(data, time_frame_chosen,symbol):
    if time_frame_chosen == "1":
        fig, ax = plt.subplots()
        candlestick_ohlc(ax, data.values, width=0.0005, colorup="g", colordown="r")
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.title(f"Intraday Candlestick Chart for {symbol}")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.show()
    else:
        plt.plot(data["date"], data["Close"])
        fig, ax = plt.subplots()
        ax.xaxis_date()
        candlestick_ohlc(ax, data.values, width=0.0005, colorup="g", colordown="r")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.title(time_frame_chosen + " Stock Data for " + symbol)
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.show()


print("Stocks Visualiser")
print("========")
time.sleep(0.5)
data,time_frame_chosen,symbol = lookup()
data = format_data(data, time_frame_chosen)
display_data(data, time_frame_chosen,symbol)


