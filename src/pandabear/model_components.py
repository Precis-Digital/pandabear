import dataclasses
from typing import Any


@dataclasses.dataclass
class Field:
    typ: Any = None

    # Pandas Series checks
    ge: float = None
    gt: float = None
    lt: float = None
    le: float = None
    isin: list = None
    notin: list = None
    str_contains: str = None
    str_endswith: str = None
    str_startswith: str = None
    notnull: bool = None
    null: bool = None

    # Column name checks
    alias: str = None
    regex: bool = False


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
