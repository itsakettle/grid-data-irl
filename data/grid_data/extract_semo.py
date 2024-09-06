import boto3
import requests
import xml.etree.ElementTree as ET
from typing import Type, List
from datetime import datetime, timezone
from collections import namedtuple 

import polars as pl

SEMO_MINIMAL_COST_URL = "https://reports.sem-o.com/documents/PUB_30MinImbalCost_{period}.xml"
SEMO_PERIOD_FORMAT = "%Y%m%d%H%M"

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
   
def period_to_fetch(run_time_iso: str):
    """
    Figure's out which period to fetch

    Returns:
        The 30 mnute period to fetch as a string e.g. 202312251900

    """

    run_time = datetime.fromisoformat(run_time_iso)
    period = datetime(run_time.year,
        run_time.month,
        run_time.day,
        run_time.hour,
        30 if run_time.minute >= 30 else 0,
        0,
        tzinfo=timezone.utc)
    
    return period.strftime(SEMO_PERIOD_FORMAT)

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
        raise Exception(f"Semo data unavailable for period: {period}")

    return response.text


def parse_semo_xml(period: str, semo_xml: str):
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
        xml_as_dict =  {"period": period,
                        "imbalance_volume": float(imbalance_xml.attrib.get('ImbalanceVolume')),
                        "imbalance_price": float(imbalance_xml.attrib.get('ImbalancePrice')),
                        "imbalance_cost": float(imbalance_xml.attrib.get('ImbalanceCost'))}
    except:
        raise Exception(f"Unable to parse Semo xml.")
    
    return xml_as_dict

def main(run_time: str, semo_df_path: str):
    """
    Runs the main extract_semo job. 

    Args:
    - run_time (str): The run time of the job which determines the period we fetch
    - semo_df_path (str): The location where the semo dataframe is saved.

    """

    period = period_to_fetch(run_time_iso=run_time)
    semo_xml = fetch_semo_xml(period=period)
    semo_data = parse_semo_xml(period=period, semo_xml=semo_xml)
    new_df = pl.DataFrame(semo_data)
    existing_semo_df = read_df(path=semo_df_path)
    
    if existing_semo_df is not None:
        new_df = pl.concat([existing_semo_df, new_df])

    new_df.write_parquet(file=semo_df_path)
