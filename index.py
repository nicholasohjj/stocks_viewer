import requests
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import csv
import os
import time
import json
load_dotenv()

api_key = os.getenv("api_key")

time_frames = None
with open("time_frames.json") as file:
    time_frames = json.load(file)

def write_into_csv(symbol):
    with open(f"{symbol}.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        for date, values in data.items():
            writer.writerow([date, values["1. open"], values["2. high"], values["3. low"], values["4. close"], values["6. volume"]])

def read_csv_and_plot(symbol):
    dates = []
    closing_prices = []
    with open(f"{symbol}.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            dates.append(row["Date"])
            closing_prices.append(float(row["Close"]))

    plt.plot(dates, closing_prices)
    plt.title(f"Daily Closing Prices for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Closing Price ($)")
    plt.show()

print("Stocks Visualiser")
print("========")
time.sleep(0.5)


symbol = input("Enter symbol to lookup: ").strip().upper()

print("--------")
time_frame_chosen = None
while not time_frame_chosen:
    print("Select time frame (Enter digit)")
    print("Enter digit followed by info for more details on time frame (E.g: 1 info)")
    print("--------")
    for bullet, details in time_frames.items():
        time_frame = details["time"]
        print(f"{bullet}: {time_frame}")
    option = input("Option: ").strip()
    if "info" in option.lower():
        response = option.split()
        print(time_frames[response[0]]["info"])
        move = input("Press any key to continue")
    else:
        try:
            option = int(option)
        except:
            print("Enter a valid digit")
            continue
        if int(option) > len(time_frames):
            print("Enter a valid digit")
        else:
            time_frame_chosen = option



print(api_key,symbol)
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}"
response = requests.get(url)
data = response.json()["Time Series (Daily)"]

write_into_csv(symbol)
read_csv_and_plot(symbol)
## writing data into csv file



