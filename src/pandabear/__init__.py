__version__ = "0.2.1"


# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())

from .decorators import check_types
from .model import DataFrameModel, SeriesModel
from .model_components import Field
from .typing import DataFrame, Series
