import datetime
import numpy as np
import pandas as pd

from pandabear import DataFrameModel, Field, Index


def test_datetime_index():

    class MySchema(DataFrameModel):
        date: Index[pd.DatetimeIndex]
        column_a: int

    df = pd.DataFrame(
        data = [200],
        columns=['column_a'],
        index=pd.DatetimeIndex(['2020-01-01'], name='date')
    )
    MySchema.validate(df)


def test_categorical_index():
    CategoryABType = pd.CategoricalDtype(['a', 'b'], ordered=True)
    categorical_index = pd.CategoricalIndex(list('aabb'), categories=['a', 'b'], ordered=True)

    class GenericCategorySchema(DataFrameModel):
        category: Index[pd.CategoricalIndex]
        column_a: int

    df = pd.DataFrame(
        data = [200, 300, 400, 500],
        columns=['column_a'],
        index=categorical_index
    )

    GenericCategorySchema.validate(df)

    class SpecificCategorySchema(DataFrameModel):
        category: Index[CategoryABType]
        column_a: int

    SpecificCategorySchema.validate(df)


def test_datetime_dtypes():

    class MySchema(DataFrameModel):
        date_datetime64: np.datetime64
        date_dtype: np.dtype('datetime64[ns]')
        date_datetime: datetime.datetime

    df = pd.DataFrame(dict(
        date_datetime64=pd.to_datetime(['2020-01-01']),
        date_dtype=pd.to_datetime(['2020-01-01']),
        date_datetime=pd.to_datetime(['2020-01-01']),
    ))

    MySchema.validate(df)


if __name__ == "__main__":
    test_datetime_index()
    test_datetime_dtypes()
    test_categorical_index()