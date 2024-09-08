from enum import Enum
import polars as pl

class Table:

    def __init__(self, name: str, path: str, schema: dict):
        self.name = name
        self.schema = schema
        self.path = path

class Tables(Enum):
    IMBALANCE_PRICE = Table(name="imbalance_price",
                            schema={"period": pl.Utf8, 
                                    "imbalance_volume": pl.Float32, 
                                     "imbalance_price": pl.Float32,
                                     "imbalance_cost": pl.Float32}
                     )
  