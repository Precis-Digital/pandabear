import inspect
from functools import wraps
from types import UnionType
from typing import Any, Callable, get_args

import pandas as pd

from .model import BaseModel
from .typing_ import DataFrame


def validate_variable_against_type_hint(var: Any, type_hint: Any):
    suggestion = "Check that your type hints and returned values match."
    # type hint like: `pd.DataFrame | MySchema`
    if (
        isinstance(type_hint, UnionType)
        and len(get_args(type_hint)) == 2
        and issubclass(get_args(type_hint)[1], BaseModel)
    ):
        if not type(var) in [pd.DataFrame, pd.Series]:
            raise TypeError(f"Expected a pandas dataframe or series, but found {type(var)}. {suggestion}")
        schema = get_args(type_hint)[1]
        schema.validate(var)

    # type hint like: `tuple[int, pd.DataFrame | MySchema]` (or deeper nesting)
    elif (len(return_types := get_args(type_hint))) > 1:
        if type(var) not in [list, tuple]:
            raise TypeError(f"Expected an array-like, but found {type(var)}. {suggestion}")
        elif len(var) != len(return_types):
            raise TypeError(f"Expected {len(return_types)} values, but found {len(var)}. {suggestion}")
        for var_i, type_hint_i in zip(var, return_types):
            validate_variable_against_type_hint(var_i, type_hint_i)


def check_types(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Validate input argument(s)
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for name, variable in bound_args.arguments.items():
            type_hint = sig.parameters[name].annotation
            validate_variable_against_type_hint(variable, type_hint)

        # Execute the function
        result = func(*args, **kwargs)

        # Validate return value(s)
        validate_variable_against_type_hint(result, sig.return_annotation)

        return result

    return wrapper
