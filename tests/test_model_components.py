import pandas as pd

from pandabear import model_components


def test_is_type_index_wrapped():
    assert model_components.is_type_index_wrapped(model_components.Index[int])
    assert not model_components.is_type_index_wrapped(int)


def test_is_type_index():
    assert model_components.is_type_index(model_components.Index[int])
    assert not model_components.is_type_index(int)
    model_components.PANDAS_INDEX_TYPES.append(pd.DatetimeIndex)
    assert model_components.is_type_index(pd.DatetimeIndex)
    assert not model_components.is_type_index(str)
    assert not model_components.is_type_index(model_components.Index)


def test_get_index_type():
    assert model_components.get_index_type(model_components.Index[int]) is int
    assert model_components.get_index_type(pd.DatetimeIndex) is pd.DatetimeIndex
