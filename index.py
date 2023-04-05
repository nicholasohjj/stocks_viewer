import requests
from dotenv import load_dotenv
import csv
import os

load_dotenv()

api_key = os.getenv("api_key")
symbol = os.getenv("symbol")
print(api_key,symbol)
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}"
response = requests.get(url)
data = response.json()["Time Series (Daily)"]

## writing data into csv file
with open("data.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
    for date, values in data.items():
        writer.writerow([date, values["1. open"], values["2. high"], values["3. low"], values["4. close"], values["6. volume"]])

