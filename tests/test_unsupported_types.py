import numpy as np
import pandas as pd
import pytest

from pandabear import DataFrameModel, Field, Index
from pandabear.exceptions import UnsupportedTypeError


def test_datetime():
    class MySchema(DataFrameModel):
        date_dtype: np.dtype("datetime64[ns]")

    df = pd.DataFrame(
        dict(
            date_dtype=pd.to_datetime(["2020-01-01"]),
        )
    )

    with pytest.raises(UnsupportedTypeError):
        MySchema.validate(df)


def test_categorical():
    CategoryABType = pd.CategoricalDtype(["a", "b"], ordered=True)

    class SpecificCategorySchema(DataFrameModel):
        category: CategoryABType

    df = pd.DataFrame({"category": ["a", "a", "b", "b"]})

    with pytest.raises(UnsupportedTypeError):
        SpecificCategorySchema.validate(df)


def test_obvious_mistakes():
    class MySchema(DataFrameModel):
        index: [0, 1, 2]
        column_a: "lol"

    df = pd.DataFrame({"index": [0, 1, 2, 2, 1, 2], "column_a": ["lol", "lol", "lol", "lol", "lol", "lol"]})

    with pytest.raises(UnsupportedTypeError):
        MySchema.validate(df)
