import re
from types import NoneType, UnionType
from typing import Any, Type, Union

import numpy as np
import pandas as pd

from pandabear.column_checks import CHECK_NAME_FUNCTION_MAP
from pandabear.exceptions import (
    CoersionError,
    ColumnCheckError,
    IndexCheckError,
    MissingColumnsError,
    MissingIndexError,
    SchemaDefinitionError,
    SchemaValidationError,
    UnsupportedTypeError,
)
from pandabear.model_components import (
    BaseConfig,
    Field,
    FieldInfo,
    get_index_type,
    is_type_index,
)
from pandabear.type_checking import is_of_type


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
    def _validate_series_or_index(
        cls, se_or_idx: pd.Series | Type[pd.Index], field: Field, typ: Any, coerce: bool
    ) -> pd.Series:
        """Validate a series against a field and type.

        Args:
            se_or_idx: The series or Index (or Index substype) to validate.
            field: The field to validate against.
            typ: The type to validate against.
            coerce: Whether to coerce the series to the type of the
                field.

        Returns:
            se_or_idx: pd.Series | Type[pd.Index]: The validated series or Index.
        """

        is_index = ~isinstance(se_or_idx, pd.Series)

        if not is_of_type(se_or_idx, typ):
            if coerce:
                try:
                    se_or_idx = se_or_idx.astype(typ)
                except ValueError:
                    raise CoersionError(f"Could not coerce `{se_or_idx.name}` with dtype {se_or_idx.dtype} to {typ}")
            else:
                raise SchemaValidationError(
                    f"Expected {f'`{se_or_idx.name}`' if se_or_idx.name else 'index'} with dtype {typ} but found dtype `{se_or_idx.dtype}`"
                )

        for check_name, check_func in CHECK_NAME_FUNCTION_MAP.items():
            check_value = getattr(field, check_name)
            if check_value is not None:
                result = check_func(series=se_or_idx if is_index else se_or_idx.to_series(), value=check_value)
                if not result.all():
                    if is_index:
                        raise ColumnCheckError(
                            check_name=check_name, check_value=check_value, series=se_or_idx, result=result
                        )
                    else:
                        raise IndexCheckError(
                            check_name=check_name, check_value=check_value, index=se_or_idx, result=result
                        )
        return se_or_idx


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
            cls._check_type_is_valid(typ)
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
    def _override_level(
        df_index: Type[pd.Index], index_level: str, new_index_values: Type[pd.Index]
    ) -> pd.MultiIndex | pd.Index:
        """Override a level in a MultiIndex or Index with a new index."""
        if isinstance(df_index, pd.MultiIndex):
            df_tmp = df_index.to_frame(index=False)
            if index_level not in df_tmp.columns:
                raise ValueError(f"Index level '{index_level}' not found in MultiIndex.")
            df_tmp[index_level] = new_index_values
            return pd.MultiIndex.from_frame(df_tmp)
        else:
            if df_index.name != index_level:
                raise ValueError(f"Index name '{df_index.name}' does not match given index_level '{index_level}'.")
            index_type_map = {
                pd.Index: pd.Index,
                pd.DatetimeIndex: pd.DatetimeIndex,
                pd.PeriodIndex: pd.PeriodIndex,
                pd.TimedeltaIndex: pd.TimedeltaIndex,
                pd.CategoricalIndex: pd.CategoricalIndex,
                pd.RangeIndex: pd.RangeIndex,
                pd.IntervalIndex: pd.IntervalIndex,
            }
            index_type = index_type_map.get(type(df_index))
            return index_type(new_index_values, name=index_level)

    @staticmethod
    def _select_index_series(df: pd.DataFrame, level: str, optional: bool = True) -> list[Type[pd.Index]]:
        """Select a series from a dataframe by column name.

        Return a list containing maximally 1 series. Reason for this is that
        series are validated in a loop, so returning a list is convenient.
        """
        try:
            return [df.index.get_level_values(level)]
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
    def _select_index_series_by_regex(df: pd.DataFrame, alias: str) -> list[Type[pd.Index]]:
        """Select a series from a dataframe by regex."""
        return [df.index.get_level_values(level) for level in df.index.names if re.match(alias, level) is not None]

    @staticmethod
    def _select_series_by_regex(df: pd.DataFrame, alias: str) -> list[pd.Series]:
        """Select a series from a dataframe by regex."""
        return [df[col] for col in df.filter(regex=alias, axis=1).columns]

    @classmethod
    def _check_type_is_valid(cls, typ: Any) -> bool:
        """Recursively check that `typ` is a valid type annotation."""
        if typ in [int, float, str, bytes, bool, type(None)]:
            return True
        if isinstance(typ, type):
            return True
        if hasattr(typ, "__origin__") and hasattr(typ, "__args__"):
            origin = typ.__origin__
            args = typ.__args__
            if origin in {list, dict, Union}:
                return all(cls._check_type_is_valid(arg) for arg in args)
        if isinstance(typ, UnionType):
            return all(cls._check_type_is_valid(arg) for arg in typ.__args__)
        raise UnsupportedTypeError(f"Type `{typ}` is not supported")

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
    def _validate_multiindex(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Validate index levels in `df` against the schema.

        Raise approproate errors if index levels are missing or if there is an
        overlap between index levels that different schema fields match.

        This method also acts as a filter, that (depending on the config) will
        pass `df` through with coerced types, filtered index levels, ordered
        index levels or as-is.
        """
        matching_index_names_in_df = cls._select_matching_names(list(df.index.names), match_index=True)

        if cls.Config.filter:
            # Make sure that only the matching index levels are kept
            if df.index.names != [None] and len(matching_index_names_in_df) < len(df.index.names):
                if len(matching_index_names_in_df) == 0:
                    df = df.reset_index(drop=True, inplace=True)
                else:
                    df = df.droplevel([ind for ind in df.index.names if ind not in matching_index_names_in_df])

        if cls.Config.multiindex_strict:
            if unexpected_indices := set(df.index.names) - set(matching_index_names_in_df) - set([None]):
                raise SchemaValidationError(
                    f"MultiIndex names {unexpected_indices} are present in `df` but not defined in schema. Use `multiindex_strict=False` to supress this error."
                )

        if cls.Config.multiindex_ordered:
            if df.index.names != [None] and matching_index_names_in_df != list(df.index.names):
                raise SchemaValidationError(
                    "MultiIndex names in `df` are not ordered as in schema. Use `multiindex_ordered=False` to supress this error."
                )

        if cls.Config.multiindex_sorted:
            if not (df.index.is_monotonic_increasing or df.index.is_monotonic_decreasing):
                raise SchemaValidationError(
                    "MultiIndex is not sorted. Use `multiindex_sorted=False` to supress this error."
                )

        if cls.Config.multiindex_unique:
            if not df.index.is_unique:
                raise SchemaValidationError(
                    "MultiIndex is not unique. Use `multiindex_unique=False` to supress this error."
                )

        return df

    @classmethod
    def _validate_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Validate column names in `df` against the schema.

        Raise approproate errors if columns are missing or if there is an
        overlap between columns that different schema fields match.

        This method also acts as a filter, that (depending on the config) will
        pass `df` through with coerced types, filtered columns, ordered columns
        or as-is.
        """
        matching_columns_in_df = cls._select_matching_names(list(df.columns))

        # Drop columns in `df` that do not match the schema
        if cls.Config.filter:
            ordered_columns_in_df = [col for col in df.columns if col in matching_columns_in_df]
            df = df[ordered_columns_in_df].copy()

        # Complain about columns in `df` that are not defined in the schema
        elif cls.Config.strict:
            if unexpected_columns := set(df.columns) - set(matching_columns_in_df):
                raise SchemaValidationError(
                    f"Columns {unexpected_columns} are present in `df` but not in schema. Use `strict=False` or `filter=True` to supress this error."
                )

        # Complain if the order of columns in `df` does not match the order in
        # which they are defined in the schema
        if cls.Config.ordered:
            if matching_columns_in_df != list(df.columns):
                raise SchemaValidationError(
                    "Columns in `df` are not ordered as in schema. Use `ordered=False` to supress this error."
                )

        return df

    @classmethod
    def _select_matching_names(
        cls, names: list[str], match_index: bool = False
    ) -> tuple[list[str], dict[str, FieldInfo]]:
        """Select columns or index levels in `names` that match the schema.

        If a column or index level is defined in the schema it *must* be
        present in `df`. This function serves the important purpose of raising
        errors when columns in `df` seem to be *missing* when compared to the
        schema.

        NOTE: This method may modify the schema map. This happens when an Index
        field is defined with `check_index_name = False`. In that case this
        method will replace the index name in the schema map with the name of
        the index in `df`.

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
        for series_name, (_, optional, is_index, field) in cls.schema_map.items():
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
                    cls.schema_map[names[0]] = cls.schema_map.pop(series_name)
                    return names
                else:
                    matching_names.append(series_name)
        return matching_names

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

        cls.schema_map = cls._get_schema_map()
        cls.Config = cls._get_config()

        # Validate schema definition. Catch errors like, e.g., missing aliases
        # when regex=True, number checks on non-numeric columns, etc.
        cls._validate_schema(cls.schema_map)

        # Check that indices and columns in `df` match schema. The only errors
        # that should be thrown here relate to schema errors or missing columns
        # in `df`. Furthermore, this method may filter, coerce or order `df`
        # depending on user-provided specifications in `Config`.
        df = cls._validate_multiindex(df)
        df = cls._validate_columns(df)

        # Validate `df` against schema. The only errors that should be raised
        # in this step are from dtype checks and `Field` checks.
        for name, (typ, optional, is_index, field) in cls.schema_map.items():
            # Select the column (or columns) in `df` that match the field.
            # ... when index column
            if is_index:
                if field.regex and field.alias is not None:
                    matched_series_or_index = cls._select_index_series_by_regex(df, field.alias)
                else:
                    matched_series_or_index = cls._select_index_series(df, field.alias or name, optional)

            # ... when column has aliased name
            elif field.alias is not None:
                if field.regex:
                    matched_series_or_index = cls._select_series_by_regex(df, field.alias)
                else:
                    matched_series_or_index = cls._select_series(df, field.alias, optional)

            # ... when column name is attribute name (not alias)
            else:
                matched_series_or_index = cls._select_series(df, name, optional)

            # Validate the selected column(s) against the field and type.
            for series_or_index in matched_series_or_index:
                series_or_index = cls._validate_series_or_index(
                    series_or_index, field, typ, cls.Config.coerce or field.coerce
                )
                if cls.Config.coerce or field.coerce:
                    if is_index:
                        df.index = cls._override_level(df.index, series_or_index.name, series_or_index.values)
                    else:
                        df[series_or_index.name] = series_or_index

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
        series = cls._validate_series_or_index(series, field, value_type, Config.coerce)
        return series
