import pandas as pd
import pytest

from pandabear import DataFrameModel, Field
from pandabear.decorators import dataframe_check


def test__validate_custom_dataframe_check__success():
    """Test that the custom checks works for dataframes."""

    class MySchema(DataFrameModel):
        column_a: int = Field()
        column_b: int = Field()

        @dataframe_check
        def check_df(df: pd.DataFrame) -> bool:
            return df.sum().sum() > 0

    df = pd.DataFrame(
        dict(
            column_a=[1, 2, 3],
            column_b=[1, 0, 3],
        )
    )

    assert hasattr(MySchema.check_df, "__check__")
    assert getattr(MySchema.check_df, "__check__") is None

    MySchema.validate(df)


def test__validate_custom_dataframe_check__failure():
    """Test that the custom checks fails foir datafrane check."""

    class MySchema(DataFrameModel):
        column_a: int = Field()
        column_b: int = Field()

        @dataframe_check
        def check_df(df: pd.DataFrame) -> bool:
            return (df > 0).all().all()

    df = pd.DataFrame(
        dict(
            column_a=[1, 2, 3],
            column_b=[-1, 1, 2],
        )
    )

    with pytest.raises(ValueError):
        MySchema.validate(df)
