__version__ = "0.2.4"


# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())

from pandabear.decorators import check, check_types
from pandabear.model import DataFrameModel, SeriesModel
from pandabear.model_components import Field
from pandabear.typing import DataFrame, Series
