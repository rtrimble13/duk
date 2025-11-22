"""
Price History (ph) module for downloading security price history from FMP
"""

import logging
from typing import Optional

import pandas as pd
import requests

logger = logging.getLogger("duk.api.ph")


def get_price_history(
    symbol: str,
    api_key: str,
    limit: int = 5,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Download price history for a security symbol from FMP API

    Args:
        symbol: Security symbol (e.g., 'IBM', 'AAPL')
        api_key: FMP API key
        limit: Number of data points to return (default: 5)
        from_date: Start date in YYYY-MM-DD format (optional)
        to_date: End date in YYYY-MM-DD format (optional)

    Returns:
        DataFrame with price history data, sorted by date ascending

    Raises:
        ValueError: If symbol or api_key is empty
        requests.RequestException: If API request fails
    """
    logger.info(f"Fetching price history for symbol: {symbol}")

    # Validate inputs
    if not symbol or not symbol.strip():
        logger.error("Symbol cannot be empty")
        raise ValueError("Symbol cannot be empty")

    if not api_key or not api_key.strip():
        logger.error("API key cannot be empty")
        raise ValueError("API key cannot be empty")

    # Convert symbol to uppercase for API call
    symbol = symbol.strip().upper()
    logger.debug(f"Normalized symbol: {symbol}")

    # Build API URL
    base_url = "https://financialmodelingprep.com/api/v3/historical-price-full"
    url = f"{base_url}/{symbol}"

    # Build query parameters
    params = {"apikey": api_key}

    if from_date:
        params["from"] = from_date
        logger.debug(f"Using from_date: {from_date}")

    if to_date:
        params["to"] = to_date
        logger.debug(f"Using to_date: {to_date}")

    # Make API request
    logger.info(f"Making API request to FMP for {symbol}")
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        logger.info(f"API request successful for {symbol}")
    except requests.RequestException as e:
        logger.error(f"API request failed for {symbol}: {e}")
        raise

    # Parse response
    data = response.json()

    if "historical" not in data:
        logger.error(f"No historical data found for {symbol}")
        raise ValueError(f"No historical data found for symbol: {symbol}")

    historical_data = data["historical"]

    if not historical_data:
        logger.warning(f"Empty historical data for {symbol}")
        return pd.DataFrame()

    # Convert to DataFrame
    logger.debug(f"Converting {len(historical_data)} records to DataFrame")
    df = pd.DataFrame(historical_data)

    # Sort by date ascending
    df = df.sort_values("date", ascending=True)

    # Apply limit
    if limit and limit > 0:
        df = df.tail(limit)
        logger.debug(f"Applied limit of {limit} records")

    logger.info(f"Successfully retrieved {len(df)} records for {symbol}")
    return df
