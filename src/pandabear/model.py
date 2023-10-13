import dataclasses
from typing import Any

import numpy as np
import pandas as pd

from pandabear.column_checks import CHECK_NAME_FUNCTION_MAP
from pandabear.model_components import Field

TYPE_DTYPE_MAP = {
    str: np.dtype("O"),
}


@dataclasses.dataclass
class BaseModel:
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


class DataFrameModel(BaseModel):
    @classmethod
    def _get_names_and_types(cls):
        return cls.__annotations__

    @classmethod
    def _get_fields(cls):
        names_types = cls._get_names_and_types()
        return {name: getattr(cls, name) for name in names_types}

    @staticmethod
    def _select_series_by_name(df: pd.DataFrame, name: str) -> pd.Series:
        if not name in df.columns:
            raise ValueError(f"Column `{name}` was not found in dataframe")
        return df[name]

    @staticmethod
    def _select_series_by_alias(df: pd.DataFrame, alias: str, regex: bool) -> list[pd.Series]:
        if regex:
            return [df[col] for col in df.filter(regex=alias, axis=1).columns]
        else:
            return [df[alias]]

    @classmethod
    def validate(cls, df: pd.DataFrame):
        # Validate `Fields`
        name_types = cls._get_names_and_types()
        name_fields = cls._get_fields()
        for name in name_types:
            typ = name_types[name]
            field = name_fields[name]
            if field.alias is not None:
                for series in cls._select_series_by_alias(df, field.alias, field.regex):
                    cls._validate_series(series, field, typ)
            else:
                series = cls._select_series_by_name(df, name)
                cls._validate_series(series, field, typ)

        # Validate `@check` decorated functions
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, "__check__"):
                check_columns: list[str] = getattr(attr, "__check__")

                if getattr(attr, "__regex__"):
                    new_check_columns = []
                    for column in check_columns:
                        matched_columns = df.filter(regex=column, axis=1).columns
                        if len(matched_columns) == 0:
                            raise ValueError(f"No columns match regex `{column}`")
                        new_check_columns.extend(matched_columns)
                    check_columns = new_check_columns

                for column in check_columns:
                    series = cls._select_series_by_name(df, column)
                    if not attr(series):
                        raise ValueError(f"Column `{column}` did not pass custom check `{attr_name}`")


class SeriesModel(BaseModel):
    @classmethod
    def _get_value_name_and_type(cls):
        return list(cls.__annotations__.items())[0]

    @classmethod
    def _get_field(cls):
        value_name, _ = cls._get_value_name_and_type()
        return getattr(cls, value_name)

    @classmethod
    def validate(cls, series: pd.Series):
        _, value_type = cls._get_value_name_and_type()
        field = cls._get_field()
        cls._validate_series(series, field, value_type)
