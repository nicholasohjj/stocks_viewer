
<h1 align="center">
  <br>
  <br>
    Stockvision
  <br>
</h1>

<p align="center">
  <a href="#about-offcharge">About</a> •
  <a href="#requirements">Requirements</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a>

</p>

## About
StockVision is a Python program that utilizes the Dash and Plotly libraries to visualize stock prices. It fetches data from the Alpha Vantage API and provides users with the option to view intraday, daily adjusted, weekly adjusted, and monthly adjusted prices. Additionally, charts can be viewed in line or candlestick format.

## Requirements
* Python 3.6 or higher
* Alpha Vantage API key (you can get a free one [here](https://www.alphavantage.co/support/#api-key))
* Git

## Installation

```sh
git clone https://github.com/nicholasohjj/StockVision.git

cd StockVision

pip install -r requirements.txt

echo "api-key=YOUR_API_KEY_HERE" > .env
```
## Usage
1. Start the program by running the following command:

```sh
python app.py
```
2. Open a web browser and go to http://localhost:8050.
3. Use the dropdown menus to select the stock symbol, time period, and chart type.
4. Click the Update Chart button to display the selected chart.
5. To exit the program, press CTRL + C in the terminal window where the program is running.
---

> GitHub [@nicholasohjj](https://github.com/nicholasohjj) &nbsp;&middot;&nbsp;
> Linkedin [@nicholasohjj](https://www.linkedin.com/in/nicholasohjj)

