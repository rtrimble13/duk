"""
duk - A CLI tool and library for downloading markets and financial data.
"""

from duk.date_utils import DateRangeError, get_api_date_range

__version__ = "0.2.0"

__all__ = ["__version__", "get_api_date_range", "DateRangeError"]
