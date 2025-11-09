"""
API functions for programmatic use of duk functionality.

This module provides Python API functions that mirror the CLI commands,
allowing duk to be used as a library in Python programs.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Union

import pandas as pd
from dateutil.parser import parse as parse_date

from duk.commands.ph import (
    PriceHistoryDownloader,
    process_price_data,
)

logger = logging.getLogger(__name__)


def ph(
    tickers: Union[str, List[str]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    num_records: Optional[int] = None,
    fields: Optional[List[str]] = None,
    frequency: str = "daily",
    include_dividends: bool = False,
    include_splits: bool = False,
    calculate_adjusted: bool = False,
    use_cache: bool = True,
) -> pd.DataFrame:
    """
    Download historical security price data programmatically.

    This function provides the same functionality as the `duk ph` command,
    but returns data as a pandas DataFrame for use in Python programs.

    Args:
        tickers: Single ticker symbol (str) or list of ticker symbols
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        num_records: Number of records to return (default: 5 if no dates specified)
        fields: List of fields to include (e.g., ['open', 'high', 'low', 'close'])
                If None, defaults to ['close']
        frequency: Data frequency - 'daily', 'weekly', 'monthly', 'quarterly',
                  'semiannual', or 'annual' (default: 'daily')
        include_dividends: Include dividend data (default: False)
        include_splits: Include split data (default: False)
        calculate_adjusted: Calculate adjusted close prices (default: False)
        use_cache: Use cached data if available (default: True)

    Returns:
        DataFrame containing the requested price data with columns:
        - symbol: Stock symbol
        - date: Date of the record
        - Additional columns based on 'fields' parameter

    Raises:
        ValueError: If invalid parameters are provided
        RuntimeError: If data download fails

    Examples:
        >>> import duk
        >>> # Get latest 5 days of close prices for AAPL
        >>> df = duk.ph('AAPL')
        >>> # Get OHLC data for multiple tickers
        >>> df = duk.ph(['AAPL', 'MSFT'], fields=['open', 'high', 'low', 'close'])
        >>> # Get data for a specific date range
        >>> df = duk.ph('AAPL', start_date='2023-01-01', end_date='2023-12-31')
        >>> # Get weekly data with dividends
        >>> df = duk.ph('AAPL', frequency='weekly', include_dividends=True)
    """
    # Normalize tickers to list
    if isinstance(tickers, str):
        ticker_list = [tickers]
    else:
        ticker_list = list(tickers)

    if not ticker_list:
        raise ValueError("At least one ticker must be provided")

    # Validate tickers
    for ticker in ticker_list:
        if not ticker or not ticker.strip():
            raise ValueError("Empty ticker symbol provided")

    # Normalize ticker symbols to uppercase
    ticker_list = [t.strip().upper() for t in ticker_list]

    # Handle default value for num_records
    num_records_was_explicitly_set = num_records is not None
    if num_records is None:
        num_records = 5

    logger.debug(f"Number of records requested: {num_records}")

    # Validate date arguments
    if start_date and end_date and num_records_was_explicitly_set:
        raise ValueError("Cannot specify num_records with both start_date and end_date")

    # Handle date parameter calculations
    if num_records and not start_date and not end_date:
        # Get last N days from today
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date_obj = datetime.now() - timedelta(days=num_records - 1)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        logger.debug(f"Calculated date range: {start_date} to {end_date}")
    elif num_records and start_date and not end_date:
        # Get N days from start date
        start_date_obj = parse_date(start_date)
        end_date_obj = start_date_obj + timedelta(days=num_records - 1)
        end_date = end_date_obj.strftime("%Y-%m-%d")
        logger.debug(f"Calculated end date: {end_date}")
    elif num_records and end_date and not start_date:
        # Get N days before end date
        end_date_obj = parse_date(end_date)
        start_date_obj = end_date_obj - timedelta(days=num_records - 1)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        logger.debug(f"Calculated start date: {start_date}")

    # Validate frequency
    valid_frequencies = [
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "semiannual",
        "annual",
    ]
    if frequency not in valid_frequencies:
        raise ValueError(
            f"Invalid frequency '{frequency}'. Must be one of: {valid_frequencies}"
        )

    # Set default fields if none specified
    if fields is None:
        fields = ["close"]
    else:
        # Validate fields
        valid_fields = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "adjusted_close",
            "dividend",
            "split",
        ]
        for field in fields:
            if field not in valid_fields:
                raise ValueError(
                    f"Invalid field '{field}'. Must be one of: {valid_fields}"
                )

    # Add dividend and split fields if requested
    if include_dividends and "dividend" not in fields:
        fields.append("dividend")
    if include_splits and "split" not in fields:
        fields.append("split")
    if calculate_adjusted and "adjusted_close" not in fields:
        fields.append("adjusted_close")

    logger.info(f"Processing {len(ticker_list)} ticker(s): {ticker_list}")
    logger.info(f"Fields to include: {fields}")

    # Create downloader
    downloader = PriceHistoryDownloader(use_cache=use_cache)

    # Process each ticker
    all_data = []

    for symbol in ticker_list:
        logger.info(f"Processing ticker: {symbol}")

        # Download price data
        price_data = downloader.download_price_data(
            symbol, start_date, end_date, num_records
        )
        if price_data is None:
            logger.error(f"Failed to download price data for {symbol}")
            raise RuntimeError(f"Failed to download price data for {symbol}")

        if not price_data:
            logger.warning(f"No price data found for {symbol}")
            continue

        # If num_records was explicitly specified, ensure we return exactly that many
        if num_records_was_explicitly_set and price_data:
            price_data_sorted = sorted(
                price_data, key=lambda x: x.get("date", ""), reverse=True
            )
            if len(price_data_sorted) > num_records:
                price_data = price_data_sorted[:num_records]
                logger.debug(f"Limited to {num_records} records for {symbol}")
            else:
                price_data = price_data_sorted

        # Download dividend data if needed
        dividends_data = None
        if include_dividends or calculate_adjusted:
            logger.debug(f"Downloading dividend data for {symbol}")
            dividends_data = downloader.download_dividends_data(
                symbol, start_date, end_date
            )

        # Download split data if needed
        splits_data = None
        if include_splits or calculate_adjusted:
            logger.debug(f"Downloading split data for {symbol}")
            splits_data = downloader.download_splits_data(symbol, start_date, end_date)

        # Process the data
        df = process_price_data(
            symbol=symbol,
            price_data=price_data,
            dividends_data=dividends_data,
            splits_data=splits_data,
            fields=fields,
            frequency=frequency,
            calculate_adjusted=calculate_adjusted,
        )

        if not df.empty:
            logger.info(f"Processed {len(df)} records for {symbol}")
            all_data.append(df)

    if not all_data:
        logger.error("No data found for any of the requested symbols")
        raise RuntimeError("No data found for any of the requested symbols")

    # Combine all data into one DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df.sort_values(["symbol", "date"])
    logger.info(f"Combined data: {len(combined_df)} total records")

    return combined_df
