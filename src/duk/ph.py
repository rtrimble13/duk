"""
Price History (ph) module for downloading security price history from FMP.

This module provides functionality to download historical price data for securities
from the Financial Modeling Prep (FMP) API.
"""

import pandas as pd
import requests

from duk.config import get_config
from duk.logger import get_logger

# Initialize logger
logger = get_logger("ph")


def get_price_history(
    symbol,
    api_key=None,
    limit=None,
    from_date=None,
    to_date=None,
    fields=None,
):
    """
    Download security price history from FMP API.

    This function can be used as a library call in other projects or through
    the CLI interface.

    Args:
        symbol: Stock symbol (case-insensitive, e.g., 'IBM' or 'ibm')
        api_key: Optional FMP API key. If None, uses config or environment.
        limit: Number of most recent data points to return. Default from config.
        from_date: Start date for historical data (YYYY-MM-DD format)
        to_date: End date for historical data (YYYY-MM-DD format)
        fields: List of fields to return. If None, returns default fields.

    Returns:
        pandas.DataFrame with price history data

    Raises:
        ValueError: If symbol is invalid or API key is missing
        requests.RequestException: If API request fails
    """
    logger.info(f"Fetching price history for symbol: {symbol}")

    # Validate and normalize symbol
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string")

    symbol = symbol.upper().strip()
    logger.debug(f"Normalized symbol: {symbol}")

    # Get API key
    if api_key is None:
        config = get_config()
        api_key = config.get_fmp_api_key()

    if not api_key:
        error_msg = (
            "FMP API key not found. Set it in ~/.dukrc or "
            "FMP_API_KEY environment variable"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.debug("API key found")

    # Get limit from config if not specified
    if limit is None:
        config = get_config()
        limit = config.get_default_limit()

    logger.debug(f"Limit: {limit}")

    # Build API URL
    base_url = "https://financialmodelingprep.com/api/v3/historical-price-full"
    url = f"{base_url}/{symbol}"

    # Build query parameters
    params = {"apikey": api_key}

    if from_date:
        params["from"] = from_date
        logger.debug(f"From date: {from_date}")

    if to_date:
        params["to"] = to_date
        logger.debug(f"To date: {to_date}")

    logger.info(f"Making API request to FMP for {symbol}")

    # Make API request
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        logger.debug(f"API response status: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise

    # Parse response
    data = response.json()

    if "historical" not in data:
        error_msg = f"No historical data found for symbol: {symbol}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    historical_data = data["historical"]
    logger.info(f"Retrieved {len(historical_data)} historical records")

    # Convert to DataFrame
    df = pd.DataFrame(historical_data)

    if df.empty:
        logger.warning(f"No data available for symbol: {symbol}")
        return df

    # Sort by date ascending
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=True)
    logger.debug("Data sorted by date (ascending)")

    # Select fields if specified
    if fields:
        available_fields = df.columns.tolist()
        # Always include date
        if "date" not in fields:
            fields = ["date"] + list(fields)
        # Filter to available fields
        fields = [f for f in fields if f in available_fields]
        df = df[fields]
        logger.debug(f"Selected fields: {fields}")
    else:
        # Default fields
        default_fields = [
            "date",
            "open",
            "high",
            "low",
            "close",
            "adjClose",
            "volume",
        ]
        available_fields = df.columns.tolist()
        fields = [f for f in default_fields if f in available_fields]
        df = df[fields]
        logger.debug(f"Using default fields: {fields}")

    # Apply limit (most recent)
    if limit and limit > 0:
        df = df.tail(limit)
        logger.debug(f"Limited to {limit} most recent records")

    logger.info(f"Returning {len(df)} records")
    return df
