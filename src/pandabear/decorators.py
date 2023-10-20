import inspect
from functools import wraps
from types import NoneType, UnionType
from typing import Any, Callable, get_args

import pandas as pd

from pandabear.model import BaseModel


def _validate_variable_against_type_hint(var: Any, type_hint: Any):
    """Validate a variable against a type hint.

    This function is used by the `check_types` decorator to validate
    input arguments and return values of a function.

    Args:
        var (Any): The variable to validate.
        type_hint (Any): The type hint to validate against.

    Raises:
        TypeError: If the variable does not match the type hint.
    """
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
            _validate_variable_against_type_hint(var_i, type_hint_i)


def check_types(func: Callable[..., Any]) -> Callable[..., Any]:
    """Main decorator for validating schemas of input and return dataframes.

    This decorator is used to validate the dataframe schema of input arguments
    and return values of a function. It will check if those input/return values
    whose type hints are `DataFrameModel` subclasses respect the schema of those
    subclasses.

    Args:
        func (Callable[..., Any]): The function to decorate.

    Returns:
        Callable[..., Any]: The decorated function.

    Raises:
        TypeError: If the input arguments or return values do not match their
            type hints.

    Examples:
        >>> from pandabear import DataFrameModel, Field, check_types
        >>>
        >>> class MySchema(DataFrameModel):
        >>>     column_a: int = Field()
        >>>
        >>> @check_types
        >>> def my_func(df: MySchema) -> MySchema:
        >>>     return df
        >>>
        >>> my_func(pd.DataFrame(dict(column_a=[1, 2, 3])))
        >>> my_func(pd.DataFrame(dict(column_a=["a", "b", "c"])))
        TypeError: Expected a pandas dataframe or series, but found <class 'str'>. Check that your type hints and returned values match.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Validate input argument(s)
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for name, variable in bound_args.arguments.items():
            type_hint = sig.parameters[name].annotation
            _validate_variable_against_type_hint(variable, type_hint)

        # Execute the function
        result = func(*args, **kwargs)

        # Validate return value(s)
        _validate_variable_against_type_hint(result, sig.return_annotation)

        return result

    return wrapper


def check(column_names: str | list[str]) -> Callable:
    """Decorator for defining custom checks on dataframe columns.

    This decorator is used to define custom checks on dataframe columns.
    It requires that that the user specifies the column name(s) to apply
    the check to. These must match the column names defined in the schema.

    Args:
        column_names (str | list[str]): The column name(s), defined in the
            schema, to apply the check to.

    Raises:
        TypeError: If `column_names` is not a `str` or `list[str]`.

    Returns:
        Callable: The decorated function.

    Examples:
        >>> from pandabear import DataFrameModel, Field, check
        >>>
        >>> class MySchema(DataFrameModel):
        >>>     column_a: int = Field()
        >>>     column_b: int = Field()
        >>>
        >>>     @check("column_a")
        >>>     def check_column(column: pd.Series) -> bool:
        >>>         return column.sum() > 0
        >>>
        >>>     # or
        >>>     @check(["column_a", "column_b"])
        >>>     def check_columns(column: pd.Series) -> bool:
        >>>         return column.sum() > 0
    """
    if not isinstance(column_names, (str, list)):
        raise TypeError(f"Expected `str` or `list[str]`, but found {type(column_names)}")

    column_names = [column_names] if type(column_names) == str else column_names

    def decorator(method: Callable) -> Callable:
        # Annotate method with check information. This allows the `validate`
        # method to find check functions and apply them to the correct columns.
        method.__setattr__("__check__", column_names)
        return method

    return decorator


def dataframe_check(method: Callable) -> Callable:
    """Decorator for defining custom checks on dataframes.

    This decorator is used to define custom checks on dataframes.

    Args:
        method (Callable): The method to decorate.

    Returns:
        Callable: The decorated function.

    Examples:
        >>> from pandabear import DataFrameModel, Field, dataframe_check
        >>>
        >>> class MySchema(DataFrameModel):
        >>>     column_a: int = Field()
        >>>     column_b: int = Field()
        >>>
        >>>     @dataframe_check
        >>>     def check_dataframe(df: pd.DataFrame) -> bool:
        >>>         return df.sum().sum() > 0
    """

    def wrapper(df: pd.DataFrame) -> bool:
        return method(df)

    # Annotate method with check information. This allows the `validate`
    # method to find check functions and apply them to the correct columns.
    wrapper.__check__ = None

    return wrapper
