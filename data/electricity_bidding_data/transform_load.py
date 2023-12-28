import polars as pl
import requests

SEMO_MINIMAL_COST_URL = "https://reports.sem-o.com/documents/PUB_30MinImbalCost_202312251900.xml"

def fetch_semo_data():
  r = requests.get(SEMO_MINIMAL_COST_URL)
  print(r.txt)