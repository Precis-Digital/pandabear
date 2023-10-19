import pandas as pd
import pytest

from pandabear.model import TYPE_DTYPE_MAP, DataFrameModel
from pandabear.model_components import Field


def test_coerce_dtypes():
    class CoerceConfig:
        coerce: bool = True

    class MySchema(DataFrameModel):
        a: int = Field()
        b: float = Field()
        c: str = Field()

    # 1. will raise error

    df = pd.DataFrame(dict(a=["1"], b=[1], c=[2]))
    print(df.dtypes)
    expected_message = "Expected `a` with dtype <class 'int'> but found object"
    with pytest.raises(TypeError, match=expected_message):
        dfval = MySchema.validate(df)

    # 2. will coerce dtypes
    MySchema.Config = CoerceConfig
    dfval = MySchema.validate(df)
    assert dfval.dtypes.tolist() == [int, float, TYPE_DTYPE_MAP[str]]
    assert dfval.a.tolist() == [1]
    assert dfval.b.tolist() == [1.0]
    assert dfval.c.tolist() == ["2"]


if __name__ == "__main__":
    test_coerce_dtypes()
