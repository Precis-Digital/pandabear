from typing import Iterable


def flatten_list(l: list[Iterable]) -> list:
    """Flatten a list of lists into a single list."""
    return [item for sublist in l for item in sublist]
