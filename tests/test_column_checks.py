import numpy as np
import pandas as pd
import pytest

from pandabear.column_checks import (
    series_greater,
    series_greater_equal,
    series_isin,
    series_less,
    series_less_equal,
    series_notin,
    series_nullable,
    series_str_contains,
    series_str_endswith,
    series_str_startswith,
)
from pandabear.exceptions import ColumnCheckError


def test_series_greater_equal():
    assert not series_greater_equal(pd.Series([1, 2, 3]), 2).all()
    assert series_greater_equal(pd.Series([1, 2, 3]), 1).all()
    assert series_greater_equal(pd.Series([1, 2, 3]), 0).all()
    # and for some strings
    assert not series_greater_equal(pd.Series(["a", "b", "c"]), "b").all()
    assert series_greater_equal(pd.Series(["a", "b", "c"]), "a").all()


def test_series_greater():
    assert not series_greater(pd.Series([1, 2, 3]), 2).all()
    assert not series_greater(pd.Series([1, 2, 3]), 1).all()
    assert series_greater(pd.Series([1, 2, 3]), 0).all()
    # and for some strings
    assert not series_greater(pd.Series(["a", "b", "c"]), "b").all()
    assert not series_greater(pd.Series(["a", "b", "c"]), "a").all()
    assert series_greater(pd.Series(["a", "b", "c"]), "0").all()


def test_series_less_equal():
    assert not series_less_equal(pd.Series([1, 2, 3]), 2).all()
    assert series_less_equal(pd.Series([1, 2, 3]), 3).all()
    assert series_less_equal(pd.Series([1, 2, 3]), 4).all()
    # and for some strings
    assert series_less_equal(pd.Series(["a", "b", "c"]), "c").all()
    assert not series_less_equal(pd.Series(["a", "b", "c"]), "a").all()


def test_series_less():
    assert series_less(pd.Series([1, 2, 3]), 4).all()
    assert not series_less(pd.Series([1, 2, 3]), 1).all()
    assert not series_less(pd.Series([1, 2, 3]), 0).all()
    # and for some strings
    assert series_less(pd.Series(["a", "b", "c"]), "d").all()
    assert not series_less(pd.Series(["a", "b", "c"]), "a").all()
    assert not series_less(pd.Series(["a", "b", "c"]), "0").all()


def test_series_isin():
    assert not series_isin(pd.Series([1, 2, 3]), [2]).all()
    assert series_isin(pd.Series([1, 2, 2]), [1, 2]).all()
    # and for some strings
    assert not series_isin(pd.Series(["a", "b", "c"]), ["b"]).all()
    assert series_isin(pd.Series(["a", "b", "b"]), ["a", "b"]).all()


def test_series_notin():
    assert series_notin(pd.Series([1, 2, 3]), [4]).all()
    assert not series_notin(pd.Series([1, 2, 2]), [2]).all()
    # and for some strings
    assert series_notin(pd.Series(["a", "b", "c"]), ["d", "e"]).all()
    assert not series_notin(pd.Series(["a", "b", "b"]), ["a", "b"]).all()


def test_series_str_contains():
    assert not series_str_contains(pd.Series(["a", "b", "c"]), "b").all()
    assert series_str_contains(pd.Series(["ab", "bb", "cb"]), "b").all()
    assert not series_str_contains(pd.Series(["a", "b", "c"]), "0").all()


def test_series_str_endswith():
    assert not series_str_endswith(pd.Series(["a", "b", "c"]), "b").all()
    assert series_str_endswith(pd.Series(["ac", "bc", "cc"]), "c").all()
    assert not series_str_endswith(pd.Series(["a", "b", "c"]), "0").all()


def test_series_str_startswith():
    assert not series_str_startswith(pd.Series(["a", "b", "c"]), "b").all()
    assert series_str_startswith(pd.Series(["ca", "cb", "cc"]), "c").all()


def test_series_nullable():
    assert series_nullable(pd.Series([1, 2, 3]), True).all()
    assert series_nullable(pd.Series([1, 2, 3]), False).all()
    assert not series_nullable(pd.Series([1, 2, 3, None]), False).all()
    assert not series_nullable(pd.Series([1.0, 2.0, np.nan]), False).all()
    assert not series_nullable(pd.Series([pd.NaT, pd.Timestamp("1939-05-27")]), False).all()


def test_ColumnCheckError():
    check_func = series_greater
    series = pd.Series([1, 2, 3], name="test")

    # 1. test failure and message with info on failing rows
    expected_message = r"Column 'test' failed check greater\(2\): 2 of 3 \(67 %\)"
    with pytest.raises(ColumnCheckError, match=expected_message):
        result = check_func(series, 2)
        raise ColumnCheckError(check_name=check_func.__name__, check_value=2, series=series, result=result)


if __name__ == "__main__":
    test_series_greater_equal()
    test_series_greater()
    test_series_less_equal()
    test_series_less()
    test_series_isin()
    test_series_notin()
    test_series_str_contains()
    test_series_str_endswith()
    test_series_str_startswith()
    test_series_notnull()
    test_check_handler()
