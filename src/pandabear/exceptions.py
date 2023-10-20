import re


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


class TypeHintError(Exception):
    def __init__(self, message):
        super().__init__(message)
