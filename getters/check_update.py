from datetime import datetime as dt
import pandas as pd

def check_outdated(df):
    date = df[df.time_frame == "Daily adjusted"].iloc[-1]["date"]
    date = str(date)
    date = dt.strptime(date,"%Y-%m-%d %H:%M:%S")
    diff = date-dt.now()
    diff = abs(int(diff.days))

    return diff>4