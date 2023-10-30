import re
from typing import Any, Type

import pandas as pd

MAX_FAILURE_ROWS = 10


class MissingColumnsError(Exception):
    """Raise when `df` is missing columns defined in `schema`.

    Is not raised if Config defines `strict=False` or `filter=True`.
    """

    def __init__(self, message):
        # strip trailing "." and " " from message
        message = re.sub(r"[. ]+$", "", message)
        suggestion = ". Is there a typo in the schema definition? If not, the dataframe is missing columns."
        super().__init__(message + suggestion)


class MissingIndexError(Exception):
    """Raise when `df` is missing index levels defined in `schema`.

    Is not raised if Config defines `strict=False` or `filter=True`.
    """

    def __init__(self, message):
        # strip trailing "." and " " from message
        message = re.sub(r"[. ]+$", "", message)
        suggestion = ". Is there a typo in the schema definition? If not, the dataframe is missing index levels."
        super().__init__(message + suggestion)


class SchemaDefinitionError(Exception):
    """Raise when `schema` is not a valid schema definition.

    This may happen if e.g. the user has a numerical check on a column with non-numerical values.
    """

    def __init__(self, message):
        super().__init__(message)


class UnsupportedTypeError(Exception):
    """Raise when a field is defined with a unsupported type.

    This may happen when the user defines types that are not supported.
    """

    def __init__(self, message):
        super().__init__(message)


class SchemaValidationError(Exception):
    """Raise when `df` does not match `schema`.

    This is raised if `df` has unexpected columns of column dtypes don't match.
    If Config defines `strict=False` or `filter=True` unexpected columns won't
    raise an error, though.
    """

    def __init__(self, message):
        super().__init__(message)


class CoersionError(Exception):
    """Raise when `df` cannot be coerced to `schema`.

    This is raised if `df` has a column with a dtype that the schema defined
    dtype cannot coerce. For example, if the schema defines a column as `int`
    but the column contains `str` values, coersion will fail.
    """

    def __init__(self, message):
        super().__init__(message)


class TypeHintError(Exception):
    """Raise when the function argument or return value is not of the expected type.

    This could for example happen if the user provides an int to an argument with a
    `DataFrame` or `Series` type hint. Of if the return type hint indicates multiple
    return values, but the function only returns a single value.
    """

    def __init__(self, message):
        super().__init__(message)


class ColumnCheckError(Exception):
    """Raise when a column check fails checks defined in `Field` variable.

    Report the percentage of rows that failed the check, and display the first
    few rows that failed the check.
    """

    def __init__(self, check_name: str, check_value: Any, series: pd.Series, result: pd.Series):
        self.check_name = check_name
        self.check_value = check_value
        self.series = series
        self.result = result
        super().__init__(self._get_message())

    def _get_message(self) -> str:
        fail_series = self.series[~self.result]
        total = len(self.series)
        fails = len(fail_series)
        fail_pc = int(round(100 * fails / total))
        check_name = self.check_name.replace("series_", "")
        text_msg = (
            f"Column '{self.series.name}' failed check {check_name}({self.check_value}): "
            f"{fails} of {total} ({fail_pc} %)"
        )
        fails_msg = fail_series.head(MAX_FAILURE_ROWS).to_string()
        return f"{text_msg}\n{fails_msg}"


class IndexCheckError(Exception):
    """Raise when an index check fails checks defined in `Field` variable.

    Report the percentage of rows that failed the check, and display the first
    few rows that failed the check.
    """

    def __init__(self, check_name: str, check_value: Any, index: Type[pd.Index], result: pd.Series):
        self.check_name = check_name
        self.check_value = check_value
        self.series = index.to_series()
        self.result = result
        super().__init__(self._get_message())

    def _get_message(self) -> str:
        fail_series = self.series[~self.result]
        total = len(self.series)
        fails = len(fail_series)
        fail_pc = int(round(100 * fails / total))
        check_name = self.check_name.replace("series_", "")
        text_msg = (
            f"Column '{self.series.name}' failed check {check_name}({self.check_value}): "
            f"{fails} of {total} ({fail_pc} %)"
        )
        fails_msg = fail_series.head(MAX_FAILURE_ROWS).to_string()
        return f"{text_msg}\n{fails_msg}"
