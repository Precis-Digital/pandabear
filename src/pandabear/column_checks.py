import pandas as pd

MAX_FAILURE_ROWS = 10


def series_greater_equal(series, value):
    return series >= value


def series_greater(series, value):
    return series > value


def series_less_equal(series, value):
    return series <= value


def series_less(series, value):
    return series < value


def series_isin(series, value):
    return series.isin(value)


def series_notin(series, value):
    return ~series.isin(value)


def series_str_contains(series, value):
    return series.str.contains(value)


def series_str_endswith(series, value):
    return series.str.endswith(value)


def series_str_startswith(series, value):
    return series.str.startswith(value)


def series_notnull(series, value=None):
    return series.notnull()


def series_all_unique(series, value=None):
    return len(set(series)) == len(series)


def check_handler(check_func: callable, series: pd.Series, value):
    """Handle a defined check, and report failures.

    check_func: callable with signature (series, value) -> bool or pd.Series.
        note that the value argument is optional for some checks, but must be passed.
    series: pd.Series to which to apply the chack function
    value: additional value specifying the check
    """
    result = check_func(series, value)
    if type(result) is bool:
        if result:
            return True
        check_name = check_func.__name__.replace("series_", "")
        raise ValueError(f"Column '{series.name}' failed check {check_name}({value}).")

    elif not isinstance(result, pd.Series):
        raise ValueError(f"Unexpected check result type: {type(result)}")

    if result.all():
        return True

    print(result)

    fail_series = series[~result]
    total = len(series)
    fails = len(fail_series)
    fail_pc = int(round(100 * fails / total))
    check_name = check_func.__name__.replace("series_", "")
    text_msg = f"Column '{series.name}' failed check {check_name}({value}): " f"{fails} of {total} ({fail_pc} %)"
    fails_msg = fail_series.head(MAX_FAILURE_ROWS).to_string()
    raise ValueError(f"{text_msg}\n{fails_msg}")


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
