from typing import Type

import pandas as pd

from pandabear.model import DataFrameModel, SeriesModel


class DataFrame(pd.DataFrame, DataFrameModel):
    @classmethod
    def __class_getitem__(cls, typ: Type[DataFrameModel]):
        """Enable DataFrame[MySchema] syntax in type hints.

        Setting `DataFrame[MySchema]` to return `pd.DataFrame | MySchema` allows
        `pandabear` to play nice with other runtime type checkers such as `pydantic`
        and `beartype`. Notice how the `check_schemas` decorator handles type hints
        in case the the value is a `pd.DataFrame`. It will check if the type hint
        is a `pd.DataFrame | MySchema` and if so, it will validate the dataframe
        against `MySchema`.
        """
        return pd.DataFrame | typ


class Series(pd.Series, SeriesModel):
    @classmethod
    def __class_getitem__(cls, typ: Type[SeriesModel]):
        """Enable Series[MySeries] syntax in type hints.

        Setting e.g. `Series[MySeries]` to return `pd.Series | MySeries` allows
        `pandabear` to play nice with other runtime type checkers such as `pydantic`
        and `beartype`. Notice how the `check_schemas` decorator handles type hints
        in case the the value is a `pd.Series`. It will check if the type hint
        is a `pd.Series | MySeries` and if so, it will validate the Series
        against `MySeries`.
        """
        return pd.Series | typ
