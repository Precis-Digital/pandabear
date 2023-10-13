import dataclasses
from typing import Any

import numpy as np
import pandas as pd

from pandabear.column_checks import CHECK_NAME_FUNCTION_MAP
from pandabear.model_components import Field, BaseConfig
from pandabear.index_type import check_type_is_index, get_index_dtype

TYPE_DTYPE_MAP = {
    str: np.dtype("O"),
}

@dataclasses.dataclass
class BaseModel:

    Config: BaseConfig = BaseConfig

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
    def _get_config(cls):
        return BaseConfig._override(cls.Config)

    @classmethod
    def _get_names_and_types(cls):
        return cls.__annotations__

    @classmethod
    def _get_index_names(cls):
        return [c for c, v in cls._get_names_and_types().items() if check_type_is_index(v)]

    @classmethod
    def _get_column_names(cls):
        return [c for c, v in cls._get_names_and_types().items() if not check_type_is_index(v)]

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
    def _select_series_by_alias(df: pd.DataFrame, field: Field) -> list[pd.Series]:
        if field.regex:
            return [df[col] for col in df.filter(regex=field.alias, axis=1).columns]
        else:
            return [df[field.alias]]

    @classmethod
    def validate(cls, df: pd.DataFrame):
        name_types = cls._get_names_and_types()
        name_fields = cls._get_fields()
        index_names = cls._get_index_names()

        for name in name_types:
            is_index = name in index_names
            typ = get_index_dtype(name_types[name]) if is_index else name_types[name]
            field = name_fields[name]

            if is_index:
                series = df.index.get_level_values(name)
                cls._validate_series(series, field, typ)

            elif field.alias is not None:
                for series in cls._select_series_by_alias(df, field):
                    cls._validate_series(series, field, typ)
            else:
                series = cls._select_series_by_name(df, name)
                cls._validate_series(series, field, typ)

        cls._validate_multiindex(df)

        return cls._validate_columns(df)

    @classmethod
    def _validate_columns(cls, df):
        Config = cls._get_config()

        if Config.strict == 'filter':
            return df[cls._get_column_names()].copy()

        if Config.strict:
            if set(cls._get_column_names()) != set(df.columns):
                raise ValueError("DataFrame columns did not match expected columns")

        if Config.ordered:
            if cls._get_column_names() != list(df.columns):
                raise ValueError("DataFrame columns did not match expected columns")
        return df

    @classmethod
    def _validate_multiindex(cls, df):
        Config = cls._get_config()
        if Config.multiindex_strict:
            if not isinstance(df.index, pd.MultiIndex):
                raise ValueError("Expected MultiIndex")
            if not set(cls._get_index_names()) == set(list(df.index.names)):
                raise ValueError("MultiIndex names did not match expected names")
        if Config.multiindex_ordered:
            if cls._get_index_names() != list(df.index.names):
                raise ValueError("MultiIndex names did not match expected names")
            if not df.index.is_lexsorted():
                raise ValueError("MultiIndex was not lexsorted")
        if Config.multiindex_unique:
            if not df.index.is_unique:
                raise ValueError("MultiIndex was not unique")



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
