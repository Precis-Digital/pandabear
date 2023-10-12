from pandabear.model import DataFrameModel, SeriesModel

from pandabear.model_components import Field
from pandabear.typing_ import DataFrame, Index, Series

class MySchema(DataFrameModel):
    A: Index[str] = Field()
    B: Index[int] = Field()
    C: str = Field()



nt = MySchema._get_names_and_types()

at = nt['A']

print(dir(at))

print(at.__parameters__)