"""
Rate utilities for processing treasury rate data.

This module provides functions for converting and processing treasury rate
data retrieved from APIs.
"""

import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def treasury_rates2df(par_yields: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert treasury rates API output to a pandas DataFrame.

    Converts the output of treasury_rates_api into a pandas DataFrame
    with the date field converted to a date object and set as the index.

    Args:
        par_yields: List of dictionaries containing treasury rates data,
            as returned by treasury_rates_api. Each dictionary should
            contain a 'date' field and various rate maturity fields.

    Returns:
        pandas DataFrame with the date as the index and rate maturities
        as columns. The DataFrame is sorted by date in ascending order.

    Example:
        >>> from duk.fmp_api import treasury_rates_api
        >>> par_yields = treasury_rates_api("your_api_key")
        >>> df = treasury_rates2df(par_yields)
        >>> print(df.head())
    """
    if not par_yields:
        logger.warning("Empty par_yields input, returning empty DataFrame")
        return pd.DataFrame()

    logger.debug(f"Converting {len(par_yields)} treasury rate records to DataFrame")

    # Create DataFrame from list of dictionaries
    df = pd.DataFrame(par_yields)

    # Convert date column to datetime and set as index
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df.set_index("date")
        df = df.sort_index()
        logger.info(f"Created DataFrame with {len(df)} records")
    else:
        logger.warning("No 'date' column found in par_yields data")

    return df
