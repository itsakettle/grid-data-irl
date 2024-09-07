import polars as pl

tables = [{"system_imbalance_price": {"period": pl.Utf8, 
                      "imbalance_volume": pl.Float32, 
                      "imbalance_price": pl.Float32, 
                      "imbalance_cost": pl.Float32}}]

def append(column_data: dict, to_delta_path: str, schema: dict):
    df = pl.DataFrame(data=column_data, schema=schema)
    df.write_delta(target=to_delta_path, mode="append")


