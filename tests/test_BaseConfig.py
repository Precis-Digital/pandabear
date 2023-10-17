from pandabear.model import DataFrameModel, Field
from pandabear.model_components import BaseConfig


def test_default_config():
    """This test checks whether the default configuration values of a
    DataFrameModel subclass are the same as the default configuration values
    of the BaseConfig class."""

    class MySchema(DataFrameModel):
        a: int
        b: str

    Config = MySchema._get_config()
    for name, typ in Config.__annotations__.items():
        val = getattr(Config, name)
        print(name, typ, val)
        assert getattr(Config, name) == getattr(BaseConfig, name)
        assert isinstance(typ, type)


def test_override_config():
    """This test checks whether the _override method of the BaseConfig class
    works correctly with DataFrameModel subclasses that have inheritance.
    """

    # 1. Test of BaseConfig override works

    class MyConfig:
        filter = True

    Config = BaseConfig._override(MyConfig)

    print(Config.__annotations__)
    assert Config.__annotations__ == BaseConfig.__annotations__
    assert Config.filter is True
    assert Config.strict is True

    # 2. Test if this works with DataFrameModel

    class MySchema(DataFrameModel):
        a: int
        b: str
        Config = MyConfig

    Config = MySchema._get_config()

    assert Config.__annotations__ == BaseConfig.__annotations__
    assert Config.filter is True

    # 3. test that it works for DataFrameModel with inheritance

    class MySchema(DataFrameModel):
        a: int
        b: str
        Config = MyConfig

    class MySchema2(MySchema):
        c: float

    Config = MySchema2._get_config()

    assert Config.__annotations__ == BaseConfig.__annotations__
    assert Config.filter is True


if __name__ == "__main__":
    test_default_config()
    test_override_config()
    print("Done")
