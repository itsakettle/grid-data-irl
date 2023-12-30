import os
import pytest
import polars as pl
from datetime import datetime
from electricity_bidding_data import extract_semo

SAMPLE_SEMO_XML = """
    <OutboundData xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="mi-outbound-reports-isem.xsd" DatasetName="PUB_30MinImbalCost" DatasetType="HALF_HOURLY" Date="2023-12-26" DateType="TRADE" PublishTime="2023-12-26T12:30:05">
    <PUB_30MinImbalCost ROW="1" StartTime="2023-12-26T11:30:00" EndTime="2023-12-26T12:00:00" ImbalanceVolume="31.987" ImbalancePrice="125.96" ImbalanceCost="4029.08252"/>
    </OutboundData>
"""

TEST_DF_PATH = "/usr/src/app/semo_test.parquet"

@pytest.fixture
def prepare_saved_df():

    test_data = {"period": ["202312281100", "202312281200"],
                 "imbalance_volume": [100.1, 100.2],
                 "imbalance_price": [5.1, 5.2],
                 "imbalance_cost": [1.1, 1.2]}
    test_df = pl.DataFrame(test_data)
    test_df.write_parquet(TEST_DF_PATH)
    yield
    os.remove(TEST_DF_PATH)

def test_read_df(prepare_saved_df):
    df = extract_semo.read_df(path="/usr/src/app/does_not_exist.parquet")
    assert df is None

    df = extract_semo.read_df(path=TEST_DF_PATH)
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
    result = extract_semo.parse_semo_xml("202312261130", SAMPLE_SEMO_XML)
    expected = {"period": "202312261130",
                "imbalance_volume": 31.987,
                "imbalance_price": 125.96,
                "imbalance_cost": 4029.08252}
    assert result == expected

@pytest.fixture
def mock_fetch_semo(mocker):
    mock = mocker.patch('electricity_bidding_data.extract_semo.fetch_semo_xml', return_value=SAMPLE_SEMO_XML)
    yield mock

def test_main_existing_data(mock_fetch_semo, prepare_saved_df):
    run_time = "2023-12-26T11:35:12"
    extract_semo.main(run_time, TEST_DF_PATH)

    df = pl.read_parquet(TEST_DF_PATH)
    price_value = df.filter(pl.col("period") == "202312261130")["imbalance_price"][0]
    assert df.height == 3
    assert price_value == 125.96

def test_main_no_existing_data(mock_fetch_semo):
    run_time = "2023-12-26T11:35:12"
    extract_semo.main(run_time, TEST_DF_PATH)

    df = pl.read_parquet(TEST_DF_PATH)
    price_value = df.filter(pl.col("period") == "202312261130")["imbalance_price"][0]
    assert df.height == 1
    assert price_value == 125.96

    

