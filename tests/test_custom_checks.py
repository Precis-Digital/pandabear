import pandas as pd
import pytest

from pandabear import DataFrameModel, Field, check


@pytest.mark.custom_checks
class TestCustomChecksSuccessSeries:
    def test___custom_checks__success__series__1(self):
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

    def test___custom_checks__success__series__2(self):
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

    def test___custom_checks__success__series__3(self):
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

    def test___custom_checks__success__series__4(self):
        """Test that the custom checks works for multiple series, with regex."""

        class MySchema(DataFrameModel):
            column_a: int = Field()
            column_c: float = Field()

            @check(r"column_\w", regex=True)
            def check_column(column: pd.Series) -> bool:
                return column.sum() > 0

        df = pd.DataFrame(
            dict(
                column_a=[1, 2, 3],
                column_c=[0.1, 0.2, 0.3],
            )
        )

        MySchema.validate(df)

    def test___custom_checks__success__series__5(self):
        """Test that the custom checks works for multiple series, with multiple regex."""

        class MySchema(DataFrameModel):
            column_a: int = Field()
            column_c: float = Field()
            series_a: int = Field()
            series_c: float = Field()

            @check([r"column_\w", r"series_\w"], regex=True)
            def check_column(column: pd.Series) -> bool:
                return column.sum() > 0

        df = pd.DataFrame(
            dict(
                column_a=[1, 2, 3],
                column_c=[0.1, 0.2, 0.3],
                series_a=[1, 2, 3],
                series_c=[0.1, 0.2, 0.3],
            )
        )

        MySchema.validate(df)


@pytest.mark.custom_checks
class TestCustomChecksFailureSeries:
    def test___custom_checks__failure__series__1(self):
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

    def test___custom_checks__failure__series__2(self):
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

    def test___custom_checks__failure__series__3(self):
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

    def test___custom_checks__failure__series__4(self):
        """Test that the custom checks fails when bad column names are passed to decorator."""
        with pytest.raises(ValueError):

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

    def test___custom_checks__failure__series__5(self):
        """Test that the custom checks fails when bad column regex is passed to decorator."""
        with pytest.raises(ValueError):

            class MySchema(DataFrameModel):
                column_a: int = Field()
                column_b: int = Field()

                @check("bad_pattern.+", regex=True)
                def check_column(column: pd.Series) -> bool:
                    return column.sum() > 0

            df = pd.DataFrame(
                dict(
                    column_a=[1, 2, 3],
                )
            )

            MySchema.validate(df)
