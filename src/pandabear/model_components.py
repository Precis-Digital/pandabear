import dataclasses
from typing import Any

CHECK_NAME_FUNCTION_MAP = {
    "ge": lambda se, v: (se >= v).all(),
    "gt": lambda se, v: (se > v).all(),
    "lt": lambda se, v: (se < v).all(),
    "le": lambda se, v: (se <= v).all(),
    "isin": lambda se, v: se.isin(v).all(),
    "notin": lambda se, v: (~se.isin(v)).all(),
    "str_contains": lambda se, v: se.str.contains(v).all(),
    "str_endswith": lambda se, v: se.str.endswith(v).all(),
    "str_startswith": lambda se, v: se.str.startswith(v).all(),
    "notnull": lambda se, v: se.notnull().all(),
    "null": lambda se, v: se.isnull().all(),
}

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