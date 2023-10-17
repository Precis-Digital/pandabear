import dataclasses
from typing import Any


@dataclasses.dataclass
class Field:
    typ: Any = None

    # Pandas Series checks
    ge: int | float = None
    gt: int | float = None
    lt: int | float = None
    le: int | float = None
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

        new_class = type("SchemaConfig", (other_cls, cls), {})
        new_class.__annotations__ = cls.__annotations__.copy()
        return new_class
