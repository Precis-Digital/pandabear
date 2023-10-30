import numpy as np
import pandas as pd
import pytest

from pandabear.exceptions import CoersionError, SchemaValidationError
from pandabear.model import DataFrameModel
from pandabear.model_components import Field, Index


def test_coerce_base_case():
    class CoerceConfig:
        coerce: bool = True

    class MySchema(DataFrameModel):
        a: int = Field()
        b: float = Field()
        c: str = Field()

    # 1. will raise error

    df = pd.DataFrame(dict(a=["1"], b=[1], c=[2]))
    print(df.dtypes)
    expected_message = "Expected `a` with dtype <class 'int'> but found dtype `object`"
    with pytest.raises(SchemaValidationError, match=expected_message):
        dfval = MySchema.validate(df)

    # 2. will coerce dtypes
    MySchema.Config = CoerceConfig
    dfval = MySchema.validate(df)
    assert dfval.dtypes.a == int
    assert dfval.dtypes.b == float
    assert dfval.dtypes.c == np.dtype("O")
    assert dfval.a.tolist() == [1]
    assert dfval.b.tolist() == [1.0]
    assert dfval.c.tolist() == ["2"]


class TestCoerceSuccess:
    def test___coerce__index__success__1(self):
        class MySchema(DataFrameModel):
            index: Index[str] = Field(alias="index\d", regex=True)
            column_a: int = Field(ge=0)

            class Config:
                coerce = True

        df = pd.DataFrame(dict(column_a=[4, 5, 6]), index=[1, 2, 3]).rename_axis("index0")

        df_out = MySchema.validate(df)

        assert df_out.index.dtype == "object"

    def test___coerce__index__success__2(self):
        class MySchema(DataFrameModel):
            index: Index[int] = Field(alias="index\d", regex=True)
            column_a: int = Field(ge=0)

            class Config:
                coerce = True

        df = pd.DataFrame(dict(column_a=[4, 5, 6]), index=["1", "2", "3"]).rename_axis("index0")

        df_out = MySchema.validate(df)

        assert df_out.index.dtype == int

    def test___coerce__multi_index__success__1(self):
        class MySchema(DataFrameModel):
            index: Index[bool] = Field(alias="index\d", regex=True)
            column_a: int = Field(ge=0)

            class Config:
                coerce = True

        df = pd.DataFrame(
            data=dict(column_a=[1, 2, 3]),
            index=pd.MultiIndex.from_arrays([["foo", "bar", "foo"], [0, 1, 2]], names=["index0", "index1"]),
        )

        df_out = MySchema.validate(df)

        assert df_out.index.get_level_values("index0").dtype == bool
        assert df_out.index.get_level_values("index1").dtype == bool

    def test___coerce__multi_index__success__2(self):
        class MySchema(DataFrameModel):
            index: Index[bool] = Field(alias="index\d", regex=True, coerce=True)
            column_a: int = Field(ge=0)

        df = pd.DataFrame(
            data=dict(column_a=[1, 2, 3]),
            index=pd.MultiIndex.from_arrays([["foo", "bar", "foo"], [0, 1, 2]], names=["index0", "index1"]),
        )

        df_out = MySchema.validate(df)

        assert df_out.index.get_level_values("index0").dtype == bool
        assert df_out.index.get_level_values("index1").dtype == bool

    def test___coerce__column__success__1(self):
        class MySchema(DataFrameModel):
            column_a: int = Field(ge=0)

            class Config:
                coerce = True

        df = pd.DataFrame(dict(column_a=["4", "5", "6"]))

        df_out = MySchema.validate(df)

        assert df_out["column_a"].dtype == int

    def test___coerce__column__success__2(self):
        class MySchema(DataFrameModel):
            column_a: str = Field()

            class Config:
                coerce = True

        df = pd.DataFrame(dict(column_a=[4, 5, 6]))

        df_out = MySchema.validate(df)

        assert df_out["column_a"].dtype == "object"


class TestCoerceFailure:
    def test___coerce__index__failure(self):
        class MySchema(DataFrameModel):
            index: Index[int] = Field(alias="index\d", regex=True)
            column_a: int = Field(ge=0)

            class Config:
                coerce = True

        df = pd.DataFrame(dict(column_a=[4, 5, 6]), index=["a", "b", "c"]).rename_axis("index0")

        with pytest.raises(CoersionError):
            MySchema.validate(df)

    def test___coerce__column__failure(self):
        class MySchema(DataFrameModel):
            column_a: int = Field(ge=0)

            class Config:
                coerce = True

        df = pd.DataFrame(dict(column_a=["a", "b", "c"]))

        with pytest.raises(CoersionError):
            MySchema.validate(df)
