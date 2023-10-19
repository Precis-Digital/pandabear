import dataclasses
from types import NoneType
from typing import Any, Optional

import numpy as np
import pandas as pd

from pandabear.column_checks import CHECK_NAME_FUNCTION_MAP, ColumnCheckError
from pandabear.exceptions import MissingColumnsError, SchemaDefinitionError
from pandabear.index_type import get_index_dtype, type_is_index
from pandabear.model_components import BaseConfig, Field

TYPE_DTYPE_MAP = {
    str: np.dtype("O"),
}


# @dataclasses.dataclass
class BaseModel:
    Config: BaseConfig = BaseConfig

    @classmethod
    def _get_config(cls):
        return BaseConfig._override(cls.Config)

    @classmethod
    def _validate_series(cls, se: pd.Series, field: Field, typ: Any, coerce: bool) -> pd.Series:
        dtype = TYPE_DTYPE_MAP.get(typ, typ)

        if se.dtype != dtype:
            if coerce:
                se = se.astype(typ)
            else:
                raise TypeError(f"Expected `{se.name}` dtype {dtype} but found {se.dtype}")

        for check_name, check_func in CHECK_NAME_FUNCTION_MAP.items():
            check_value = getattr(field, check_name)
            if check_value is not None:
                result = check_func(series=se, value=check_value)
                if not result.all():
                    raise ColumnCheckError(check_name=check_name, check_value=check_value, series=se, result=result)
        return se


