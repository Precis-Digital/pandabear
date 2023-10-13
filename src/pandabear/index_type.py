class Index:
    @classmethod
    def __class_getitem__(cls, typ):
        """Only for "marking" index columns as part of index.
        """
        return cls | typ


def check_type_is_index(t):
    if hasattr(t, '__args__'):
        if t.__args__[0] is Index:
            return True
    return False


def get_index_dtype(t):
    return t.__args__[1]

