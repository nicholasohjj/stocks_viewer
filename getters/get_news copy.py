import pandas as pd
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_key_sma_intraday = os.getenv("api_key_sma_intraday")
api_key_sma_daily = os.getenv("api_key_sma_daily")
api_key_sma_weekly = os.getenv("api_key_sma_weekly")
api_key_sma_monthly = os.getenv("api_key_sma_monthly")

def get_data(symbol, interval,api_key):
    url_path = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval={interval}&time_period=20&series_type=close&apikey={api_key}"
    
    try:
        response = requests.get(url_path)
        data = response.json()
        print(data)
        if not data["items"]:
            return "Maximum calls reached"

        with open("/assets/ticker_news/"+symbol.upper()+".json","w") as json_file:
            json.dump(data, json_file, indent=4)
    except:
        print("Maximum API calls reached")
    
    json_data = None
    try:
        with open('/assets/ticker_news/'+symbol.upper()+'.json', 'r') as file:
            json_data = json.load(file)

        data = json_data

        return data
    except:
        return


def lookup_sma(symbol):
    try:
        response = requests.get(url_path)
        data = response.json()
        print(data)
        if not data["items"]:
            return "Maximum calls reached"

        with open("/assets/ticker_news/"+symbol.upper()+".json","w") as json_file:
            json.dump(data, json_file, indent=4)

    except:
        print("Maximum API calls reached")
    
    json_data = None
    try:
        with open('/assets/ticker_news/'+symbol.upper()+'.json', 'r') as file:
            json_data = json.load(file)

        data = json_data

        return data
    except:
        return
##TESTS
#lookup_news("AAPL")
