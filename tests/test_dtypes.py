import datetime

import numpy as np
import pandas as pd

from pandabear import DataFrameModel, Field, Index


def test_datetime():
    class MySchema(DataFrameModel):
        date: Index[pd.DatetimeIndex]
        column_a: int

    df = pd.DataFrame(data=[200], columns=["column_a"], index=pd.DatetimeIndex(["2020-01-01"], name="date"))
    MySchema.validate(df)

    class MySchema(DataFrameModel):
        date: pd.DatetimeIndex
        column_a: int

    df = pd.DataFrame(data=[200], columns=["column_a"], index=pd.DatetimeIndex(["2020-01-01"], name="date"))
    MySchema.validate(df)

    class MySchema(DataFrameModel):
        index_date_datetime64: Index[np.datetime64]
        index_date_datetime: Index[datetime.datetime]
        date_datetime64: np.datetime64
        date_datetime: datetime.datetime

    df = pd.DataFrame(
        dict(
            date_datetime64=pd.to_datetime(["2020-01-01"]),
            date_datetime=pd.to_datetime(["2020-01-01"]),
        ),
        index=pd.MultiIndex.from_arrays(
            [
                pd.to_datetime(["2020-01-01"]),
                pd.to_datetime(["2020-01-01"]),
            ],
            names=["index_date_datetime64", "index_date_datetime"],
        ),
    )
    MySchema.validate(df)


def test_categorical_index():
    class GenericCategorySchema(DataFrameModel):
        category: pd.CategoricalIndex = Field()
        column_a: int

    df = pd.DataFrame(
        data=[200, 300, 400, 500],
        columns=["column_a"],
        index=pd.CategoricalIndex(list("aabb"), categories=["a", "b"], ordered=True, name="category"),
    )

    GenericCategorySchema.validate(df)
