import requests
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import csv
import os
import time
import json
load_dotenv()

api_key = os.getenv("api_key")
TIME_FRAMES = None
with open("time_frames.json") as file:
    TIME_FRAMES = json.load(file)

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

    url = TIME_FRAMES[time_frame_chosen]["url"]
    url = url.replace("_API_KEY_",api_key)
    url = url.replace("_SYMBOL_", symbol)

    response = requests.get(url)
    raw_data = response.json()
    print(raw_data)
    if len(raw_data) == 1:
        print("Invalid symbol, please try again.")
        return lookup()
    data_index = [i for i in raw_data.keys()][1]
    data = raw_data[data_index]

    header = TIME_FRAMES[time_frame_chosen]["time"]

    return symbol,data,header

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

def read_csv_and_plot(symbol):
    dates = []
    closing_prices = []
    title = ""
    with open(f"{symbol}.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        print(title)
        for row in reader:
            if not title:
                title = list(row.keys())[-1]
            dates.append(row["Date"])
            closing_prices.append(float(row["Close"]))

    plt.plot(dates, closing_prices)
    plt.title(f"{title} Closing Prices for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Closing Price ($)")
    plt.show()


print("Stocks Visualiser")
print("========")
time.sleep(0.5)
symbol,data,header = lookup()
write_into_csv(symbol,data,header)
read_csv_and_plot(symbol)


