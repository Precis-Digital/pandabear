import inspect
from functools import wraps
from typing import Any, Callable, get_args

import pandas as pd

from .model import DataFrameModel
from .typing import DataFrame


def check_types(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for name, value in bound_args.arguments.items():
            if isinstance(value, pd.DataFrame):
                type_hint = sig.parameters[name].annotation  # if this is `pd.DataFrame | MySchema`
                type_hint = get_args(type_hint)              # then this: `[pd.DataFrame, MySchema]`
                if (
                    len(type_hint) == 2
                    and issubclass(type_hint[1], DataFrameModel)
                ):
                    type_hint[1].validate(value)

        # Execute the function
        result = func(*args, **kwargs)

        # Validate return value
        if isinstance(result, DataFrame) and result.schema:
            result.schema.validate(result)
        return result

    return wrapper