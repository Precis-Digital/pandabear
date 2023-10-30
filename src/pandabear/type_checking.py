import datetime

import numpy as np
import pandas as pd


def check_dtype_equality(series_or_index, typ):
    return series_or_index.dtype == typ


def check_isinstance(series_or_index, typ):
    return isinstance(series_or_index, typ)


def check_type_is(series_or_index, typ):
    return type(series_or_index) is typ


def check_str_object(series_or_index, typ):
    return check_dtype_equality(series_or_index, np.dtype("O"))


def check_datetime64(series_or_index, typ):
    return check_dtype_equality(series_or_index, np.dtype("datetime64[ns]"))


def check_str_expensive(series_or_index, typ):
    if not check_str_object(series_or_index, None):
        return False
    return all(isinstance(x, str) for x in series_or_index)


def check_bare_categorical_dtype(series_or_index, typ):
    return check_dtype_equality(series_or_index, "category")


TYPE_CHECK_MAP = {
    int: check_dtype_equality,
    float: check_dtype_equality,
    bool: check_dtype_equality,
    str: check_str_object,
    np.datetime64: check_datetime64,
    datetime.datetime: check_datetime64,
    pd.CategoricalIndex: check_isinstance,
    pd.CategoricalDtype: check_bare_categorical_dtype,
    pd.DatetimeIndex: check_type_is,
    pd.Index: check_type_is,
}


def is_of_type(series_or_index, typ):
    if typ in TYPE_CHECK_MAP:
        return TYPE_CHECK_MAP[typ](series_or_index, typ)
    if isinstance(typ, type(pd.CategoricalDtype())):
        return check_dtype_equality(series_or_index, typ)
    check_dtype_equality(series_or_index, typ)
