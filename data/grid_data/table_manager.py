from collections import namedtuple
from enum import Enum
from pathlib import Path
import polars as pl

TableInfo = namedtuple("TableInfo", ["name", "schema"])

class Tables(Enum):
    IMBALANCE_PRICE = TableInfo(name="imbalance_price",
                                schema={"period": pl.Utf8, 
                                    "imbalance_volume": pl.Float64, 
                                     "imbalance_price": pl.Float64,
                                     "imbalance_cost": pl.Float64})

class TableManager:

    def __init__(self, base_path):
        self.base_path = base_path

    def append(self, column_data: dict, to_table: Tables):
        table_info = to_table.value
        df = pl.DataFrame(data=column_data, schema=table_info.schema)
        path = Path(self.base_path) / table_info.name
        df.write_delta(target=path, mode="append")


