
<h1 align="center">
    Stockvision (Buggy)
</h1>

<p align="center">
  <a href="#about-offcharge">About</a> •
  <a href="#requirements">Requirements</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a>

</p>

## About
StockVision is a Python program that utilizes the Dash and Plotly libraries to visualize stock prices. It fetches data from the Alpha Vantage API and provides users with the option to view intraday, daily adjusted, weekly adjusted, and monthly adjusted prices. Additionally, charts can be viewed in line or candlestick format. The data is securely stored in Amazon S3, a highly scalable and durable object storage service provided by Amazon Web Services (AWS).

## Requirements
* Python 3.6 or higher
* Multiple Alpha Vantage API keys (you can get a free one [here](https://www.alphavantage.co/support/#api-key))
* Git
* Amazon S3 bucket for data storage (you can create one in your AWS account)

## Installation
1. Clone the repository:

```sh
git clone https://github.com/nicholasohjj/StockVision.git
```
2. Navigate to the repository directory:
```sh
cd StockVision
```
3. Install the required dependencies:
```sh
pip install -r requirements.txt
```
4. Create a .env file with your Alpha Vantage API key (more than 1 is):
```sh
echo "api-key1=YOUR_API_KEY_1_HERE" > .env
echo "api-key2=YOUR_API_KEY_2_HERE" >> .env
# Add more api-keyN entries as needed
```
5. Configure your Amazon S3 bucket settings in the config.py file by providing the bucket name, region, and access credentials.

## Usage
1. Start the program by running the following command:

```sh
python app.py
```
2. Open a web browser and go to http://localhost:8050.
3. Use the dropdown menus to select the stock symbol, time period, and chart type.
4. Click the Update Chart button to display the selected chart.
5. The data fetched from Alpha Vantage API is stored securely in your configured Amazon S3 bucket.
6. To exit the program, press CTRL + C in the terminal window where the program is running.
---

> GitHub [@nicholasohjj](https://github.com/nicholasohjj) &nbsp;&middot;&nbsp;
> Linkedin [@nicholasohjj](https://www.linkedin.com/in/nicholasohjj)

