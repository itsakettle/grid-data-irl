import pytest
from data.electricity_bidding_data import transform_load

@pytest.fixture
def data():
    return [list(range(100)), list(range(200))]

def test_semo_fetch(data):
    transform_load.fetch_semo_data()