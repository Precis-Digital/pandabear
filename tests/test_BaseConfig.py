from pandabear.model import DataFrameModel, Field
from pandabear.model_components import BaseConfig


class MyConfig:
    strict = "filter"


class MySchema(DataFrameModel):
    Config = MyConfig
    a: int
    b: str


Config = MySchema._get_config()
