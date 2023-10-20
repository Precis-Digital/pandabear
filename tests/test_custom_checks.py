import pandas as pd
import pytest

from pandabear import DataFrameModel, Field, check
from pandabear.exceptions import SchemaDefinitionError


class TestCustomChecksSuccessDataFrame:
    def test___custom_checks__success__dataframe__1(self):
        """Test that the custom checks works for series."""

        class MySchema(DataFrameModel):
            column_a: int = Field()

            @check("column_a")
            def check_column_a(column_a: pd.Series) -> bool:
                return column_a.sum() > 0

        df = pd.DataFrame(
            dict(
                column_a=[1, 2, 3],
            )
        )

        MySchema.validate(df)

    def test___custom_checks__success__dataframe__2(self):
        """Test that the custom checks works for multiple series."""

        class MySchema(DataFrameModel):
            column_a: int = Field()
            column_c: float = Field()

            @check(["column_a", "column_c"])
            def check_column(column: pd.Series) -> bool:
                return column.sum() > 0

        df = pd.DataFrame(
            dict(
                column_a=[1, 2, 3],
                column_c=[0.1, 0.2, 0.3],
            )
        )

        MySchema.validate(df)

    def test___custom_checks__success__dataframe__3(self):
        """Test that the custom checks works for multiple series, with multiple check functions."""

        class MySchema(DataFrameModel):
            column_a: int = Field()
            column_c: float = Field()

            @check("column_a")
            def check_column_a(column_a: pd.Series) -> bool:
                return column_a.sum() > 0

            @check("column_c")
            def check_column_c(column_c: pd.Series) -> bool:
                return column_c.sum() > 0

        df = pd.DataFrame(
            dict(
                column_a=[1, 2, 3],
                column_c=[0.1, 0.2, 0.3],
            )
        )

        MySchema.validate(df)


class TestCustomChecksFailureDataFrame:
    def test___custom_checks__failure__dataframe__1(self):
        """Test that the custom checks fails when check does not pass."""
        with pytest.raises(ValueError):

            class MySchema(DataFrameModel):
                column_a: int = Field()

                @check("column_a")
                def check_column_a(column_a: pd.Series) -> bool:
                    return column_a.sum() > 0

            df = pd.DataFrame(
                dict(
                    column_a=[-1, -2, -3],
                )
            )

            MySchema.validate(df)

    def test___custom_checks__failure__dataframe__2(self):
        """Test that the custom checks fails when one of checks do not pass."""
        with pytest.raises(ValueError):

            class MySchema(DataFrameModel):
                column_a: int = Field()
                column_b: int = Field()

                @check(["column_a", "column_b"])
                def check_column_a(column: pd.Series) -> bool:
                    return column.sum() > 0

            df = pd.DataFrame(
                dict(
                    column_a=[1, 2, 3],
                    column_b=[-1, -2, -3],
                )
            )

            MySchema.validate(df)

    def test___custom_checks__failure__dataframe__3(self):
        """Test that the custom checks fails when no column name is passed to decorator."""
        with pytest.raises(TypeError):

            class MySchema(DataFrameModel):
                column_a: int = Field()
                column_b: int = Field()

                @check()
                def check_column(column: pd.Series) -> bool:
                    return column.sum() > 0

            df = pd.DataFrame(
                dict(
                    column_a=[1, 2, 3],
                    column_b=[-1, -2, -3],
                )
            )

            MySchema.validate(df)

    def test___custom_checks__failure__dataframe__4(self):
        """Test that the custom checks fails when bad column names are passed to decorator."""
        with pytest.raises(SchemaDefinitionError):

            class MySchema(DataFrameModel):
                column_a: int = Field()
                column_b: int = Field()

                @check("column_c")
                def check_column(column: pd.Series) -> bool:
                    return column.sum() > 0

            df = pd.DataFrame(
                dict(
                    column_a=[1, 2, 3],
                    column_b=[-1, -2, -3],
                )
            )

            MySchema.validate(df)
