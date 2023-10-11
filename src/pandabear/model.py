import dataclasses
from typing import Any

import numpy as np
import pandas as pd

from .model_components import CHECK_NAME_FUNCTION_MAP, Field

TYPE_DTYPE_MAP = {
    str: np.dtype("O"),
}


@dataclasses.dataclass
class DataFrameModel:
    @classmethod
    def _get_names_and_types(cls):
        return cls.__annotations__

    @classmethod
    def _get_fields(cls):
        names_types = cls._get_names_and_types()
        return {name: getattr(cls, name) for name in names_types}

    @staticmethod
    def _validate_series(se: pd.Series, field: Field, typ: Any):
        dtype = TYPE_DTYPE_MAP.get(typ, typ)
        if se.dtype != dtype:
            raise TypeError(f"Expected `{se.name}` dtype {dtype} but found {se.dtype}")

        for check_name, check_func in CHECK_NAME_FUNCTION_MAP.items():
            check_value = getattr(field, check_name)
            if check_value is not None:
                if not check_func(se, check_value):
                    raise ValueError(f"Column`{se.name}` did not pass check `{check_name} {check_value}`")

    @staticmethod
    def _select_series_by_name(df: pd.DataFrame, name: str) -> pd.Series:
        if not name in df.columns:
            raise ValueError(f"Column `{name}` was not found in dataframe")
        return df[name]

    @staticmethod
    def _select_series_by_alias(df: pd.DataFrame, field: Field) -> list[pd.Series]:
        if field.regex:
            return [df[col] for col in df.filter(regex=field.alias, axis=1).columns]
        else:
            return [df[field.alias]]

    @classmethod
    def validate(cls, df: pd.DataFrame):
        name_types = cls._get_names_and_types()
        name_fields = cls._get_fields()
        for name in name_types:
            typ = name_types[name]
            field = name_fields[name]
            if field.alias is not None:
                for series in cls._select_series_by_alias(df, field):
                    cls._validate_series(series, field, typ)
            else:
                series = cls._select_series_by_name(df, name)
                cls._validate_series(series, field, typ)
