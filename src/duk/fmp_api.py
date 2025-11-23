"""
FMP (Financial Modeling Prep) API integration.

This module provides functions for interacting with the FMP API
to retrieve financial and market data.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from duk.date_utils import get_api_date_range

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
    base_url = "https://financialmodelingprep.com/stable"
    endpoint = f"{base_url}/historical-price-eod/full?symbol={symbol}"

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


def adjusted_price_history_api(
    symbol: str,
    api_key: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Request dividend-adjusted security price history from FMP API.

    Retrieves end-of-day (EOD) dividend-adjusted historical price data for a
    given security symbol from the Financial Modeling Prep API.

    Args:
        symbol: The ticker symbol for the security (e.g., "AAPL", "MSFT")
        api_key: FMP API key for authentication
        from_date: Optional start date for historical data (format: YYYY-MM-DD)
        to_date: Optional end date for historical data (format: YYYY-MM-DD)

    Returns:
        List of dictionaries containing dividend-adjusted historical price data.
        Each dictionary contains fields like date, open, high, low, close, volume, etc.

    Raises:
        FMPAPIError: If the API request fails or returns an error
        ValueError: If required parameters are invalid

    Example:
        >>> history = adjusted_price_history_api("AAPL", "your_api_key")
        >>> history = adjusted_price_history_api("AAPL", "your_api_key",
        ...                                      from_date="2023-01-01",
        ...                                      to_date="2023-12-31")
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    if not api_key:
        raise ValueError("API key cannot be empty")

    # Construct the base URL
    base_url = "https://financialmodelingprep.com/stable"
    endpoint = f"{base_url}/historical-price-eod/dividend-adjusted?symbol={symbol}"

    # Build query parameters
    params = {"apikey": api_key}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    logger.debug(
        f"Requesting dividend-adjusted price history for {symbol} from FMP API"
    )

    try:
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Failed to fetch dividend-adjusted price history for {symbol}: {e}"
        )
        raise FMPAPIError(
            f"Failed to fetch dividend-adjusted price history for {symbol}: {e}"
        ) from e

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
        logger.info(
            f"Retrieved {len(historical_data)} dividend-adjusted records for {symbol}"
        )
        return historical_data
    elif isinstance(data, list):
        # Some endpoints return a list directly
        logger.info(f"Retrieved {len(data)} dividend-adjusted records for {symbol}")
        return data
    else:
        logger.warning(f"Unexpected response format for {symbol}")
        return []


def get_price_history(
    api_key: str,
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frequency: str = "day",
    limit: Optional[int] = None,
    fields: Optional[List[str]] = None,
    adjusted: bool = False,
) -> pd.DataFrame:
    """
    Get historical price data as a pandas DataFrame.

    This function combines the api_date_range and price_history_api functions
    to retrieve and process historical price data for a security. It supports
    date range calculation, data resampling, and limiting the number of records.

    Args:
        api_key: FMP API key for authentication
        symbol: The ticker symbol for the security (e.g., "AAPL", "MSFT")
        start_date: Optional start date string (format: YYYY-MM-DD)
        end_date: Optional end date string (format: YYYY-MM-DD)
        frequency: Frequency of data points. Valid values are:
            'day' (daily), 'week' (weekly), 'month' (monthly),
            'quarter' (quarterly), 'semi-annual' (semi-annually),
            'annual' (annually). Default is 'day'.
        limit: Optional number of records to return. When combined with:
            - start_date (no end_date): returns first `limit` records
            - end_date (no start_date): returns last `limit` records
        fields: Optional list of columns to return. Valid fields are:
            'open', 'high', 'low', 'close', 'volume'. Default is all fields.
        adjusted: If True, retrieve dividend-adjusted price history. Default is False.

    Returns:
        pandas DataFrame with historical price data, indexed on Date (ascending).
        Columns include the specified fields (or all fields if not specified).

    Raises:
        ValueError: If parameters are invalid or if invalid fields are specified
        FMPAPIError: If the API request fails

    Examples:
        >>> # Get all available daily data for AAPL
        >>> df = get_price_history("your_api_key", "AAPL")

        >>> # Get daily data for a specific date range
        >>> df = get_price_history("your_api_key", "AAPL",
        ...                        start_date="2023-01-01",
        ...                        end_date="2023-12-31")

        >>> # Get first 10 daily records starting from a date
        >>> df = get_price_history("your_api_key", "AAPL",
        ...                        start_date="2023-01-01", limit=10)

        >>> # Get last 10 daily records before a date
        >>> df = get_price_history("your_api_key", "AAPL",
        ...                        end_date="2023-12-31", limit=10)

        >>> # Get weekly data for the last 30 weeks
        >>> df = get_price_history("your_api_key", "AAPL",
        ...                        frequency="week", limit=30)

        >>> # Get monthly data for a date range
        >>> df = get_price_history("your_api_key", "AAPL",
        ...                        start_date="2023-01-01",
        ...                        end_date="2023-12-31",
        ...                        frequency="month")

        >>> # Get only close prices
        >>> df = get_price_history("your_api_key", "AAPL",
        ...                        start_date="2023-01-01",
        ...                        end_date="2023-12-31",
        ...                        fields=["close"])

        >>> # Get OHLC data without volume
        >>> df = get_price_history("your_api_key", "AAPL",
        ...                        start_date="2023-01-01",
        ...                        end_date="2023-12-31",
        ...                        fields=["open", "high", "low", "close"])
    """
    # Validate fields parameter
    valid_fields = ["open", "high", "low", "close", "volume"]
    if fields is not None:
        fields = [f for f in fields if f in valid_fields]
    else:
        fields = valid_fields  # Default to all fields

    # Convert string dates to date objects
    start_date_obj = None
    end_date_obj = None
    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Calculate date range using api_date_range
    calculated_start, calculated_end = get_api_date_range(
        start_date=start_date_obj,
        end_date=end_date_obj,
        limit=limit,
        frequency=frequency,
    )

    # Convert dates back to strings for the API call
    from_date = calculated_start.strftime("%Y-%m-%d") if calculated_start else None
    to_date = calculated_end.strftime("%Y-%m-%d") if calculated_end else None

    logger.info(f"Fetching price history for {symbol} from {from_date} to {to_date}")

    # Fetch data from API - use adjusted or regular price history
    if adjusted:
        data = adjusted_price_history_api(
            symbol=symbol,
            api_key=api_key,
            from_date=from_date,
            to_date=to_date,
        )
    else:
        data = price_history_api(
            symbol=symbol,
            api_key=api_key,
            from_date=from_date,
            to_date=to_date,
        )

    # Convert to DataFrame
    if not data:
        logger.warning(f"No data returned for {symbol}")
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # Convert df columns to lower case for consistency
    df.columns = [col.lower() for col in df.columns]

    # Strip "adj" prefix from column names if adjusted data is used
    if adjusted:
        df.columns = [col.removeprefix("adj").strip() for col in df.columns]

    # Keep only the relevant columns
    expected_columns = ["date"] + fields
    df = df.loc[:, [col for col in expected_columns if col in df.columns]]

    # Ensure date column exists and convert to datetime
    if "date" not in df.columns:
        logger.error("No 'date' column in response data")
        raise ValueError("Response data missing 'date' column")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")  # Sort ascending by date

    # Set date as index
    df = df.set_index("date")

    # Resample if frequency is not 'day'
    if frequency != "day":
        logger.info(f"Resampling data to {frequency} frequency")
        # Map frequency to pandas resample offset
        freq_map = {
            "week": "W",
            "month": "ME",
            "quarter": "QE",
            "semi-annual": "6ME",
            "annual": "YE",
        }

        if frequency in freq_map:
            # Resample: use last value for each period (typical for OHLC data)
            # For open: use first, for high: use max, for low: use min,
            # for close/volume: use last
            agg_dict = {}
            if "open" in df.columns:
                agg_dict["open"] = "first"
            if "high" in df.columns:
                agg_dict["high"] = "max"
            if "low" in df.columns:
                agg_dict["low"] = "min"
            if "close" in df.columns:
                agg_dict["close"] = "last"
            if "volume" in df.columns:
                agg_dict["volume"] = "sum"

            # Add any other columns with 'last' aggregation
            for col in df.columns:
                if col not in agg_dict:
                    agg_dict[col] = "last"

            df = df.resample(freq_map[frequency]).agg(agg_dict).dropna()
            logger.debug(
                f"Resampled to {frequency} frequency, {len(df)} records remaining"
            )

    # Apply limit if specified (after resampling)
    if limit is not None and limit > 0:
        # Case: limit with start_date and no end_date - keep first `limit` records
        if start_date_obj is not None and end_date_obj is None:
            df = df.head(limit)
            logger.debug(f"Keeping first {limit} records")
        # Case: limit with end_date and no start_date - keep last `limit` records
        else:
            df = df.tail(limit)
            logger.debug(f"Keeping last {limit} records")

    logger.info(f"Returning {len(df)} records for {symbol}")
    return df
