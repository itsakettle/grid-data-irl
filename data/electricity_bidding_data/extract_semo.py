import boto3
import requests
import json
from datetime import datetime, timezone

SEMO_MINIMAL_COST_URL = "https://reports.sem-o.com/documents/PUB_30MinImbalCost_202312251900.xml"
LOOKBACK_DAYS = 2

def get_file_from_s3(bucket: str, key: str) -> str:
    """
    Get's a file from S3.

    Args:
    - bucket (str): S3 bucket
    - key (str): Key of the file.

    Returns:
        Returns a string with the file contents as a string or none
    """

    s3_client = boto3.client("s3")
    try:
        response = s3_client.get_object("lastest_data.json")
        json_string = response['Body'].read().decode('utf-8')
    except s3_client.Client.exceptions.NoSuchKey as err:
        return None
    
    return json_string

def get_latest_data_json_from_s3(bucket: str, key: str) -> dict:
    """
    Get's the json data of the last few days

    Args:
    - bucket (str): S3 bucket
    - key (str): Key of the file.

    Returns:
        Returns a dict of the latest semo json data saved to S3 
    """

    json_data = get_file_from_s3(bucket, key)
    if json_data is None:
        return []
    else:
        data = json.loads(json_data)
        return data
    
def periods_to_fetch(latest_data: dict) -> list:
    """
    Figure's out which periods to fetch based on the latest_data that has already been fetched.

    Args:
    - latest_data (dict): Latest data

    Returns:
        A list of periods to fetch data for.

    """
    current_time = datetime.now(timezone.utc)
    last_period = datetime(current_time.year,
        current_time.month,
        current_time.day,
        current_time.hour,
        30 if current_time.minute >= 30 else 0,
        0,
        tzinfo=timezone.utc)

    []


def put_latest_data_json_from_s3(latest_data: list, bucket: str) -> list:
    pass

def fetch_semo_data():
    r = requests.get(SEMO_MINIMAL_COST_URL)
    print(r.txt)

def extract_handler(event, context):
    get_latest_data_json_from_s3
    figure_out_dates
    fill_missing_periods
    put_latest_data_json_from_s3

    json 