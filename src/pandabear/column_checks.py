def series_greater_equal(series, value):
    return (series >= value).all()


def series_greater(series, value):
    return (series > value).all()


def series_less_equal(series, value):
    return (series <= value).all()


def series_less(series, value):
    return (series < value).all()


def series_isin(series, value):
    return series.isin(value).all()


def series_notin(series, value):
    return (~series.isin(value)).all()


def series_str_contains(series, value):
    return series.str.contains(value).all()


def series_str_endswith(series, value):
    return series.str.endswith(value).all()


def series_str_startswith(series, value):
    return series.str.startswith(value).all()


def series_notnull(series):
    return series.notnull().all()


def series_all_unique(series):
    return len(set(series)) == len(series)


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
