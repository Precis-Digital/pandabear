from typing import Any, Iterable

import pandas as pd


def series_greater_equal(series: pd.Series, value: Any) -> pd.Series:
    return series >= value


def series_greater(series: pd.Series, value: Any) -> pd.Series:
    return series > value


def series_less_equal(series: pd.Series, value: Any) -> pd.Series:
    return series <= value


def series_less(series: pd.Series, value: Any) -> pd.Series:
    return series < value


def series_isin(series: pd.Series, value: Iterable) -> pd.Series:
    return series.isin(value)


def series_notin(series: pd.Series, value: Iterable) -> pd.Series:
    return ~series.isin(value)


def series_str_contains(series: pd.Series, value: str) -> pd.Series:
    return series.str.contains(value)


def series_str_endswith(series: pd.Series, value: str) -> pd.Series:
    return series.str.endswith(value)


def series_str_startswith(series: pd.Series, value: str) -> pd.Series:
    return series.str.startswith(value)


def series_nullable(series: pd.Series, value: bool) -> pd.Series:
    if value:
        return pd.Series([True] * len(series), index=series.index)
    return series.notnull()


def series_unique(series: pd.Series, value: bool = True) -> pd.Series:
    return ~series.duplicated(keep="first")


CHECK_NAME_FUNCTION_MAP = {
    "ge": series_greater_equal,
    "gt": series_greater,
    "le": series_less_equal,
    "lt": series_less,
    "isin": series_isin,
    "notin": series_notin,
    "str_contains": series_str_contains,
    "str_startswith": series_str_startswith,
    "str_endswith": series_str_endswith,
    "nullable": series_nullable,
    "unique": series_unique,
}
