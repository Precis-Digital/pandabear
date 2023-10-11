import pandas as pd
import pytest

from src.pandabear import (
    DataFrame,
    DataFrameModel,
    Field,
    Series,
    SeriesModel,
    check_types,
)


# Define a custom dataframe schema
class MySchema(DataFrameModel):
    column_a: int = Field(gt=0)
    column_b: str = Field(str_contains="foo")
    column_c: float = Field(ge=0.0, le=1.0)
    my_prefix_column: int = Field(alias="my_prefix.+", regex=True, ge=0)

# Define a custom series schema
class MySeries(SeriesModel):
    value: int = Field(gt=0, lt=10)


# Define an example dataframe that follows the dataframe schema
df = pd.DataFrame(
    dict(
        column_a=[1, 2, 3],
        column_b=["foo", "foo-bar", "baz-foo"],
        column_c=[0.1, 0.2, 0.3],
        my_prefix_column_a=[1, 2, 3],
        my_prefix_column_b=[4, 5, 6],
    )
)


@pytest.mark.check_types
class TestCheckTypes:
    def test_base_case_dataframe(self):
        """Test that the base case works for dataframes."""

        @check_types
        def my_function(df: DataFrame[MySchema]) -> DataFrame[MySchema]:
            return df

        my_function(df)

    def test_base_case_series(self):
        """Test that the base case works for series."""

        @check_types
        def my_function(se: Series[MySeries]) -> Series[MySeries]:
            return se

        my_function(df.column_a)

    def test_base_case_with_beartype(self):
        """Test that the base case works with beartype."""
        from beartype import beartype

        @beartype
        @check_types
        def my_function(df: DataFrame[MySchema], val: int) -> tuple[DataFrame[MySchema], int]:
            return df, val

        my_function(df, 1)
