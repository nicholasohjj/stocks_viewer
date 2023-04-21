import pandas as pd
import requests
from dotenv import load_dotenv
import os
import json
import boto3

load_dotenv()

api_key_sma_intraday = os.getenv("api_key_sma_intraday")
api_key_sma_daily = os.getenv("api_key_sma_daily")
api_key_sma_weekly = os.getenv("api_key_sma_weekly")
api_key_sma_monthly = os.getenv("api_key_sma_monthly")

def get_data(symbol, interval, api_key, function):
    url_path = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&time_period=20&series_type=close&apikey={api_key}"
    
    try:
        response = requests.get(url_path)
        data = response.json()
        print(data)
        if not data["items"]:
            return "Maximum calls reached"

        with open(symbol.upper()+"_"+function+".json","w") as json_file:
            json.dump(data, json_file, indent=4)
        
        # Upload the JSON file to S3
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(symbol.upper()+"_"+function+".json", 'your-bucket-name', 'folder-name/'+symbol.upper()+"_"+function+".json")

    except:
        print("Maximum API calls reached")
    
    json_data = None
    try:
        with open(symbol.upper()+'_'+function+'.json', 'r') as file:
            json_data = json.load(file)

        data = json_data

        return data
    except:
        return


def lookup_sma(symbol):
    return get_data(symbol, "daily", api_key_sma_daily, "SMA")


def lookup_ema(symbol):
    return get_data(symbol, "daily", api_key_sma_daily, "EMA")


##TESTS
#lookup_sma("AAPL")
#lookup_ema("AAPL")
