import dataclasses
from typing import Any, NamedTuple, Type, Union

import pandas as pd

from pandabear.exceptions import SchemaDefinitionError, UnsupportedTypeError

PANDAS_INDEX_TYPES = [
    # pd.DatetimeIndex
]


@dataclasses.dataclass
class Field:
    """Class for defining a schema for a column (or group thereof) in a dataframe.

    Args:
        typ: The type of the column. If None, the type is not checked.
        ge: Greater than or equal to.
        gt: Greater than.
        le: Less than or equal to.
        lt: Less than.
        isin: Checks if the column is in the given list.
        notin: Checks if the column is not in the given list.
        str_contains: Checks if the column contains the given string.
        str_startswith: Checks if the column starts with the given string.
        str_endswith: Checks if the column ends with the given string.
        nullable: If false checks if series contains null values.
        null: Checks if the column is null.
        unique: Checks if the column is unique.
        check_index_name: Whether or not to check the index name (or allow it to be anything)
        alias: Alias for the column name. Can be a regex.
        regex: Whether or not the alias is a regex.
        coerce: Whether or not to coerce the column to the given type.
    """

    typ: Any = None

    # Pandas Series checks
    ge: int | float | None = None
    gt: int | float | None = None
    lt: int | float | None = None
    le: int | float | None = None
    isin: list | None = None
    notin: list | None = None
    str_contains: str | None = None
    str_endswith: str | None = None
    str_startswith: str | None = None
    nullable: bool | None = None
    null: bool | None = None
    unique: bool | None = None
    check_index_name: bool = True

    # Column name checks
    alias: str | None = None
    regex: bool = False
    coerce: bool = False


@dataclasses.dataclass
class BaseConfig:
    strict: bool = True
    filter: bool = False
    ordered: bool = False
    coerce: bool = False
    multiindex_strict: bool = True
    multiindex_ordered: bool = False
    multiindex_sorted: bool = False
    multiindex_unique: bool = False

    @classmethod
    def _override(cls, other_cls):
        if other_cls is cls:
            return cls
        cls._assert_config_fields(other_cls)
        cls._assert_config_types(other_cls)
        new_class = type("SchemaConfig", (other_cls, cls), {})
        new_class.__annotations__ = cls.__annotations__.copy()
        return new_class

    @classmethod
    def _assert_config_fields(cls, other_cls):
        for name in dir(other_cls):
            if name.startswith("_"):
                continue
            if name in cls.__annotations__:
                continue
            raise ValueError(f"Config field `{name}` is not defined in BaseConfig")

    @classmethod
    def _assert_config_types(cls, other_cls):
        annotations = cls.__annotations__
        for name in dir(other_cls):
            if name.startswith("_"):
                continue
            if name in cls.__annotations__:
                value = getattr(other_cls, name)
                expeced_typ = annotations[name]
                if not isinstance(value, expeced_typ):
                    raise TypeError(f"Config field `{name}` expected type {expeced_typ} but found {type(value)}")


class Index:
    @classmethod
    def __class_getitem__(cls, typ):
        """Only for "marking" index columns as part of index."""
        return cls | typ


class FieldInfo(NamedTuple):
    type: Type
    optional: bool
    is_index: bool
    field: Field


def is_type_index_wrapped(typ):
    """Check whether type annotation is like `Index[<type>]`."""
    return hasattr(typ, "__args__") and typ.__args__[0] is Index


def is_type_index(typ, name, class_name):
    # Field is like `index: Index` (not allowed)
    if typ is Index:
        raise SchemaDefinitionError(
            f"Index column `{name}` in schema `{class_name}` must be defined as `Index[<type>]`"
        )
    # Field is like `index: Index[int]`
    if is_type_index_wrapped(typ):
        return True
    # Field is like `index: pd.DatetimeIndex` or other subclass of `pd.Index`
    if issubclass(typ, pd.Index):
        return True

    # The user has provided something that is not meant as an index
    return False


def get_index_type(typ):
    if is_type_index_wrapped(typ):
        return typ.__args__[1]
    return typ
