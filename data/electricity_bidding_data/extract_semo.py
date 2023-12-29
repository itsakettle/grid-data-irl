import boto3
import requests
import xml.etree.ElementTree as ET
from typing import Type, List
import polars as pl
from datetime import datetime, timezone

SEMO_MINIMAL_COST_URL = "https://reports.sem-o.com/documents/PUB_30MinImbalCost_{period}.xml"
SEMO_PERIOD_FORMAT = "%Y%m%d%H%M"

def create_s3_url(bucket: str, key: str):
    """
    Creates S3 path from a bucket and key.

    Args:
    - bucket (str): S3 bucket
    - key (str): Key of the file.

    Returns:
        Returns the path as a string.
    """

    return f's3://{bucket}/{key}'


def read_df(path: str) -> Type[pl.DataFrame]:
    """
    Get's a dataframe, handling errors on the way

    Args:
    - path (str): Path to the df.

    Returns:
        A polars dataframe or None if it doesn't exist
    """
    try:
        df = pl.read_parquet(path)
    except FileNotFoundError:
        df = None

    return df

def init_df(periods: List[str], imbalance_prices: List[float]) -> Type[pl.DataFrame]:
    return pl.DataFrame({"period": periods, "imbalance_price": imbalance_prices})

    
def period_to_fetch(run_time: datetime):
    """
    Figure's out which period to fetch

    Returns:
        The 30 mnute period to fetch as a string e.g. 202312251900

    """

    period = datetime(run_time.year,
        run_time.month,
        run_time.day,
        run_time.hour,
        30 if run_time.minute >= 30 else 0,
        0,
        tzinfo=timezone.utc)
    
    return period.strftime(SEMO_PERIOD_FORMAT)


def put_latest_data_json_from_s3(latest_data: list, bucket: str) -> list:
    pass

def fetch_semo_xml(period: str):
    """
    Fetch semo data for a period. This won't be tested.

    Args:
    - period (str): The start time of the period to fetch .

    Returns:
     XML as a string or None if there is an error

    """
    semo_url = SEMO_MINIMAL_COST_URL.format(period=period)
    response = requests.get(semo_url)

    if response.status_code != 200:
        return None

    return response.text


def parse_semo_schema(semo_xml: str):
    """
    Fetch semo data for a period.

    Args:
    - semo_xml (str): The xml to parse.

    Returns:
     A dictionary of attributes from the xml or None if there is an error parsing the xml.

    """
    try:
        xml_root = ET.fromstring(semo_xml)
        imbalance_xml = xml_root.find("PUB_30MinImbalCost")
        xml_as_dict =  {"imbalance_volume": float(imbalance_xml.attrib.get('ImbalanceVolume')),
                        "imbalance_price": float(imbalance_xml.attrib.get('ImbalancePrice')),
                        "imbalance_cost": float(imbalance_xml.attrib.get('ImbalanceCost'))}
    except:
        return None
    
    return xml_as_dict
    

def extract_handler(event, context):
    get_latest_data_json_from_s3
    figure_out_dates
    fill_missing_periods
    put_latest_data_json_from_s3

    json 