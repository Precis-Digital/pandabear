import datetime

import numpy as np
import pandas as pd

from pandabear import type_checking


def test_datetime():
    series = pd.date_range("2020-01-01", "2020-01-03")
    assert type_checking.is_of_type(series, datetime.datetime)
    assert type_checking.is_of_type(series, np.datetime64)


def test_check_datetime_index():
    index = pd.DatetimeIndex(["2020-01-01", "2020-01-03"])
    assert type_checking.is_of_type(index, pd.DatetimeIndex)


def test_bare_categorical_dtype():
    series = pd.Series(["a", "b", "c"], dtype="category")
    assert type_checking.is_of_type(series, pd.CategoricalDtype)


def test_categorical_dtype():
    cat_type_ordered = pd.CategoricalDtype(["a", "b"], ordered=True)
    cat_series = pd.CategoricalIndex(list("aaabbbabba"), categories=["a", "b"], ordered=True).to_series()
    assert type_checking.is_of_type(cat_series, cat_type_ordered)

    cat_type_unordered = pd.CategoricalDtype(["a", "b"], ordered=False)
    assert not type_checking.is_of_type(cat_series, cat_type_unordered)


if __name__ == "__main__":
    test_datetime()
    test_check_datetime_index()
    test_bare_categorical_dtype()
    test_categorical_dtype()
