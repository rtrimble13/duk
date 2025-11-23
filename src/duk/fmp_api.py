"""
FMP (Financial Modeling Prep) API integration.

This module provides functions for interacting with the FMP API
to retrieve financial and market data.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class FMPAPIError(Exception):
    """Exception raised for FMP API errors."""

    pass


def price_history_api(
    symbol: str,
    api_key: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Request security price history from FMP API.

    Retrieves end-of-day (EOD) historical price data for a given security
    symbol from the Financial Modeling Prep API.

    Args:
        symbol: The ticker symbol for the security (e.g., "AAPL", "MSFT")
        api_key: FMP API key for authentication
        from_date: Optional start date for historical data (format: YYYY-MM-DD)
        to_date: Optional end date for historical data (format: YYYY-MM-DD)

    Returns:
        List of dictionaries containing historical price data. Each dictionary
        contains fields like date, open, high, low, close, volume, etc.

    Raises:
        FMPAPIError: If the API request fails or returns an error
        ValueError: If required parameters are invalid

    Example:
        >>> history = price_history_api("AAPL", "your_api_key")
        >>> history = price_history_api("AAPL", "your_api_key",
        ...                            from_date="2023-01-01",
        ...                            to_date="2023-12-31")
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    if not api_key:
        raise ValueError("API key cannot be empty")

    # Construct the base URL
    base_url = "https://financialmodelingprep.com/api/v3"
    endpoint = f"{base_url}/historical-price-full/{symbol}"

    # Build query parameters
    params = {"apikey": api_key}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    logger.debug(f"Requesting price history for {symbol} from FMP API")

    try:
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch price history for {symbol}: {e}")
        raise FMPAPIError(f"Failed to fetch price history for {symbol}: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        raise FMPAPIError(f"Failed to parse JSON response: {e}") from e

    # Check if the response contains an error message
    if isinstance(data, dict) and "Error Message" in data:
        error_msg = data["Error Message"]
        logger.error(f"FMP API error: {error_msg}")
        raise FMPAPIError(f"FMP API error: {error_msg}")

    # Extract historical data from response
    if isinstance(data, dict) and "historical" in data:
        historical_data = data["historical"]
        logger.info(f"Retrieved {len(historical_data)} records for {symbol}")
        return historical_data
    elif isinstance(data, list):
        # Some endpoints return a list directly
        logger.info(f"Retrieved {len(data)} records for {symbol}")
        return data
    else:
        logger.warning(f"Unexpected response format for {symbol}")
        return []
