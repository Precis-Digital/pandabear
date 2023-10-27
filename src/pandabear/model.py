import re
from types import NoneType
from typing import Any, Union

import numpy as np
import pandas as pd

from pandabear.column_checks import CHECK_NAME_FUNCTION_MAP
from pandabear.exceptions import (
    CoersionError,
    ColumnCheckError,
    MissingColumnsError,
    MissingIndexError,
    SchemaDefinitionError,
    SchemaValidationError,
)
from pandabear.model_components import (
    BaseConfig,
    Field,
    FieldInfo,
    Index,
    get_index_type,
    is_type_index,
)

TYPE_DTYPE_MAP = {
    str: np.dtype("O"),
}


# @dataclasses.dataclass
class BaseModel:
    Config: BaseConfig = BaseConfig

    @classmethod
    def _get_config(cls):
        """Get the config for the model.

        Schema definitions that inherit from this class often overrides the
        `Config` class attribute, like e.g.:

        >>> class MySchema(DataFrameModel):
        >>>     class Config:
        >>>         coerce = True

        This is basically a complete override of `cls.Config` that removes all
        the other (default) `Config` attributes. This method is used as a getter
        to retrieve the `Config` class attribute, with all the default values
        intact.
        """
        return BaseConfig._override(cls.Config)

    @classmethod
    def _validate_series(cls, se: pd.Series, field: Field, typ: Any, coerce: bool) -> pd.Series:
        """Validate a series against a field and type.

        Args:
            se (pd.Series): The series to validate.
            field (Field): The field to validate against.
            typ (Any): The type to validate against.
            coerce (bool): Whether to coerce the series to the type of the
                field.

        Returns:
            pd.Series: The validated series.
        """
        dtype = TYPE_DTYPE_MAP.get(typ, typ)

        if se.dtype != dtype:
            if coerce:
                try:
                    se = se.astype(typ)
                except ValueError:
                    raise CoersionError(f"Could not coerce `{se.name}` with dtype {se.dtype} to {dtype}")
            else:
                raise SchemaValidationError(f"Expected `{se.name}` with dtype {dtype} but found {se.dtype}")

        for check_name, check_func in CHECK_NAME_FUNCTION_MAP.items():
            check_value = getattr(field, check_name)
            if check_value is not None:
                result = check_func(series=se, value=check_value)
                if not result.all():
                    raise ColumnCheckError(check_name=check_name, check_value=check_value, series=se, result=result)
        return se


