import pandas as pd
import requests
from dotenv import load_dotenv
import os
import json
import boto3
from botocore.exceptions import ClientError

load_dotenv()

aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
bucket_name = 'stockvision'

api_key_news = os.getenv("api_key_news")

def fetch_news_sentiment(symbol):
    """
    Fetches news sentiment data for a given stock symbol from Alpha Vantage API,
    stores the data in S3, and retrieves the data from S3.

    Args:
        symbol (str): Stock symbol for which news sentiment data is to be retrieved.

    Returns:
        dict: News sentiment data in JSON format, or None if retrieval fails.
    """
    print("Finding", symbol)
    url_path = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers="+symbol+"&limit=10&apikey="+api_key_news

    try:
        response = requests.get(url_path)
        response.raise_for_status()
        data = response.json()
        print(data)
        if not data["items"]:
            return "No news items found"
        
        s3_object_key = os.path.join("tickers_news", symbol.upper()+'.json')
        with open('temp.json', 'w') as f:
            json.dump(data, f)
        with open('temp.json', 'rb') as f:
            s3.upload_fileobj(f, bucket_name, s3_object_key)

    except requests.exceptions.HTTPError as err:
        print("HTTP error occurred:", err)
    except requests.exceptions.RequestException as err:
        print("Error occurred:", err)
    except ClientError as err:
        print("Error occurred while uploading data to S3:", err)
    finally:
        if os.path.exists('temp.json'):
            os.remove('temp.json')

    try:
        s3_response = s3.get_object(Bucket=bucket_name, Key=s3_object_key)
        data = json.loads(s3_response['Body'].read().decode('utf-8'))
        print(data)
        return data
    except ClientError as err:
        print("Error occurred while retrieving data from S3:", err)
    return None

#fetch_news_sentiment('AAPL')