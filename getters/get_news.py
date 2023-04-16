import pandas as pd
import requests
from dotenv import load_dotenv
import os
import json
import boto3

load_dotenv()

aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
bucket_name = 'stockvision'

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
        
        s3_object_key = "tickers_news/"+symbol.upper()+'.json'
        s3.put_object(Body=json.dumps(data), Bucket=bucket_name, Key=s3_object_key)

    except:
        print("Maximum API calls reached")
    
    try:
        response = s3.get_object(Bucket=bucket_name, Key=s3_object_key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        print(data)
        return data
    except:
        return
##TESTS

