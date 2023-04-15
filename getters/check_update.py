from datetime import datetime as dt
from alpha_vantage.timeseries import TimeSeries
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

api_key_update = os.getenv("api_key_update")

ts = TimeSeries(key=api_key_update)


def check_outdated(symbol, df):
    try:
        data, meta_data = ts.get_daily_adjusted(symbol=symbol)
    except:
        return False
    last_closing_time = meta_data['3. Last Refreshed']
    last_closing_time = str(last_closing_time)
    last_closing_time = dt.strptime(last_closing_time,"%Y-%m-%d")

    current_date = df[df.time_frame == "Daily adjusted"].iloc[-1]["date"]
    current_date = str(current_date)
    current_date = dt.strptime(current_date,"%Y-%m-%d %H:%M:%S")

    diff = last_closing_time-current_date
    diff = int(diff.days)
    ##TO-DO
    ## Sync with last closing time1

    print(diff)

    return diff != 0