class DataFrameModel(BaseModel):
    @classmethod
    def _get_index_names(cls):
        return [c for c, v in cls.__annotations__.items() if type_is_index(v)]

    @classmethod
    def _get_name_field_map(cls) -> dict[str, tuple[type, bool, bool, Field]]:
        """Get a dictionary mapping between index/column names and `Field`.

        Note: The `getattr(cls, name) if hasattr(cls, name) else Field()` bit
            assigns a `Field` value to columns that are defined in the schema
            without a `Field`. This is useful, because it allows a more concise
            API where columns that don't have aliases or need checks can be
            defined as an annotation without a `Field` object. E.g.:
            >>> class MySchema(DataFrameModel):
            >>>     column_a: int
            >>>     column_b: str = Field(alias="column_b_alias")
            Here `column_a` has no checks and no alias, so it is defined simply
            as an annotation.

        Returns:
            name_field_map (dict): A dictionary mapping index/column names to a
                tuple containing (type, optional, is_index, field)
        """
        name_field_map = {}
        for name, typ in cls.__annotations__.items():
            typ, optional = cls._check_optional_type(typ)
            is_index = False
            if type_is_index(typ):
                typ = get_index_dtype(typ)
                is_index = True
            name_field_map[name] = (typ, optional, is_index, getattr(cls, name) if hasattr(cls, name) else Field())
        return name_field_map

    @staticmethod
    def _select_series(df: pd.DataFrame, column_name: str, optional: bool = True) -> Optional[list[pd.Series]]:
        try:
            return [df[column_name]]
        except KeyError:
            # When this happens we can deduce that the corresponding column is
            # optional (otherwise an error would have been raised in
            # _validate_columns).
            assert (
                optional
            ), "This should not happen. Looks like columns were not properly filtered in `_validate_columns`"
            return []

    @staticmethod
    def _select_series_by_regex(df: pd.DataFrame, alias: str) -> list[pd.Series]:
        return [df[col] for col in df.filter(regex=alias, axis=1).columns]

    @staticmethod
    def _check_optional_type(typ: type) -> tuple[type, bool]:
        """
        Check if a type is optional and return the non-optional type.

        Args:
            typ (type): The type to check.

        Returns:
            typ: The non-optional type.
            optional: A boolean indicating whether the type is optional.

        Raises:
            TypeError: If `typ` is not a type.
        """
        optional = False
        if hasattr(typ, "__args__") and type(None) in typ.__args__:
            optional = True
            if len(typ.__args__) == 2:
                typ = typ.__args__[0]
            else:
                typ = typ.__args__[:-1]
        return typ, optional

    @classmethod
    def validate(cls, df: pd.DataFrame):
        """Validate a dataframe against the schema.

        This method also acts as a filter, that (depending on the config) will
        pass `df` through with coerced types, filtered columns, ordered columns
        or as-is.

        Args:
            df (pandas.DataFrame): The dataframe to validate.

        Returns:
            pandas.DataFrame: The validated dataframe.

        Raises:
            MissingColumnsError: If a column name/alias/regex is not in `df`.
                This happens when a column is defined in the schema but not in
                `df`. Or (more often than you'd think) because of typos ^^.
            SchemaDefinitionError: If there is a problem with the schema. This
                could e.g. happen when there is an overlap between the columns
                in `df` that different schema fields match, so that it is not
                clear which field should be used to validate a column.
        """
        name_field_map = cls._get_name_field_map()
        Config = cls._get_config()

        # Check that indices and columns in `df` match schema. The only errors
        # that should be thrown here relate to schema errors or missing columns
        # in `df`. Furthermore, this method may filter, coerce or order `df`
        # depending on user-provided specifications in `Config`.
        ...
        df = cls._validate_columns(df, name_field_map, Config)

        # Validate `df` against schema. The only errors that should be raises
        # in this step are from dtype checks and `Field` checks:
        for name, (typ, optional, is_index, field) in name_field_map.items():
            # Select the column (or columns) in `df` that match the field.
            # ... when index column
            if is_index:
                matched_series = [df.index.get_level_values(field.alias or name).to_series()]
                if field.regex:
                    raise NotImplementedError("Regex not implemented for index aliases")

            # ... when column has aliased name
            elif field.alias is not None:
                if field.regex:
                    matched_series = cls._select_series_by_regex(df, field.alias)
                else:
                    matched_series = cls._select_series(df, field.alias, optional)

            # ... when column name is attribute name (not alias)
            else:
                matched_series = cls._select_series(df, name, optional)

            # Validate the selected column(s) against the field and type.
            for series in matched_series:
                series = cls._validate_series(series, field, typ, Config.coerce)
                if Config.coerce:
                    df[series.name] = series

        cls._validate_multiindex(df)

        cls._validate_custom_checks(df)
        return df

    @classmethod
    def _select_matching_columns(
        cls, df: pd.DataFrame, name_field_map: dict[str, tuple[type, bool, bool, Field]]
    ) -> list[str]:
        """
        Select columns in `df` that match the schema.

        If a column is defined in the schema it *must* be present in `df`.
        This function serves the important purpose of raising errors when
        columns in `df` seem to be *missing* when compared to the schema.

        Args:
            df (pandas.DataFrame): The dataframe to select columns from.
            name_field_map (dict): A dictionary mapping column names to their
                corresponding Field objects.

        Returns:
            list: A list of column names in `df` that match the schema.

        Raises:
            SchemaDefinitionError: If a column or alias is not found in `df`, is already
                matched by another field.
            MissingColumnsError: If a column is defined in the schema but not
                found in `df`.
        """
        matching_columns_in_df = []
        for column, (_, optional, is_index, field) in name_field_map.items():
            if is_index:
                continue
            if field.alias is not None:
                if field.regex:
                    matched = df.filter(regex=field.alias, axis=1).columns
                    if len(matched) == 0 and not optional:
                        raise MissingColumnsError(
                            f"No columns match regex `{field.alias}` for field `{column}` in schema `{cls.__name__}`"
                        )
                    elif len(already_matched := set(matched) & set(matching_columns_in_df)) > 0:
                        raise SchemaDefinitionError(
                            f"Regex `{field.alias}` for field `{column}` in schema `{cls.__name__}` matched columns {already_matched} already matched by another field."
                        )
                    matching_columns_in_df.extend(matched)
                else:
                    if field.alias not in df.columns and not optional:
                        raise MissingColumnsError(
                            f"No columns match alias `{field.alias}` for field `{column}` in schema `{cls.__name__}`."
                        )
                    elif field.alias in matching_columns_in_df:
                        raise SchemaDefinitionError(
                            f"Alias `{field.alias}` for field `{column}` in schema `{cls.__name__}` is used by another field."
                        )
                    matching_columns_in_df.append(field.alias)
            else:
                if column not in df.columns and not optional:
                    raise MissingColumnsError(f"No columns match column name `{column}` in schema `{cls.__name__}`.")
                elif column in matching_columns_in_df:
                    raise SchemaDefinitionError(
                        f"Column `{column}` in schema `{cls.__name__}` is used by another field."
                    )
                matching_columns_in_df.append(column)
        return matching_columns_in_df

    @classmethod
    def _validate_custom_checks(cls, df):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if not hasattr(attr, "__check__"):
                continue

            check_columns: list[str] | NoneType = getattr(attr, "__check__")

            if check_columns is None:
                # assumes check is for whole df
                if not attr(df):
                    raise ValueError(f"DataFrame did not pass custom check `{attr_name}`")
                continue

            if any(undefined_columns := [c for c in check_columns if c not in cls.__annotations__]):
                raise SchemaDefinitionError(
                    f"Decorator on custom check `{attr_name}` references undefined columns {undefined_columns}. Values passed to the `check` decorator must reference columns defined in the schema."
                )

            for column in check_columns:
                if not attr(df[column]):
                    raise ValueError(f"Column `{column}` did not pass custom check `{attr_name}`")

    @classmethod
    def _validate_columns(
        cls, df: pd.DataFrame, name_field_map: dict[str, tuple[type, bool, bool, Field]], Config: BaseConfig
    ) -> pd.DataFrame:
        """Validate column names in `df` against the schema.

        Raise approproate errors if columns are missing or if there is an
        overlap between columns that different schema fields match.

        This method also acts as a filter, that (depending on the config) will
        pass `df` through with coerced types, filtered columns, ordered columns
        or as-is.
        """
        matching_columns_in_df = cls._select_matching_columns(df, name_field_map)

        # Drop columns in `df` that do not match the schema
        if Config.filter:
            ordered_columns_in_df = [col for col in df.columns if col in matching_columns_in_df]
            df = df.copy()[ordered_columns_in_df]

        # Complain about columns in `df` that are not defined in the schema
        elif Config.strict:
            if len(unexpected_columns := set(df.columns) - set(matching_columns_in_df)) > 0:
                raise KeyError(f"Columns {unexpected_columns} are present in `df` but not in schema")

        # Complain if the order of columns in `df` does not match the order in
        # which they are defined in the schema
        if Config.ordered:
            if matching_columns_in_df != list(df.columns):
                raise ValueError("Columns in `df` are not ordered as in schema")

        return df

    @classmethod
    def _validate_multiindex(cls, df: pd.DataFrame):
        index_names = cls._get_index_names()

        Config = cls._get_config()

        if (index_names == []) and (df.index.names == [None]):
            # no index defined in schema, and no index defined in dataframe
            return

        if set(index_names) - set(df.index.names):
            # all schema index names must be in dataframe index names
            raise ValueError(f"Index levels {set(index_names) - set(df.index.names)} missing in df")

        if Config.multiindex_strict:
            if not set(index_names) == set(list(df.index.names)):
                raise ValueError("MultiIndex names did not match expected names")

        if Config.multiindex_ordered:
            # assume order implies strict
            if cls._get_index_names() != list(df.index.names):
                raise ValueError("MultiIndex names did not match expected names")

        if Config.multiindex_sorted:
            if not (df.index.is_monotonic_increasing or df.index.is_monotonic_decreasing):
                raise ValueError("MultiIndex not sorted")

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
        Config = cls._get_config()
        cls._validate_series(series, field, value_type, Config.coerce)
