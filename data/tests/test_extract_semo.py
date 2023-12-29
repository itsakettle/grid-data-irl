import os
import pytest
import polars as pl
from datetime import datetime
from electricity_bidding_data import extract_semo

def test_init_df():
    df = extract_semo.init_df(periods=["one", "two"], imbalance_prices=[1.1, 1.2])
    result = df.filter(pl.col("period") == "two").rows()[0][1]
    assert result == 1.2


@pytest.fixture
def prepare_df():
    temp_path = "/usr/src/app/semo_test.parquet"
    df = extract_semo.init_df(periods=["one", "two"], imbalance_prices=[1.1, 1.2])
    df.write_parquet(temp_path)
    yield temp_path
    os.remove(temp_path)

def test_read_df(prepare_df):
    df = extract_semo.read_df(path="/usr/src/app/does_not_exist.parquet")
    assert df is None

    df = extract_semo.read_df(path=prepare_df)
    result = df.filter(pl.col("period") == "two").rows()[0][1]
    assert result == 1.2

def test_period_to_fetch():
    early_in_the_hour = datetime(2023, 12, 28, 11, 11, 11)
    early_in_the_hour_period = extract_semo.period_to_fetch(early_in_the_hour)
    assert early_in_the_hour_period == "202312281100"

    late_in_the_hour = datetime(2023, 12, 28, 11, 31, 11)
    early_in_the_hour_period = extract_semo.period_to_fetch(late_in_the_hour)
    assert early_in_the_hour_period == "202312281130"

def test_parse_semo_schema():
    xml = """
    <OutboundData xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="mi-outbound-reports-isem.xsd" DatasetName="PUB_30MinImbalCost" DatasetType="HALF_HOURLY" Date="2023-12-26" DateType="TRADE" PublishTime="2023-12-26T12:30:05">
    <PUB_30MinImbalCost ROW="1" StartTime="2023-12-26T11:30:00" EndTime="2023-12-26T12:00:00" ImbalanceVolume="31.987" ImbalancePrice="125.96" ImbalanceCost="4029.08252"/>
    </OutboundData>
    """
    result = extract_semo.parse_semo_schema(xml)
    expected = {"imbalance_volume": 31.987,
                        "imbalance_price": 125.96,
                        "imbalance_cost": 4029.08252}
    assert result == expected

    

