"""
duk - TurningBull Data Utility Knife

A CLI tool for downloading financial market data and performing data
preprocessing.

Can also be used as a Python module:
    import duk
    df = duk.ph('AAPL')  # Get price history for Apple stock
"""

__version__ = "0.1.0"

# Import API functions for programmatic use
from duk.api import ph

__all__ = ["ph", "__version__"]
