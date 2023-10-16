import pandas as pd
import pytest

from pandabear.model import DataFrameModel, SeriesModel
from pandabear.model_components import Field


def test_strict_filter_ordered_columns():
    class FilterConfig:
        filter: bool = True

    class MySchema(DataFrameModel):
        a: int = Field()
        b: float = Field()
        c: str = Field()
        Config = FilterConfig

    # 1. passes, with a,b,c and not d present.

    df = pd.DataFrame(dict(a=[1], b=[1.0], c=["a"], d=[1]))
    dfval = MySchema._validate_columns(df)
    assert dfval.shape == (1, 3)
    assert dfval.columns.tolist() == ["a", "b", "c"]

    # 2. reorders columns to order passed
    df = pd.DataFrame(dict(b=[1.0], a=[1], d=[1], c=["a"]))
    dfval = MySchema._validate_columns(df)
    assert dfval.shape == (1, 3)
    assert dfval.columns.tolist() == ["a", "b", "c"]

    # 3. changing to strict == true doesn't do anything, filter takes precedence
    class FilterConfig:
        filter: bool = True
        strict: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(b=[1.0], a=[1], d=[1], c=["a"]))
    dfval = MySchema._validate_columns(df)
    assert dfval.columns.tolist() == ["a", "b", "c"]

    # 4. Changing filter to false, strict will now take effect, and fail:
    class FilterConfig:
        filter: bool = False
        strict: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(b=[1.0], a=[1], d=[1], c=["a"]))
    with pytest.raises(ValueError):
        dfval = MySchema._validate_columns(df)

    # 5. this passes and column order is preserved
    df = pd.DataFrame(dict(b=[1.0], a=[1], c=["a"]))
    dfval = MySchema._validate_columns(df)
    assert dfval.columns.tolist() == ["b", "a", "c"]

    # 6. changing to ordered == true, will now fail
    class FilterConfig:
        filter: bool = False
        strict: bool = True
        ordered: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(b=[1.0], a=[1], c=["a"]))
    with pytest.raises(ValueError):
        dfval = MySchema._validate_columns(df)

    # 7. changing to filter == true, will now pass
    class FilterConfig:
        filter: bool = True
        strict: bool = True
        ordered: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(b=[1.0], a=[1], c=["a"]))
    dfval = MySchema._validate_columns(df)
    assert dfval.columns.tolist() == ["a", "b", "c"]

    # 8. missing column will fail on filter
    df = pd.DataFrame(dict(b=[1.0], a=[1]))
    with pytest.raises(KeyError):
        dfval = MySchema._validate_columns(df)
