import pandas as pd
import pytest

from pandabear.model import DataFrameModel, SeriesModel
from pandabear.model_components import Field


def test_strict_filter_ordered_columns():
    class MySchema(DataFrameModel):
        a: int = Field()
        b: float = Field()
        c: str = Field()

    # 1. passes, with a,b,c and not d present.
    class FilterConfig:
        filter: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(a=[1], b=[1.0], c=["a"], d=[1]))
    dfval = MySchema._validate_columns(df)
    assert dfval.shape == (1, 3)
    assert dfval.columns.tolist() == ["a", "b", "c"]

    # 2. column order is maintained
    df = pd.DataFrame(dict(b=[1.0], a=[1], d=[1], c=["a"]))
    dfval = MySchema._validate_columns(df)
    assert dfval.shape == (1, 3)
    assert dfval.columns.tolist() == ["b", "a", "c"]

    # 3. changing to strict == true doesn't do anything, filter takes precedence
    class FilterConfig:
        filter: bool = True
        strict: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(b=[1.0], a=[1], d=[1], c=["a"]))
    dfval = MySchema._validate_columns(df)
    assert dfval.columns.tolist() == ["b", "a", "c"]

    # 4. Changing filter to false, strict will now take effect, and fail:
    class FilterConfig:
        filter: bool = False
        strict: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(b=[1.0], a=[1], d=[1], c=["a"]))
    with pytest.raises(KeyError):
        dfval = MySchema._validate_columns(df)

    # 5. changing to ordered == true, will now fail
    class FilterConfig:
        filter: bool = False
        strict: bool = True
        ordered: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(b=[1.0], a=[1], c=["a"]))
    with pytest.raises(ValueError):
        dfval = MySchema._validate_columns(df)

    # 6. changing to filter == true, will still fail
    class FilterConfig:
        filter: bool = True
        strict: bool = True
        ordered: bool = True

    MySchema.Config = FilterConfig
    df = pd.DataFrame(dict(b=[1.0], a=[1], c=["a"]))
    with pytest.raises(ValueError):
        dfval = MySchema._validate_columns(df)

    # 8. missing column will fail on filter
    df = pd.DataFrame(dict(b=[1.0], a=[1]))
    with pytest.raises(KeyError):
        dfval = MySchema._validate_columns(df)
