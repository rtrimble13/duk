"""
Price History module for duk.

This module provides functionality to download security price history from
Financial Modeling Prep (FMP) API.
"""

from typing import Optional

import pandas as pd
import requests

from duk.logging_config import get_logger

logger = get_logger("ph")


def get_price_history(
    symbol: str,
    api_key: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frequency: str = "daily",
    limit: int = 5,
    fields: Optional[list] = None,
) -> pd.DataFrame:
    """
    Get price history for a security from Financial Modeling Prep API.

    Args:
        symbol: Security symbol (case-insensitive, e.g., 'ibm' or 'IBM')
        api_key: FMP API key
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        frequency: Data frequency ('daily', 'weekly', 'monthly', 'quarterly',
                   'semi-annual', 'annual'). Default: 'daily'
        limit: Number of data points to return. Default: 5
        fields: List of fields to return. If None, returns default fields.

    Returns:
        DataFrame containing price history data ordered by ascending date

    Raises:
        ValueError: If API key is missing or invalid parameters
        requests.RequestException: If API request fails
    """
    logger.info(f"Fetching price history for symbol: {symbol}")

    # Validate API key
    if not api_key:
        logger.error("FMP API key is required")
        raise ValueError("FMP API key is required. Set it in ~/.dukrc")

    # Normalize symbol to uppercase for API call
    symbol_upper = symbol.upper()
    logger.debug(f"Normalized symbol: {symbol_upper}")

    # Validate frequency
    valid_frequencies = [
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "semi-annual",
        "annual",
    ]
    if frequency not in valid_frequencies:
        logger.error(f"Invalid frequency: {frequency}")
        raise ValueError(
            f"Invalid frequency: {frequency}. " f"Must be one of {valid_frequencies}"
        )

    # Build API URL based on frequency
    base_url = "https://financialmodelingprep.com/api/v3"
    if frequency == "daily":
        endpoint = f"historical-price-full/{symbol_upper}"
    else:
        # All non-daily frequencies use line series
        endpoint = f"historical-price-full/{symbol_upper}?serietype=line"

    # Build URL with parameters
    url = f"{base_url}/{endpoint}"
    params = {"apikey": api_key}

    # Add date range if specified
    if start_date:
        params["from"] = start_date
        logger.debug(f"Start date: {start_date}")
    if end_date:
        params["to"] = end_date
        logger.debug(f"End date: {end_date}")

    logger.info(f"Making API request to FMP for {symbol_upper}")
    logger.debug(f"API URL: {url}")

    try:
        # Make API request
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        logger.debug(f"API response received with status code: {response.status_code}")

        # Check for API errors
        if "Error Message" in data:
            error_msg = data["Error Message"]
            logger.error(f"API error: {error_msg}")
            raise ValueError(f"API error: {error_msg}")

        # Extract historical data
        if "historical" not in data:
            logger.error("No historical data found in API response")
            raise ValueError(f"No historical data found for symbol: {symbol_upper}")

        historical_data = data["historical"]
        logger.info(f"Retrieved {len(historical_data)} historical data points")

        # Convert to DataFrame
        df = pd.DataFrame(historical_data)

        if df.empty:
            logger.warning(f"No data available for {symbol_upper}")
            return df

        # Convert date column to datetime
        df["date"] = pd.to_datetime(df["date"])

        # Sort by date in ascending order
        df = df.sort_values("date", ascending=True)
        logger.debug("Data sorted by date (ascending)")

        # Apply limit - take the most recent N data points (last N rows in
        # ascending date order)
        if limit > 0:
            df = df.tail(limit)
            logger.debug(f"Limited to {limit} most recent data points")

        # Select fields if specified
        if fields:
            # Ensure 'date' is always included
            if "date" not in fields:
                fields = ["date"] + fields

            # Filter to only available columns
            available_fields = [f for f in fields if f in df.columns]
            if available_fields != fields:
                missing = set(fields) - set(available_fields)
                logger.warning(f"Fields not available: {missing}")

            df = df[available_fields]
            logger.debug(f"Selected fields: {available_fields}")
        else:
            # Default fields
            default_fields = ["date", "open", "high", "low", "close", "volume"]
            available_fields = [f for f in default_fields if f in df.columns]
            df = df[available_fields]
            logger.debug(f"Using default fields: {available_fields}")

        # Reset index
        df = df.reset_index(drop=True)

        logger.info(f"Successfully processed {len(df)} data points for {symbol_upper}")
        return df

    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def format_output(df: pd.DataFrame, output_format: str = "csv") -> str:
    """
    Format DataFrame for output.

    Args:
        df: DataFrame to format
        output_format: Output format ('csv' or 'json')

    Returns:
        Formatted string representation of the data
    """
    if output_format == "json":
        return df.to_json(orient="records", date_format="iso", indent=2)
    else:
        return df.to_csv(index=False)
