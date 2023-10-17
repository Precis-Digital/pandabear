from typing import Any, Iterable

import pandas as pd

MAX_FAILURE_ROWS = 10


class ColumnCheckError(Exception):
    def __init__(self, check_name: str, check_value: Any, series: pd.Series, result: pd.Series):
        self.check_name = check_name
        self.check_value = check_value
        self.series = series
        self.result = result
        super().__init__(self._get_message())

    def _get_message(self) -> str:
        fail_series = self.series[~self.result]
        total = len(self.series)
        fails = len(fail_series)
        fail_pc = int(round(100 * fails / total))
        check_name = self.check_name.replace("series_", "")
        text_msg = (
            f"Column '{self.series.name}' failed check {check_name}({self.check_value}): "
            f"{fails} of {total} ({fail_pc} %)"
        )
        fails_msg = fail_series.head(MAX_FAILURE_ROWS).to_string()
        return f"{text_msg}\n{fails_msg}"


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


def series_notnull(series: pd.Series, value: bool = True) -> pd.Series:
    return series.notnull()


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
    "notnull": series_notnull,
}
