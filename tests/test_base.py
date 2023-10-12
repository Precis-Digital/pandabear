import pandas as pd
import pytest

from pandabear import DataFrame, DataFrameModel, Field, Series, SeriesModel, check_types


# Define a custom dataframe schema
class MySchema(DataFrameModel):
    column_a: int = Field(gt=0)
    column_b: str = Field(str_contains="foo")
    column_c: float = Field(ge=0.0, le=1.0)
    my_prefix_column: int = Field(alias="my_prefix.+", regex=True, ge=0)


class MySchemaFailure(DataFrameModel):
    column_a: int = Field(gt=1)
    column_b: str = Field(str_contains="bar")
    column_c: float = Field(ge=0.0, le=0.1)
    my_prefix_column: int = Field(alias="my_prefix.+", regex=True, ge=5)


# Define a custom series schema
class MySeries(SeriesModel):
    value: int = Field(gt=0, lt=10)


class MySeriesFailure(SeriesModel):
    value: int = Field(gt=2, lt=2)


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


@pytest.mark.base_case
class TestBaseCase:
    # --------------------------- #
    #        Success cases        #
    # .. things that should work  #
    # --------------------------- #

    # For dataframes

    def test___base_case__success__dataframe__1(self):
        """Test that the base case works for dataframes."""

        @check_types
        def my_function(df: DataFrame[MySchema]) -> DataFrame[MySchema]:
            return df

        my_function(df)

    def test___base_case__success__dataframe__multiple_in(self):
        """Test that the base case works for dataframes."""

        @check_types
        def my_function(dfs: tuple[DataFrame[MySchema], DataFrame[MySchema]]) -> DataFrame[MySchema]:
            df, df1 = dfs
            return df

        my_function([df, df])

    def test___base_case__success__dataframe__multiple_out(self):
        """Test that the base case works for dataframes."""

        @check_types
        def my_function(df: DataFrame[MySchema]) -> tuple[DataFrame[MySchema], DataFrame[MySchema]]:
            return df, df

        my_function(df)

    def test___base_case__success__dataframe__nested_in__1(self):
        """Test that the base case works for dataframes."""

        @check_types
        def my_function(
            nested_df: tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchema]]]
        ) -> DataFrame[MySchema]:
            df, (df1, df2) = nested_df
            return df

        my_function([df, [df, df]])

    def test___base_case__success__dataframe__nested_in__2(self):
        """Test that the base case works for dataframes."""

        @check_types
        def my_function(
            nested_df: tuple[
                DataFrame[MySchema], tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchema]]]
            ]
        ) -> DataFrame[MySchema]:
            df, (df1, (df2, df3)) = nested_df
            return df

        my_function([df, [df, [df, df]]])

    def test___base_case__success__dataframe__nested_out__1(self):
        """Test that the base case works for dataframes."""

        @check_types
        def my_function(
            df: DataFrame[MySchema],
        ) -> tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchema]]]:
            return df, [df, df]

        my_function(df)

    def test___base_case__success__dataframe__nested_out__2(self):
        """Test that the base case works for dataframes."""

        @check_types
        def my_function(
            df: DataFrame[MySchema],
        ) -> tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchema]]]]:
            return df, [df, [df, df]]

        my_function(df)

    def test___base_case__success__dataframe__with_beartype(self):
        """Test that the base case works for dataframes with beartype."""
        from beartype import beartype

        @beartype
        @check_types
        def my_function(df: DataFrame[MySchema], val: int) -> tuple[DataFrame[MySchema], int]:
            return df, val

        my_function(df, 1)

    # For series

    def test___base_case__success__series(self):
        """Test that the base case works for series."""

        @check_types
        def my_function(se: Series[MySeries]) -> Series[MySeries]:
            return se

        my_function(df.column_a)

    def test___base_case__success__series__multiple_out(self):
        """Test that the base case works for series."""

        @check_types
        def my_function(se: Series[MySeries]) -> tuple[Series[MySeries], Series[MySeries]]:
            return se, se

        my_function(df.column_a)

    def test___base_case__success__series__nested_out__1(self):
        """Test that the base case works for series."""

        @check_types
        def my_function(
            se: Series[MySeries],
        ) -> tuple[Series[MySeries], tuple[Series[MySeries], Series[MySeries]]]:
            return se, (se, se)

        my_function(df.column_a)

    def test___base_case__success__series__nested_out__2(self):
        """Test that the base case works for series."""

        @check_types
        def my_function(
            se: Series[MySeries],
        ) -> tuple[Series[MySeries], tuple[Series[MySeries], tuple[Series[MySeries], Series[MySeries]]]]:
            return se, (se, (se, se))

        my_function(df.column_a)

    def test___base_case__success__series__with_beartype(self):
        """Test that the base case works for series with beartype."""
        from beartype import beartype

        @beartype
        @check_types
        def my_function(se: Series[MySeries], val: int) -> tuple[Series[MySeries], int]:
            return se, 1

        my_function(df.column_a, 1)

    # --------------------------- #
    #        Failure cases        #
    # .. things that should break #
    # --------------------------- #

    def test___base_case__failure__dataframe__in(self):
        """Test that the base case fails for dataframes, when input is fails."""
        with pytest.raises(ValueError):

            @check_types
            def my_function(df: DataFrame[MySchemaFailure]) -> DataFrame[MySchema]:
                return df

            my_function(df)

    def test___base_case__failure__dataframe__out(self):
        """Test that the base case fails for dataframes, when output fails."""
        with pytest.raises(ValueError):

            @check_types
            def my_function(df: DataFrame[MySchema]) -> DataFrame[MySchemaFailure]:
                return df

            my_function(df)

    def test___base_case__failure__dataframe__nested__in(self):
        """Test that the base case fails for dataframes, when input is fails."""
        with pytest.raises(ValueError):

            @check_types
            def my_function(
                df: tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchemaFailure]]]
            ) -> DataFrame[MySchema]:
                return df

            my_function([df, [df, df]])

    def test___base_case__failure__dataframe__nested__out(self):
        """Test that the base case fails for dataframes, when input is fails."""
        with pytest.raises(ValueError):

            @check_types
            def my_function(
                df: DataFrame[MySchema],
            ) -> tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchemaFailure]]]:
                return [df, [df, df]]

            my_function(df)

    def test___base_case__failure__dataframe__mismatch_in__1(self):
        """Test that the base case fails for dataframes, when input type hints do not match argument values."""
        with pytest.raises(TypeError):

            @check_types
            def my_function(tup: tuple[DataFrame[MySchema], DataFrame[MySchema]]) -> DataFrame[MySchema]:
                return tup[0]

            my_function(df)

    def test___base_case__failure__dataframe__mismatch_in__2(self):
        """Test that the base case fails for dataframes, when input type hints do not match argument values."""
        with pytest.raises(TypeError):

            @check_types
            def my_function(df: DataFrame[MySchema]) -> DataFrame[MySchema]:
                return df

            my_function((df, df))

    def test___base_case__failure__dataframe__mismatch_in__3(self):
        """Test that the base case fails for dataframes, when input type hints do not match argument values."""
        with pytest.raises(TypeError):

            @check_types
            def my_function(tup: tuple[DataFrame[MySchema], DataFrame[MySchema]]) -> DataFrame[MySchema]:
                return tup[0]

            my_function((df, [df, df]))

    def test___base_case__failure__dataframe__mismatch_in__4(self):
        """Test that the base case fails for dataframes, when input type hints do not match argument values."""
        with pytest.raises(TypeError):

            @check_types
            def my_function(
                nested_df: tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchema]]]
            ) -> DataFrame[MySchema]:
                df, (df1, df2) = nested_df
                return df

            my_function((df, df, df))

    def test___base_case__failure__dataframe__mismatch_out__1(self):
        """Test that the base case fails for dataframes, when output type hints do not match return values."""
        with pytest.raises(TypeError):

            @check_types
            def my_function(df: DataFrame[MySchema]) -> tuple[DataFrame[MySchema], DataFrame[MySchema]]:
                return df

            my_function(df)

    def test___base_case__failure__dataframe__mismatch_out__2(self):
        """Test that the base case fails for dataframes, when output type hints do not match return values."""
        with pytest.raises(TypeError):

            @check_types
            def my_function(df: DataFrame[MySchema]) -> DataFrame[MySchema]:
                return df, df

            my_function(df)

    def test___base_case__failure__dataframe__mismatch_out__3(self):
        """Test that the base case fails for dataframes, when output type hints do not match return values."""
        with pytest.raises(TypeError):

            @check_types
            def my_function(df: DataFrame[MySchema]) -> tuple[DataFrame[MySchema], DataFrame[MySchema]]:
                return df, [df, df]

            my_function(df)

    def test___base_case__failure__dataframe__mismatch_out__4(self):
        """Test that the base case fails for dataframes, when output type hints do not match return values."""
        with pytest.raises(TypeError):

            @check_types
            def my_function(
                df: DataFrame[MySchema],
            ) -> tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchema]]]:
                return df, df, df

            my_function(df)
