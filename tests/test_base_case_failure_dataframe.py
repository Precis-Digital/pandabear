import pytest

from pandabear import DataFrame, DataFrameModel, Field, Series, SeriesModel, check_types


def test___base_case__failure__dataframe__in():
    """Test that the base case fails for dataframes, when input is fails."""
    with pytest.raises(ValueError):
        @check_types
        def my_function(df: DataFrame[MySchemaFailure]) -> DataFrame[MySchema]:
            return df

        my_function(df)


def test___base_case__failure__dataframe__out():
    """Test that the base case fails for dataframes, when output fails."""
    with pytest.raises(ValueError):
        @check_types
        def my_function(df: DataFrame[MySchema]) -> DataFrame[MySchemaFailure]:
            return df

        my_function(df)


def test___base_case__failure__dataframe__nested__in():
    """Test that the base case fails for dataframes, when input is fails."""
    with pytest.raises(ValueError):
        @check_types
        def my_function(
                df: tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchemaFailure]]]
        ) -> DataFrame[MySchema]:
            return df

        my_function([df, [df, df]])


def test___base_case__failure__dataframe__nested__out():
    """Test that the base case fails for dataframes, when input is fails."""
    with pytest.raises(ValueError):
        @check_types
        def my_function(
                df: DataFrame[MySchema],
        ) -> tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchemaFailure]]]:
            return [df, [df, df]]

        my_function(df)


def test___base_case__failure__dataframe__mismatch_in__1():
    """Test that the base case fails for dataframes, when input type hints do not match argument values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(tup: tuple[DataFrame[MySchema], DataFrame[MySchema]]) -> DataFrame[MySchema]:
            return tup[0]

        my_function(df)


def test___base_case__failure__dataframe__mismatch_in__2():
    """Test that the base case fails for dataframes, when input type hints do not match argument values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(df: DataFrame[MySchema]) -> DataFrame[MySchema]:
            return df

        my_function((df, df))


def test___base_case__failure__dataframe__mismatch_in__3():
    """Test that the base case fails for dataframes, when input type hints do not match argument values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(tup: tuple[DataFrame[MySchema], DataFrame[MySchema]]) -> DataFrame[MySchema]:
            return tup[0]

        my_function((df, [df, df]))


def test___base_case__failure__dataframe__mismatch_in__4():
    """Test that the base case fails for dataframes, when input type hints do not match argument values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(
                nested_df: tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchema]]]
        ) -> DataFrame[MySchema]:
            df, (df1, df2) = nested_df
            return df

        my_function((df, df, df))


def test___base_case__failure__dataframe__mismatch_out__1():
    """Test that the base case fails for dataframes, when output type hints do not match return values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(df: DataFrame[MySchema]) -> tuple[DataFrame[MySchema], DataFrame[MySchema]]:
            return df

        my_function(df)


def test___base_case__failure__dataframe__mismatch_out__2():
    """Test that the base case fails for dataframes, when output type hints do not match return values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(df: DataFrame[MySchema]) -> DataFrame[MySchema]:
            return df, df

        my_function(df)


def test___base_case__failure__dataframe__mismatch_out__3():
    """Test that the base case fails for dataframes, when output type hints do not match return values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(df: DataFrame[MySchema]) -> tuple[DataFrame[MySchema], DataFrame[MySchema]]:
            return df, [df, df]

        my_function(df)


def test___base_case__failure__dataframe__mismatch_out__4():
    """Test that the base case fails for dataframes, when output type hints do not match return values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(
                df: DataFrame[MySchema],
        ) -> tuple[DataFrame[MySchema], tuple[DataFrame[MySchema], DataFrame[MySchema]]]:
            return df, df, df

        my_function(df)
