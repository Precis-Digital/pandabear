import re
from typing import Any

import pandas as pd


class MissingColumnsError(Exception):
    def __init__(self, message):
        # strip trailing "." and " " from message
        message = re.sub(r"[. ]+$", "", message)
        suggestion = ". Is there a typo in the schema definition? If not, the dataframe is missing columns."
        super().__init__(message + suggestion)


class MissingIndexError(Exception):
    def __init__(self, message):
        # strip trailing "." and " " from message
        message = re.sub(r"[. ]+$", "", message)
        suggestion = ". Is there a typo in the schema definition? If not, the dataframe is missing index levels."
        super().__init__(message + suggestion)


class SchemaDefinitionError(Exception):
    def __init__(self, message):
        super().__init__(message)


class SchemaValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class CoersionError(Exception):
    def __init__(self, message):
        super().__init__(message)


MAX_FAILURE_ROWS = 10


class ColumnCheckError(Exception):
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
