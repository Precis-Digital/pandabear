import inspect
from functools import wraps
from types import UnionType
from typing import Any, Callable, get_args

import pandas as pd

from .model import BaseModel
from .typing import DataFrame


def validate_return_value(result, return_annotation):
    if (
        isinstance(return_annotation, UnionType)
        and len(get_args(return_annotation)) == 2
        and issubclass(get_args(return_annotation)[1], BaseModel)
    ):
        schema = get_args(return_annotation)[1]
        schema.validate(result)
    elif len(get_args(return_annotation)) > 1:
        for result_i, type_hint in zip(result, get_args(return_annotation)):
            validate_return_value(result_i, type_hint)
    elif isinstance(return_annotation, tuple):
        for result_i, type_hint in zip(result, return_annotation):
            validate_return_value(result_i, type_hint)


def check_types(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Validate input argument(s)
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for name, value in bound_args.arguments.items():
            if isinstance(value, pd.DataFrame) or isinstance(value, pd.Series):
                type_hint = sig.parameters[name].annotation  # if this is e.g. `pd.DataFrame | MySchema`
                type_hint = get_args(type_hint)  # then this is:  `[pd.DataFrame, MySchema]`
                if len(type_hint) == 2 and issubclass(type_hint[1], BaseModel):
                    type_hint[1].validate(value)

        # Execute the function
        result = func(*args, **kwargs)

        # Validate return value(s)
        validate_return_value(result, sig.return_annotation)

        return result

    return wrapper
