import os
import pytest
import polars as pl
from datetime import datetime
from electricity_bidding_data import extract_semo

@pytest.fixture
def prepare_df():
    temp_path = "/usr/src/app/semo_test.parquet"
    test_data = {"period": ["202312281100", "202312281200"],
                 "imbalance_volume": [100.1, 100.2],
                 "imbalance_price": [5.1, 5.2],
                 "imbalance_cost": [1.1, 1.2]}
    test_df = pl.DataFrame(test_data)
    test_df.write_parquet(temp_path)
    yield temp_path
    os.remove(temp_path)

def test_read_df(prepare_df):
    df = extract_semo.read_df(path="/usr/src/app/does_not_exist.parquet")
    assert df is None

    df = extract_semo.read_df(path=prepare_df)
    result = df.filter(pl.col("period") == "202312281200")["imbalance_price"][0]
    assert result == 5.2

def test_period_to_fetch():
    early_in_the_hour = "2023-12-28T11:11:11"
    early_in_the_hour_period = extract_semo.period_to_fetch(early_in_the_hour)
    assert early_in_the_hour_period == "202312281100"

    late_in_the_hour = "2023-12-28T11:31:11"
    early_in_the_hour_period = extract_semo.period_to_fetch(late_in_the_hour)
    assert early_in_the_hour_period == "202312281130"

def test_parse_semo_schema():
    xml = """
    <OutboundData xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="mi-outbound-reports-isem.xsd" DatasetName="PUB_30MinImbalCost" DatasetType="HALF_HOURLY" Date="2023-12-26" DateType="TRADE" PublishTime="2023-12-26T12:30:05">
    <PUB_30MinImbalCost ROW="1" StartTime="2023-12-26T11:30:00" EndTime="2023-12-26T12:00:00" ImbalanceVolume="31.987" ImbalancePrice="125.96" ImbalanceCost="4029.08252"/>
    </OutboundData>
    """
    result = extract_semo.parse_semo_xml("202312261130", xml)
    expected = {"period": "202312261130",
                "imbalance_volume": 31.987,
                "imbalance_price": 125.96,
                "imbalance_cost": 4029.08252}
    assert result == expected

def test_main():

    

