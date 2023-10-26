import pandas as pd
import pytest

from pandabear.exceptions import MissingIndexError, SchemaValidationError
from pandabear.model import DataFrameModel
from pandabear.model_components import Field, Index


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
    NoIndexSchema._validate_multiindex(df, NoIndexSchema._get_schema_map(), NoIndexSchema._get_config())

    # 2. Strict
    NoIndexSchema.Config = IndexStrictConfig
    NoIndexSchema._validate_multiindex(df, NoIndexSchema._get_schema_map(), NoIndexSchema._get_config())

    # 3. Ordered
    NoIndexSchema.Config = IndexOrderedConfig
    NoIndexSchema._validate_multiindex(df, NoIndexSchema._get_schema_map(), NoIndexSchema._get_config())

    # 4. Sorted
    NoIndexSchema.Config = IndexSortedConfig
    NoIndexSchema._validate_multiindex(df, NoIndexSchema._get_schema_map(), NoIndexSchema._get_config())

    # 5. Unique
    NoIndexSchema.Config = IndexUniqueConfig
    NoIndexSchema._validate_multiindex(df, NoIndexSchema._get_schema_map(), NoIndexSchema._get_config())


def test_no_index_schema__failing():
    df = pd.DataFrame(dict(a=[1, 2], b=[1.0, 2.0]), index=pd.Index([1, 2], name="index"))
    with pytest.raises(SchemaValidationError):
        NoIndexSchema._validate_multiindex(df, NoIndexSchema._get_schema_map(), NoIndexSchema._get_config())


def test_index_schema__passing():
    df = pd.DataFrame(dict(a=[1, 2, 3], b=[1.0, 2.0, 3.0]), index=pd.Index([1, 2, 3], name="index"))

    # 1. passes
    IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())

    # 2. Strict
    IndexSchema.Config = IndexStrictConfig
    IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())

    # 3. Ordered
    IndexSchema.Config = IndexOrderedConfig
    IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())

    # 4. Sorted
    IndexSchema.Config = IndexSortedConfig
    IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())

    # 5. Unique
    IndexSchema.Config = IndexUniqueConfig
    IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())


def test_index_schema__failing_sorting_unique():
    df = pd.DataFrame(dict(a=[1, 2, 3, 4], b=[1.0, 2.0, 3.0, 4.0]), index=pd.Index([1, 3, 2, 3], name="index"))

    class IndexSchema(DataFrameModel):
        index: Index[str]
        a: int = Field()
        b: float = Field()

    # 1. passes
    IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())

    # 2. Strict
    IndexSchema.Config = IndexStrictConfig
    IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())

    # 3. Ordered
    IndexSchema.Config = IndexOrderedConfig
    IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())

    # 4. Sorted fails
    with pytest.raises(SchemaValidationError):
        IndexSchema.Config = IndexSortedConfig
        IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())

    # 5. Unique, failing
    with pytest.raises(SchemaValidationError):
        IndexSchema.Config = IndexUniqueConfig
        IndexSchema._validate_multiindex(df, IndexSchema._get_schema_map(), IndexSchema._get_config())


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
    MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())

    # 2. ordered
    MultiIndexSchema.Config = IndexOrderedConfig
    MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())

    # 3. sorted
    MultiIndexSchema.Config = IndexSortedConfig
    MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())

    # 4. unique
    MultiIndexSchema.Config = IndexUniqueConfig
    MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())


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
    MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())

    # 3. sorted
    with pytest.raises(SchemaValidationError):
        MultiIndexSchema.Config = IndexSortedConfig
        MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())

    # 4. unique
    with pytest.raises(SchemaValidationError):
        MultiIndexSchema.Config = IndexUniqueConfig
        MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())

    # 2. ordered, passing
    MultiIndexSchema.Config = IndexOrderedConfig
    MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())

    # 2. ordered, failing
    with pytest.raises(SchemaValidationError):
        MultiIndexSchema.Config = IndexOrderedConfig
        df.index.names = ["ix1", "ix0"]
        MultiIndexSchema._validate_multiindex(df, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())

    df2 = df.reset_index()
    with pytest.raises(MissingIndexError):
        MultiIndexSchema._validate_multiindex(df2, MultiIndexSchema._get_schema_map(), MultiIndexSchema._get_config())


def test_multiindex_check_index_name__success():
    class Coefficients(DataFrameModel):
        index: Index[str] = Field(check_index_name=False)
        credit: float = Field(ge=0, coerce=True)

    df = pd.DataFrame(
        {
            "credit": [0.2, 0.3],
        }
    )
    df.index = ["paid_search_brand", "youtube"]
    df.index.name = "channel"

    # 1. passes
    Coefficients.validate(df)


def test_multiindex_check_index_name__failing():
    class Coefficients(DataFrameModel):
        index: Index[str] = Field(check_index_name=True)
        credit: float = Field(ge=0, coerce=True)

    df = pd.DataFrame(
        {
            "credit": [0.2, 0.3],
        }
    )
    df.index = ["paid_search_brand", "youtube"]
    df.index.name = "channel"

    # 1. fails
    with pytest.raises(MissingIndexError):
        Coefficients.validate(df)
