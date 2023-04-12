import pandas as pd
import requests
from dotenv import load_dotenv
import os
import json
load_dotenv()

api_key_news = os.getenv("api_key_news")


def lookup_news(symbol):
    print("Finding", symbol)
    url_path = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers="+symbol+"&limit=10&apikey="+api_key_news

    try:
        response = requests.get(url_path)
        data = response.json()
        print(data)
        if not data["items"]:
            return "Maximum calls reached"

        with open("ticker_news/"+symbol+".json","w") as json_file:
            json.dump(data, json_file, indent=4)

    except:
        print("Maximum API calls reached")
    
    json_data = None
    try:
        with open('ticker_news/aapl.json', 'r') as file:
            json_data = json.load(file)

        data = json_data

        return data
    except:
        return
##TESTS
#lookup_news("AAPL")
