from typing import Type

import pandas as pd

from .model import DataFrameModel


class DataFrame(pd.DataFrame, DataFrameModel):
    @classmethod
    def __class_getitem__(cls, item: Type[DataFrameModel]):
        """Enable DataFrame[MySchema] syntax in type hints.
        
        Setting `DataFrame[MySchema]` to return `pd.DataFrame | MySchema` allows
        `pandabear` to play nice with other runtime type checkers such as `pydantic`
        and `beartype`. Notice how the `check_types` decorator handles type hints
        in case the the value is a `pd.DataFrame`. It will check if the type hint
        is a `pd.DataFrame | MySchema` and if so, it will validate the dataframe
        against `MySchema`.
        """
        return pd.DataFrame | item