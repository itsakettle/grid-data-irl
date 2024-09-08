import polars as pl
from tables import Tables

def append(column_data: dict, table: Tables):
    df = pl.DataFrame(data=column_data, schema=schema)
    df.write_delta(target=to_delta_path, mode="append")


