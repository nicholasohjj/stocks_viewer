from datetime import datetime
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

    last_closing_time = datetime.strptime(meta_data['3. Last Refreshed'], "%Y-%m-%d")
    current_date = datetime.strptime(df.loc[df['time_frame'] == "Daily adjusted", 'date'].iloc[-1], "%Y-%m-%d %H:%M:%S")

    diff = (last_closing_time - current_date).days
    print(diff)

    return diff != 0
