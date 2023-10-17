import pandas as pd
import pytest

from pandabear.index_type import Index
from pandabear.model import DataFrameModel, SeriesModel
from pandabear.model_components import Field


class IndexStrictConfig:
    multiindex_strict: bool = True


class IndexOrderedConfig:
    multiindex_ordered: bool = True


class IndexSortedConfig:
    multiindex_sorted: bool = True


class IndexUniqueConfig:
    multiindex_unique: bool = True


class NoIndexSchema(DataFrameModel):
    a: int = Field()
    b: float = Field()


class IndexSchema(DataFrameModel):
    index: Index[str]
    a: int = Field()
    b: float = Field()


def test_no_index_schema__passing():

    df = pd.DataFrame(dict(a=[1], b=[1.0]))

    # 1. passes
    NoIndexSchema._validate_multiindex(df)

    # 2. Strict
    NoIndexSchema.Config = IndexStrictConfig
    NoIndexSchema._validate_multiindex(df)

    # 3. Ordered
    NoIndexSchema.Config = IndexOrderedConfig
    NoIndexSchema._validate_multiindex(df)

    # 4. Sorted
    NoIndexSchema.Config = IndexSortedConfig
    NoIndexSchema._validate_multiindex(df)

    # 5. Unique
    NoIndexSchema.Config = IndexUniqueConfig
    NoIndexSchema._validate_multiindex(df)


def test_no_index_schema__failing():
    df = pd.DataFrame(dict(a=[1, 2], b=[1.0, 2.0]), index=pd.Index([1, 2], name="index"))
    with pytest.raises(ValueError):
        NoIndexSchema._validate_multiindex(df)


def test_index_schema__passing():
    df = pd.DataFrame(dict(a=[1, 2, 3], b=[1.0, 2.0, 3.0]), index=pd.Index([1, 2, 3], name="index"))

    # 1. passes
    IndexSchema._validate_multiindex(df)

    # 2. Strict
    IndexSchema.Config = IndexStrictConfig
    IndexSchema._validate_multiindex(df)

    # 3. Ordered
    IndexSchema.Config = IndexOrderedConfig
    IndexSchema._validate_multiindex(df)

    # 4. Sorted
    IndexSchema.Config = IndexSortedConfig
    IndexSchema._validate_multiindex(df)

    # 5. Unique
    IndexSchema.Config = IndexUniqueConfig
    IndexSchema._validate_multiindex(df)


def test_index_schema__failing_sorting_unique():
    df = pd.DataFrame(dict(a=[1, 2, 3, 4], b=[1.0, 2.0, 3.0, 4.0]), index=pd.Index([1, 3, 2, 3], name="index"))

    class IndexSchema(DataFrameModel):
        index: Index[str]
        a: int = Field()
        b: float = Field()

    # 1. passes
    IndexSchema._validate_multiindex(df)

    # 2. Strict
    IndexSchema.Config = IndexStrictConfig
    IndexSchema._validate_multiindex(df)

    # 3. Ordered
    IndexSchema.Config = IndexOrderedConfig
    IndexSchema._validate_multiindex(df)

    # 4. Sorted fails
    with pytest.raises(ValueError):
        IndexSchema.Config = IndexSortedConfig
        IndexSchema._validate_multiindex(df)

    # 5. Unique, failing
    with pytest.raises(ValueError):
        IndexSchema.Config = IndexUniqueConfig
        IndexSchema._validate_multiindex(df)


def test_multiindex_schema__passing():
    class MultiIndexSchema(DataFrameModel):
        ix0: Index[int] = Field()
        ix1: Index[int] = Field()
        a: int = Field()

    df = pd.DataFrame(
        dict(a=[1, 2, 3, 4], b=[1.0, 2.0, 3.0, 4.0]),
        index=pd.MultiIndex.from_tuples([(1, 1), (1, 2), (2, 1), (2, 2)], names=["ix0", "ix1"]),
    )

    # 1. passes
    MultiIndexSchema._validate_multiindex(df)

    # 2. ordered
    MultiIndexSchema.Config = IndexOrderedConfig
    MultiIndexSchema._validate_multiindex(df)

    # 3. sorted
    MultiIndexSchema.Config = IndexSortedConfig
    MultiIndexSchema._validate_multiindex(df)

    # 4. unique
    MultiIndexSchema.Config = IndexUniqueConfig
    MultiIndexSchema._validate_multiindex(df)


def test_multiindex_schema__failing():
    class MultiIndexSchema(DataFrameModel):
        ix0: Index[int] = Field()
        ix1: Index[int] = Field()
        a: int = Field()

    df = pd.DataFrame(
        dict(a=[1, 2, 3, 4], b=[1.0, 2.0, 3.0, 4.0]),
        index=pd.MultiIndex.from_tuples([(1, 1), (1, 1), (2, 2), (2, 1)], names=["ix0", "ix1"]),
    )

    # 1. passes
    MultiIndexSchema._validate_multiindex(df)

    # 3. sorted
    with pytest.raises(ValueError):
        MultiIndexSchema.Config = IndexSortedConfig
        MultiIndexSchema._validate_multiindex(df)

    # 4. unique
    with pytest.raises(ValueError):
        MultiIndexSchema.Config = IndexUniqueConfig
        MultiIndexSchema._validate_multiindex(df)

    # 2. ordered, passing
    MultiIndexSchema.Config = IndexOrderedConfig
    MultiIndexSchema._validate_multiindex(df)

    # 2. ordered, failing
    with pytest.raises(ValueError):
        MultiIndexSchema.Config = IndexOrderedConfig
        df.index.names = ["ix1", "ix0"]
        MultiIndexSchema._validate_multiindex(df)

    df2 = df.reset_index()
    with pytest.raises(ValueError):
        MultiIndexSchema._validate_multiindex(df2)
