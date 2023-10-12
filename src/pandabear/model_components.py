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
