import pandas as pd
import numpy as np

from pandabear.column_checks import (
    series_greater_equal,
    series_greater,
    series_less_equal,
    series_less,
    series_isin,
    series_notin,
    series_str_contains,
    series_str_startswith,
    series_str_endswith,
    series_notnull,
)


def test_series_greater_equal():
    assert not series_greater_equal(pd.Series([1, 2, 3]), 2)
    assert series_greater_equal(pd.Series([1, 2, 3]), 1)
    assert series_greater_equal(pd.Series([1, 2, 3]), 0)
    # and for some strings
    assert not series_greater_equal(pd.Series(["a", "b", "c"]), "b")
    assert series_greater_equal(pd.Series(["a", "b", "c"]), "a")


def test_series_greater():
    assert not series_greater(pd.Series([1, 2, 3]), 2)
    assert not series_greater(pd.Series([1, 2, 3]), 1)
    assert series_greater(pd.Series([1, 2, 3]), 0)
    # and for some strings
    assert not series_greater(pd.Series(["a", "b", "c"]), "b")
    assert not series_greater(pd.Series(["a", "b", "c"]), "a")
    assert series_greater(pd.Series(["a", "b", "c"]), "0")


def test_series_less_equal():
    assert not series_less_equal(pd.Series([1, 2, 3]), 2)
    assert series_less_equal(pd.Series([1, 2, 3]), 3)
    assert series_less_equal(pd.Series([1, 2, 3]), 4)
    # and for some strings
    assert series_less_equal(pd.Series(["a", "b", "c"]), "c")
    assert not series_less_equal(pd.Series(["a", "b", "c"]), "a")


def test_series_less():
    assert series_less(pd.Series([1, 2, 3]), 4)
    assert not series_less(pd.Series([1, 2, 3]), 1)
    assert not series_less(pd.Series([1, 2, 3]), 0)
    # and for some strings
    assert series_less(pd.Series(["a", "b", "c"]), "d")
    assert not series_less(pd.Series(["a", "b", "c"]), "a")
    assert not series_less(pd.Series(["a", "b", "c"]), "0")


def test_series_isin():
    assert not series_isin(pd.Series([1, 2, 3]), [2])
    assert series_isin(pd.Series([1, 2, 2]), [1, 2])
    # and for some strings
    assert not series_isin(pd.Series(["a", "b", "c"]), ["b"])
    assert series_isin(pd.Series(["a", "b", "b"]), ["a", "b"])


def test_series_notin():
    assert series_notin(pd.Series([1, 2, 3]), [4])
    assert not series_notin(pd.Series([1, 2, 2]), [2])
    # and for some strings
    assert series_notin(pd.Series(["a", "b", "c"]), ["d", "e"])
    assert not series_notin(pd.Series(["a", "b", "b"]), ["a", "b"])


def test_series_str_contains():
    assert not series_str_contains(pd.Series(["a", "b", "c"]), "b")
    assert series_str_contains(pd.Series(["ab", "bb", "cb"]), "b")
    assert not series_str_contains(pd.Series(["a", "b", "c"]), "0")


def test_series_str_endswith():
    assert not series_str_endswith(pd.Series(["a", "b", "c"]), "b")
    assert series_str_endswith(pd.Series(["ac", "bc", "cc"]), "c")
    assert not series_str_endswith(pd.Series(["a", "b", "c"]), "0")


def test_series_str_startswith():
    assert not series_str_startswith(pd.Series(["a", "b", "c"]), "b")
    assert series_str_startswith(pd.Series(["ca", "cb", "cc"]), "c")


def test_series_notnull():
    assert series_notnull(pd.Series([1, 2, 3]))
    assert not series_notnull(pd.Series([1, 2, 3, None]))
    assert not series_notnull(pd.Series([1.0, 2.0, np.nan]))
    assert not series_notnull(pd.Series([pd.NaT, pd.Timestamp("1939-05-27")]))

