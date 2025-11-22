"""
duk - CLI tool for downloading market and financial data through various APIs.

This package provides both a Python library API and a command-line interface
for downloading and preprocessing financial market data.
"""

__version__ = "0.1.0"
__author__ = "Ryan Trimble"
__email__ = "rtrimble13@gmail.com"

from duk.ph import get_price_history

__all__ = ["get_price_history"]
