"""
duk - A CLI tool and library for downloading financial market data
"""

__version__ = "0.1.0"

from duk.api.ph import get_price_history

__all__ = ["get_price_history"]
