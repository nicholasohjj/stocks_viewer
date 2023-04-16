import pandas as pd
import alpha_vantage.timeseries as ts
from dotenv import load_dotenv
from plotly.subplots import make_subplots
import os
import boto3

load_dotenv()
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
bucket_name = 'stockvision'

api_key_intraday = os.getenv("api_key_intraday")
api_key_daily = os.getenv("api_key_daily")
api_key_weekly = os.getenv("api_key_weekly")
api_key_monthly = os.getenv("api_key_monthly")

ts_intraday = ts.TimeSeries(api_key_intraday, output_format='pandas')
ts_daily = ts.TimeSeries(api_key_daily, output_format='pandas')
ts_weekly = ts.TimeSeries(api_key_weekly, output_format='pandas')
ts_monthly = ts.TimeSeries(api_key_monthly, output_format='pandas')

def get_data(symbol, time_frame, ts_function, interval=None, outputsize="full"):
    data = None
    if ts_function == "ts.get_intraday":
        data, meta_data = ts_intraday.get_intraday(symbol=symbol, outputsize=outputsize, interval=interval)
    else:
        data, meta_data = ts_function(symbol=symbol)
    data.index = pd.to_datetime(data.index)
    data = data.sort_index(ascending=True)
    data['time_frame'] = time_frame
    return data

def lookup(symbol):
    try:
        intraday_data = get_data(symbol, "Intraday", "ts.get_intraday", interval='1min')
        daily_data = get_data(symbol, "Daily adjusted",  ts_daily.get_daily_adjusted)
        weekly_data = get_data(symbol, "Weekly adjusted",  ts_weekly.get_weekly_adjusted)
        monthly_data = get_data(symbol, "Monthly adjusted",  ts_monthly.get_monthly_adjusted)
        data = pd.concat([intraday_data, daily_data, weekly_data, monthly_data])
        #folder_path = '/assets/tickers/'
        #data.to_csv(folder_path+symbol.upper()+'.csv', index=True)
        
        s3_object_key = "tickers/"+symbol.upper()+'.csv'
        data_csv = data.to_csv(index = True)
        s3.put_object(Body=data_csv, Bucket=bucket_name, Key=s3_object_key)

    except ValueError as e:
        print(str(e))
        if "Invalid API call" in str(e):
            
            return make_subplots().update_layout(title_text='Error: Invalid API Call', title_font_color='red',
                plot_bgcolor='rgb(250, 242, 242)',
                paper_bgcolor='rgb(250, 242, 242)',
                font=dict(
                    family="Courier New, monospace",
                    size=12,
                    color="black"
                ))
        else:
            return make_subplots().update_layout(title_text='Error: maximum calls reached', title_font_color='red',
                plot_bgcolor='rgb(250, 242, 242)',
                paper_bgcolor='rgb(250, 242, 242)',
                font=dict(
                    family="Courier New, monospace",
                    size=12,
                    color="black"
                ))  
##TESTS