"""Test that Optional fields work as expected.

The user should be able to provide a field that is optional. For example:

    class MySchema(DataFrameModel):
        column_a: Optional[int] = Field()

        class Config:
            strict = True

    df = pd.DataFrame({})
    MySchema.validate(df)

Should pass without any errors.
"""

from typing import Optional

import pandas as pd
import pytest

from pandabear import DataFrame, DataFrameModel, Field
from pandabear.exceptions import MissingColumnsError


@pytest.mark.custom_checks
class TestOptionalSuccess:
    def test___optional__success__column_name(self):
        """Test that optional fields work in the simplest case."""

        class MySchema(DataFrameModel):
            column_a: Optional[int] = Field()
            column_b: int = Field()

        MySchema.validate(
            pd.DataFrame(
                dict(
                    column_a=[1, 2, 3],
                    column_b=[4, 5, 6],
                )
            )
        )

        MySchema.validate(
            pd.DataFrame(
                dict(
                    # column_a=[1, 2, 3],
                    column_b=[4, 5, 6],
                )
            )
        )

    def test___optional__success__alias(self):
        """Test that optional fields work in the simplest case."""

        class MySchema(DataFrameModel):
            column_a: Optional[int] = Field(alias="column_x")
            column_b: int = Field()

        MySchema.validate(
            pd.DataFrame(
                dict(
                    column_x=[1, 2, 3],
                    column_b=[4, 5, 6],
                )
            )
        )

        MySchema.validate(
            pd.DataFrame(
                dict(
                    # column_x=[1, 2, 3],
                    column_b=[4, 5, 6],
                )
            )
        )

    def test___optional__success__regex(self):
        """Test that optional fields work in the simplest case."""

        class MySchema(DataFrameModel):
            column_a: Optional[int] = Field(alias="series.+", regex=True)
            column_b: int = Field()

        MySchema.validate(
            pd.DataFrame(
                dict(
                    series_99=[1, 2, 3],
                    column_b=[4, 5, 6],
                )
            )
        )

        MySchema.validate(
            pd.DataFrame(
                dict(
                    # series_99=[1, 2, 3],
                    column_b=[4, 5, 6],
                )
            )
        )


@pytest.mark.custom_checks
class TestOptionalFailure:
    def test___optional__failure__column_name(self):
        """Test that optional fields fails in the simplest case."""

        class MySchema(DataFrameModel):
            column_a: int = Field()
            column_b: int = Field()

        with pytest.raises(MissingColumnsError):
            MySchema.validate(
                pd.DataFrame(
                    dict(
                        # column_a=[1, 2, 3],
                        column_b=[4, 5, 6],
                    )
                )
            )

    def test___optional__failure__alias(self):
        """Test that optional fields fails in the simplest case."""

        class MySchema(DataFrameModel):
            column_a: int = Field(alias="column_x")
            column_b: int = Field()

        with pytest.raises(MissingColumnsError):
            MySchema.validate(
                pd.DataFrame(
                    dict(
                        # column_x=[1, 2, 3],
                        column_b=[4, 5, 6],
                    )
                )
            )

    def test___optional__failure__regex(self):
        """Test that optional fields fails in the simplest case."""

        class MySchema(DataFrameModel):
            column_a: int = Field(alias="series.+", regex=True)
            column_b: int = Field()

        with pytest.raises(MissingColumnsError):
            MySchema.validate(
                pd.DataFrame(
                    dict(
                        # series_99=[1, 2, 3],
                        column_b=[4, 5, 6],
                    )
                )
            )
