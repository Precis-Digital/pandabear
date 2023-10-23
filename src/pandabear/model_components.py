import dataclasses
from typing import Any, NamedTuple, Type


@dataclasses.dataclass
class Field:
    ''' TODO add docstring to descripe what ge, gt, lt, and le stand for..
    '''

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
    notnull: bool | None = None
    null: bool | None = None
    unique: bool | None= None

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