class DataFrameModel(BaseModel):
    @classmethod
    def _get_schema_map(cls) -> dict[str, FieldInfo]:
        """Get a convenient representation of the schema.

        This method builds a dictionary that maps index/column names to a
        tuple containing (type, optional, is_index, field). This is a
        convenient representation of the schema, because it allows easy access
        to otherwise hard-to-get information about the schema.

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
            schema_map (dict): A dictionary mapping index/column names to a
                tuple containing (type, optional, is_index, field)
        """
        schema_map = {}
        for name, typ in cls.__annotations__.items():
            typ, optional = cls._check_optional_type(typ)
            is_index = is_type_index(typ, name, cls.__name__)
            if is_index:
                # `typ` is like `Union[Index, int]` (meaning the user provided `Index[int]`)
                # or a bare pandas.index type.
                typ = get_index_type(typ)

            schema_map[name] = (typ, optional, is_index, getattr(cls, name) if hasattr(cls, name) else Field())
        return schema_map

    @staticmethod
    def _check_optional_type(typ: type) -> tuple[type, bool]:
        """Check if a type is optional and return the non-optional type."""
        optional = False
        if hasattr(typ, "__args__") and type(None) in typ.__args__:
            optional = True
            typ = Union[tuple(arg for arg in typ.__args__ if arg is not type(None))]
        return typ, optional

    @staticmethod
    def override_level(
        index: pd.MultiIndex | pd.Index, index_level: str, series: pd.Series
    ) -> pd.MultiIndex | pd.Index:
        """Override a level in a MultiIndex or Index with a new series."""
        if isinstance(index, pd.MultiIndex):
            df_reset = index.to_frame(index=False)
            if index_level not in df_reset.columns:
                raise ValueError(f"Index level '{index_level}' not found in MultiIndex.")
            df_reset[index_level] = series.values
            new_index = pd.MultiIndex.from_frame(df_reset)
        else:
            if index.name != index_level:
                raise ValueError(f"Index name '{index.name}' does not match given index_level '{index_level}'.")
            new_index = pd.Index(series.values, name=index_level)
        return new_index

    @staticmethod
    def _select_index_series(df: pd.DataFrame, level: str, optional: bool = True) -> list[pd.Series]:
        """Select a series from a dataframe by column name.

        Return a list containing maximally 1 series. Reason for this is that
        series are validated in a loop, so returning a list is convenient.
        """
        try:
            return [df.index.get_level_values(level).to_series()]
        except KeyError:
            # When this happens we can deduce that the corresponding column is
            # optional (otherwise an error would have been raised in
            # _validate_columns).
            assert (
                optional
            ), "This should not happen. Looks like columns were not properly filtered in `_validate_columns`"
            return []

    @staticmethod
    def _select_series(df: pd.DataFrame, column_name: str, optional: bool = True) -> list[pd.Series]:
        """Select a series from a dataframe by column name.

        Return a list containing maximally 1 series. Reason for this is that
        series are validated in a loop, so returning a list is convenient.
        """
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
    def _select_index_series_by_regex(df: pd.DataFrame, alias: str) -> list[pd.Series]:
        """Select a series from a dataframe by regex."""
        return [
            df.index.get_level_values(level).to_series()
            for level in df.index.names
            if re.match(alias, level) is not None
        ]

    @staticmethod
    def _select_series_by_regex(df: pd.DataFrame, alias: str) -> list[pd.Series]:
        """Select a series from a dataframe by regex."""
        return [df[col] for col in df.filter(regex=alias, axis=1).columns]

    @classmethod
    def _validate_custom_checks(cls, df: pd.DataFrame):
        """Validate custom checks defined on the schema.

        The `check` decorator can be used to define custom checks on the
        schema. This method will loop through all attributes on the schema and
        check if they have the `__check__` attribute. If they do, it means they
        are decorated with the `check` decorator and should be run on the
        dataframe.
        """
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
    def _validate_schema(cls, schema_map: dict[str, FieldInfo]):
        """Validate the schema map.

        This method will raise errors if there are obvious problems with the
        schema, like e.g. missing aliases when regex=True, number checks on
        non-numeric columns, etc.
        """
        using_check_index_name = []
        for name, (typ, optional, is_index, field) in schema_map.items():
            # Check that there are not multiple index columns if `check_index_name` is False
            if is_index:
                using_check_index_name.append(field.check_index_name)
                if len(using_check_index_name) > 1 and not all(using_check_index_name):
                    raise SchemaDefinitionError(
                        f"Schema `{cls.__name__}` defines multiple indices where one or more have `check_index_name=False`. MultiIndex schemas, require name checks."
                    )

            # Check that regex is not used when alias is not defined
            if field.regex and field.alias is None:
                raise SchemaDefinitionError(
                    f"Regex is used for `{name}` in schema `{cls.__name__}`, but no alias is defined."
                )

            # Check that string checks arenot used on non-string columns
            if any(
                [
                    field.str_contains is not None,
                    field.str_endswith is not None,
                    field.str_startswith is not None,
                ]
            ) and typ not in [str]:
                raise SchemaDefinitionError(
                    f"String check is used for `{name}` in schema `{cls.__name__}`, but the field is not a string."
                )

    @classmethod
    def _validate_multiindex(
        cls, df: pd.DataFrame, schema_map: dict[str, FieldInfo], Config: BaseConfig
    ) -> pd.DataFrame:
        """Validate index levels in `df` against the schema.

        Raise approproate errors if index levels are missing or if there is an
        overlap between index levels that different schema fields match.

        This method also acts as a filter, that (depending on the config) will
        pass `df` through with coerced types, filtered index levels, ordered
        index levels or as-is.
        """
        matching_index_names_in_df, schema_map = cls._select_matching_names(
            list(df.index.names), schema_map, match_index=True
        )

        if Config.filter:
            # Make sure that only the matching index levels are kept
            if df.index.names != [None] and len(matching_index_names_in_df) < len(df.index.names):
                if len(matching_index_names_in_df) == 0:
                    df = df.reset_index(drop=True, inplace=True)
                else:
                    df = df.droplevel([ind for ind in df.index.names if ind not in matching_index_names_in_df])

        if Config.multiindex_strict:
            if unexpected_indices := set(df.index.names) - set(matching_index_names_in_df) - set([None]):
                raise SchemaValidationError(
                    f"MultiIndex names {unexpected_indices} are present in `df` but not defined in schema. Use `multiindex_strict=False` to supress this error."
                )

        if Config.multiindex_ordered:
            if df.index.names != [None] and matching_index_names_in_df != list(df.index.names):
                raise SchemaValidationError(
                    "MultiIndex names in `df` are not ordered as in schema. Use `multiindex_ordered=False` to supress this error."
                )

        if Config.multiindex_sorted:
            if not (df.index.is_monotonic_increasing or df.index.is_monotonic_decreasing):
                raise SchemaValidationError(
                    "MultiIndex is not sorted. Use `multiindex_sorted=False` to supress this error."
                )

        if Config.multiindex_unique:
            if not df.index.is_unique:
                raise SchemaValidationError(
                    "MultiIndex is not unique. Use `multiindex_unique=False` to supress this error."
                )

        return df

    @classmethod
    def _validate_columns(cls, df: pd.DataFrame, schema_map: dict[str, FieldInfo], Config: BaseConfig) -> pd.DataFrame:
        """Validate column names in `df` against the schema.

        Raise approproate errors if columns are missing or if there is an
        overlap between columns that different schema fields match.

        This method also acts as a filter, that (depending on the config) will
        pass `df` through with coerced types, filtered columns, ordered columns
        or as-is.
        """
        matching_columns_in_df, _ = cls._select_matching_names(list(df.columns), schema_map)

        # Drop columns in `df` that do not match the schema
        if Config.filter:
            ordered_columns_in_df = [col for col in df.columns if col in matching_columns_in_df]
            df = df[ordered_columns_in_df].copy()

        # Complain about columns in `df` that are not defined in the schema
        elif Config.strict:
            if unexpected_columns := set(df.columns) - set(matching_columns_in_df):
                raise SchemaValidationError(
                    f"Columns {unexpected_columns} are present in `df` but not in schema. Use `strict=False` or `filter=True` to supress this error."
                )

        # Complain if the order of columns in `df` does not match the order in
        # which they are defined in the schema
        if Config.ordered:
            if matching_columns_in_df != list(df.columns):
                raise SchemaValidationError(
                    "Columns in `df` are not ordered as in schema. Use `ordered=False` to supress this error."
                )

        return df

    @classmethod
    def _select_matching_names(
        cls, names: list[str], schema_map: dict[str, FieldInfo], match_index: bool = False
    ) -> tuple[list[str], dict[str, FieldInfo]]:
        """Select columns or index levels in `names` that match the schema.

        If a column or index level is defined in the schema it *must* be
        present in `df`. This function serves the important purpose of raising
        errors when columns in `df` seem to be *missing* when compared to the
        schema.

        Raises:
            SchemaDefinitionError: If a column or alias is not found in `df`,
                is already matched by another field.
            MissingColumnsError: If a column is defined in the schema but not
                found in `df`.
            MissingIndexError: If an index level is defined in the schema
                but not found in `df`.
        """
        MissingNameError = MissingIndexError if match_index else MissingColumnsError
        series_type = "index level" if match_index else "column"
        matching_names = []
        for series_name, (_, optional, is_index, field) in schema_map.items():
            if is_index and not match_index:
                continue
            elif not is_index and match_index:
                continue
            if field.alias is not None and field.regex:
                matched = [name for name in names if re.match(field.alias, name)]
                if len(matched) == 0 and not optional:
                    raise MissingNameError(
                        f"No {series_type}s match regex `{field.alias}` for field `{series_name}` in schema `{cls.__name__}`"
                    )
                elif len(already_matched := set(matched) & set(matching_names)) > 0:
                    raise SchemaDefinitionError(
                        f"Regex `{field.alias}` for field `{series_name}` in schema `{cls.__name__}` matched {series_type}s {already_matched} already matched by another field."
                    )
                matching_names.extend(matched)
            elif field.alias is not None and field.regex is False:
                if field.alias not in names and not optional:
                    raise MissingNameError(
                        f"No {series_type}s match alias `{field.alias}` for field `{series_name}` in schema `{cls.__name__}`."
                    )
                elif field.alias in matching_names:
                    raise SchemaDefinitionError(
                        f"Alias `{field.alias}` for field `{series_name}` in schema `{cls.__name__}` is used by another field."
                    )
                matching_names.append(field.alias)
            else:
                if series_name not in names and not optional and field.check_index_name:  # field
                    raise MissingNameError(
                        f"No {series_type}s match {series_type} name `{series_name}` in schema `{cls.__name__}`."
                    )
                elif series_name in matching_names:
                    raise SchemaDefinitionError(
                        f"{series_type.capitalize()} `{series_name}` in schema `{cls.__name__}` is used by another field."
                    )
                elif field.check_index_name is False and match_index:
                    assert len(names) == 1, "This should not happen. Looks like columns were not properly filtered."
                    schema_map[names[0]] = schema_map.pop(series_name)
                    return names, schema_map
                else:
                    matching_names.append(series_name)
        return matching_names, schema_map

    @classmethod
    def validate(cls, df: pd.DataFrame) -> pd.DataFrame:
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
            SchemaValidationError: If there is a problem with the data in `df`.
                This could e.g. happen when a column is of the wrong dtype or
                when a custom check fails.
        """
        df = df.copy()

        schema_map = cls._get_schema_map()
        Config = cls._get_config()

        # Validate schema definition. Catch errors like, e.g., missing aliases
        # when regex=True, number checks on non-numeric columns, etc.
        cls._validate_schema(schema_map)

        # Check that indices and columns in `df` match schema. The only errors
        # that should be thrown here relate to schema errors or missing columns
        # in `df`. Furthermore, this method may filter, coerce or order `df`
        # depending on user-provided specifications in `Config`.
        df = cls._validate_multiindex(df, schema_map, Config)
        df = cls._validate_columns(df, schema_map, Config)

        # Validate `df` against schema. The only errors that should be raised
        # in this step are from dtype checks and `Field` checks.
        for name, (typ, optional, is_index, field) in schema_map.items():
            # Select the column (or columns) in `df` that match the field.
            # ... when index column
            if is_index:
                if field.regex and field.alias is not None:
                    matched_series = cls._select_index_series_by_regex(df, field.alias)
                else:
                    matched_series = cls._select_index_series(df, field.alias or name, optional)

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
                series = cls._validate_series(series, field, typ, Config.coerce or field.coerce)
                if Config.coerce or field.coerce:
                    if is_index:
                        df.index = cls.override_level(df.index, series.name, series)
                    else:
                        df[series.name] = series

        cls._validate_custom_checks(df)

        return df


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
        """Validate a series against the schema.

        Args:
            series (pandas.Series): The series to validate.

        Returns:
            pandas.Series: The validated series.
        """
        _, value_type = cls._get_value_name_and_type()
        field = cls._get_field()
        Config = cls._get_config()
        series = cls._validate_series(series, field, value_type, Config.coerce)
        return series
