"""
Price history subprogram for downloading historical security price data.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
import pandas as pd
import requests
from dateutil.parser import parse as parse_date


logger = logging.getLogger(__name__)


class PriceHistoryDownloader:
    """Class for downloading historical security price data from FMP."""

    # Financial Modeling Prep API endpoints
    PRICE_HISTORY_URL = (
        "https://financialmodelingprep.com/stable/historical-price-eod/full"
    )
    DIVIDENDS_URL = "https://financialmodelingprep.com/stable/dividends"
    SPLITS_URL = "https://financialmodelingprep.com/stable/splits"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "duk-price-history-downloader/0.1.0"}
        )
        # Load FMP API key from environment variable or etc directory
        self.api_key = os.environ.get("FMP_API_KEY")
        if not self.api_key:
            key_file = Path(__file__).parents[3] / "etc" / ".fmp_api.key"
            try:
                self.api_key = key_file.read_text().strip()
            except Exception as e:
                logger.error(f"Failed to read API key: {e}")
                sys.exit(1)

    def download_price_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Download historical price data for a symbol.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            days: Number of days to download

        Returns:
            List of price records or None if failed
        """
        try:
            params = {"apikey": self.api_key}

            # Handle date parameters
            if days and not start_date and not end_date:
                # Get last N days from today
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date_obj = datetime.now() - timedelta(days=days - 1)
                start_date = start_date_obj.strftime("%Y-%m-%d")
            elif days and start_date and not end_date:
                # Get N days from start date
                start_date_obj = parse_date(start_date)
                end_date_obj = start_date_obj + timedelta(days=days - 1)
                end_date = end_date_obj.strftime("%Y-%m-%d")
            elif days and end_date and not start_date:
                # Get N days before end date
                end_date_obj = parse_date(end_date)
                start_date_obj = end_date_obj - timedelta(days=days - 1)
                start_date = start_date_obj.strftime("%Y-%m-%d")

            # Add date range parameters if specified
            if start_date:
                params["from"] = start_date
            if end_date:
                params["to"] = end_date

            # Add symbol parameter
            params["symbol"] = symbol

            logger.info(
                f"Downloading price data for {symbol} from {start_date} to {end_date}"
            )
            response = self._make_request(self.PRICE_HISTORY_URL, params)

            if response:
                # Handle both old format (with 'historical' key) and direct list format
                if isinstance(response, dict) and "historical" in response:
                    data = response["historical"]
                elif isinstance(response, list):
                    data = response
                else:
                    logger.warning(f"Unexpected response format for symbol {symbol}")
                    return []

                # Filter by date range if specified
                if start_date or end_date:
                    data = self._filter_by_date_range(data, start_date, end_date)

                # Limit to specified number of days if requested
                if days and len(data) > days:
                    data = data[:days]

                logger.info(f"Downloaded {len(data)} price records for {symbol}")
                return data
            else:
                # API request failed
                return None

        except Exception as e:
            logger.error(f"Failed to download price data for {symbol}: {e}")
            return None

    def download_dividends_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Download dividend data for a symbol."""
        try:
            params = {"apikey": self.api_key, "symbol": symbol}

            logger.info(f"Downloading dividend data for {symbol}")
            response = self._make_request(self.DIVIDENDS_URL, params)

            if response:
                data = response if isinstance(response, list) else []
                # Filter by date range if specified
                if start_date or end_date:
                    data = self._filter_by_date_range(data, start_date, end_date)

                logger.info(f"Downloaded {len(data)} dividend records for {symbol}")
                return data
            else:
                logger.warning(f"No dividend data found for symbol {symbol}")
                return []

        except Exception as e:
            logger.error(f"Failed to download dividend data for {symbol}: {e}")
            return None

    def download_splits_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Download stock split data for a symbol."""
        try:
            params = {"apikey": self.api_key, "symbol": symbol}

            logger.info(f"Downloading split data for {symbol}")
            response = self._make_request(self.SPLITS_URL, params)

            if response:
                data = response if isinstance(response, list) else []
                # Filter by date range if specified
                if start_date or end_date:
                    data = self._filter_by_date_range(data, start_date, end_date)

                logger.info(f"Downloaded {len(data)} split records for {symbol}")
                return data
            else:
                logger.warning(f"No split data found for symbol {symbol}")
                return []

        except Exception as e:
            logger.error(f"Failed to download split data for {symbol}: {e}")
            return None

    def _make_request(
        self, url: str, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Make API request to FMP."""
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None

    def _filter_by_date_range(
        self,
        data: List[Dict[str, Any]],
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Filter data by date range."""
        if not data:
            return data

        filtered_data = []
        for record in data:
            record_date = record.get("date")
            if record_date:
                if start_date and record_date < start_date:
                    continue
                if end_date and record_date > end_date:
                    continue
                filtered_data.append(record)

        return filtered_data


def get_tickers_from_input(ticker_input: str) -> List[str]:
    """
    Get list of tickers from either single ticker or file path.

    Args:
        ticker_input: Either a single ticker symbol or path to file containing tickers

    Returns:
        List of ticker symbols
    """
    # Handle empty input first
    if not ticker_input or not ticker_input.strip():
        raise ValueError("Empty ticker symbol provided")

    # Check if input is a file path
    if Path(ticker_input).exists():
        try:
            with open(ticker_input, "r") as f:
                tickers = [line.strip().upper() for line in f if line.strip()]
            if not tickers:
                raise ValueError("File contains no valid ticker symbols")
            return tickers
        except Exception as e:
            raise ValueError(f"Error reading ticker file: {e}")
    else:
        # Assume it's a single ticker symbol
        ticker = ticker_input.strip().upper()
        if not ticker:
            raise ValueError("Empty ticker symbol provided")
        return [ticker]


def process_price_data(
    symbol: str,
    price_data: List[Dict[str, Any]],
    dividends_data: Optional[List[Dict[str, Any]]] = None,
    splits_data: Optional[List[Dict[str, Any]]] = None,
    fields: Optional[List[str]] = None,
    frequency: str = "daily",
    calculate_adjusted: bool = False,
) -> pd.DataFrame:
    """
    Process price data with optional dividend and split adjustments.

    Args:
        symbol: Stock symbol
        price_data: List of price records
        dividends_data: List of dividend records
        splits_data: List of split records
        fields: List of fields to include in output
        frequency: Data frequency (daily, weekly, monthly, quarterly,
                  semiannual, annual)
        calculate_adjusted: Whether to calculate adjusted prices

    Returns:
        Processed DataFrame
    """
    if not price_data:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(price_data)
    df["symbol"] = symbol
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Set default fields if none specified
    if fields is None:
        fields = ["open", "high", "low", "close"]

    # Initialize output columns
    output_cols = ["symbol", "date"] + fields

    # Add dividend column if requested
    if "dividend" in fields or dividends_data:
        df["dividend"] = 0.0
        if dividends_data:
            dividend_df = pd.DataFrame(dividends_data)
            dividend_df["date"] = pd.to_datetime(dividend_df["date"])
            # Merge dividends
            for _, div_row in dividend_df.iterrows():
                mask = df["date"] == div_row["date"]
                df.loc[mask, "dividend"] = div_row.get("dividend", 0.0)

    # Add split column if requested
    if "split" in fields or splits_data:
        df["split"] = 0.0
        if splits_data:
            split_df = pd.DataFrame(splits_data)
            split_df["date"] = pd.to_datetime(split_df["date"])
            # Merge splits
            for _, split_row in split_df.iterrows():
                mask = df["date"] == split_row["date"]
                # FMP uses numerator/denominator format
                numerator = split_row.get("numerator", 1)
                denominator = split_row.get("denominator", 1)
                if denominator != 0:
                    df.loc[mask, "split"] = numerator / denominator

    # Calculate adjusted prices if requested
    if calculate_adjusted or "adjusted_close" in fields:
        df["adjusted_close"] = df["close"].copy()

        # Apply dividend adjustments (subtract dividend from all previous prices)
        if dividends_data:
            dividend_df = pd.DataFrame(dividends_data)
            dividend_df["date"] = pd.to_datetime(dividend_df["date"])
            for _, div_row in dividend_df.iterrows():
                div_date = div_row["date"]
                div_amount = div_row.get("dividend", 0.0)
                mask = df["date"] < div_date
                df.loc[mask, "adjusted_close"] -= div_amount

        # Apply split adjustments (multiply all previous prices by split ratio)
        if splits_data:
            split_df = pd.DataFrame(splits_data)
            split_df["date"] = pd.to_datetime(split_df["date"])
            for _, split_row in split_df.iterrows():
                split_date = split_row["date"]
                numerator = split_row.get("numerator", 1)
                denominator = split_row.get("denominator", 1)
                if denominator != 0:
                    split_ratio = numerator / denominator
                    mask = df["date"] < split_date
                    df.loc[mask, "adjusted_close"] *= split_ratio

    # Apply frequency aggregation if not daily
    if frequency != "daily":
        df = aggregate_by_frequency(df, frequency)

    # Select only requested fields
    available_cols = [col for col in output_cols if col in df.columns]
    df = df[available_cols]

    return df


def aggregate_by_frequency(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    """Aggregate data by specified frequency."""
    if df.empty:
        return df

    # Map frequency to pandas offset
    freq_map = {
        "weekly": "W",
        "monthly": "ME",  # Use 'ME' (Month End) instead of deprecated 'M'
        "quarterly": "Q",
        "semiannual": "6ME",  # Use 'ME' instead of 'M'
        "annual": "A",
    }

    freq = freq_map.get(frequency)
    if not freq:
        return df  # Return unchanged for daily or unknown frequency

    # Set date as index for resampling
    df_resampled = df.set_index("date")

    # Define aggregation rules
    agg_rules = {
        "symbol": "first",
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "dividend": "sum",
        "split": "last",
        "adjusted_close": "last",
    }

    # Only aggregate columns that exist
    agg_rules = {k: v for k, v in agg_rules.items() if k in df_resampled.columns}

    # Resample and aggregate
    df_agg = df_resampled.resample(freq).agg(agg_rules)

    # Reset index to get date back as column
    df_agg = df_agg.reset_index()

    # Remove rows with NaN values (periods with no data)
    df_agg = df_agg.dropna(subset=["close"])

    return df_agg


def save_data(df: pd.DataFrame, filename: str, output_format: str, directory: str):
    """Save DataFrame to file."""
    output_path = Path(directory) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "json":
        # Convert to JSON format suitable for pandas
        data_dict = df.to_dict(orient="records")
        for record in data_dict:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, pd.Timestamp):
                    record[key] = value.strftime("%Y-%m-%d")

        with open(output_path, "w") as f:
            json.dump(data_dict, f, indent=2, default=str)
    else:
        # CSV format
        df.to_csv(output_path, index=False)


@click.command()
@click.argument("ticker")
@click.option(
    "--start-date", "-s", help="Start date for date range (YYYY-MM-DD format)"
)
@click.option("--end-date", "-e", help="End date for date range (YYYY-MM-DD format)")
@click.option(
    "--days",
    "-n",
    type=int,
    default=5,
    help="Number of observations to return (default: 5)",
)
@click.option("--output", "-o", is_flag=True, help="Output to file instead of stdout")
@click.option("--filename", "-f", help="Specify filename (overrides default naming)")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["csv", "json"]),
    default="csv",
    help="Output format (default: csv)",
)
@click.option(
    "--directory", "-D", default="var", help="Output directory (default: var)"
)
@click.option(
    "--frequency",
    type=click.Choice(
        ["daily", "weekly", "monthly", "quarterly", "semiannual", "annual"]
    ),
    default="daily",
    help="Data frequency (default: daily)",
)
@click.option("--ohlc", is_flag=True, help="Include Open, High, Low, Close prices")
@click.option("--hlc", is_flag=True, help="Include High, Low, Close prices")
@click.option("--ohlcv", is_flag=True, help="Include Open, High, Low, Close, Volume")
@click.option("--vol", is_flag=True, help="Include Volume")
@click.option("--adj", is_flag=True, help="Include adjusted close prices")
@click.option("--div", is_flag=True, help="Include dividend data")
@click.option("--split", is_flag=True, help="Include stock split data")
@click.pass_context
def ph_command(
    ctx,
    ticker,
    start_date,
    end_date,
    days,
    output,
    filename,
    output_format,
    directory,
    frequency,
    ohlc,
    hlc,
    ohlcv,
    vol,
    adj,
    div,
    split,
):
    """Download historical security price data.

    TICKER can be either a single ticker symbol or a path to a file containing
    ticker symbols.

    By default, returns the 5 most recent OHLC data points for the
    specified ticker(s).

    Examples:
      duk ph AAPL                           # Latest 5 days OHLC for AAPL
      duk ph AAPL --days 30                 # Last 30 days OHLC for AAPL
      duk ph AAPL --start-date 2023-01-01 --end-date 2023-12-31  # Year 2023 data
      duk ph AAPL --ohlcv --adj             # OHLCV with adjusted prices
      duk ph AAPL --div --split             # Only dividend and split data
      duk ph AAPL --frequency monthly       # Monthly aggregated data
      duk ph tickers.txt --output           # Process multiple tickers from file
    """
    downloader = PriceHistoryDownloader()

    # Validate date arguments
    if start_date and end_date and days:
        if days != 5:  # Only error if user explicitly set days different from default
            click.echo(
                "Error: Cannot specify --days with both --start-date and --end-date",
                err=True,
            )
            sys.exit(1)

    # Get list of tickers
    try:
        tickers = get_tickers_from_input(ticker)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Determine which fields to include
    fields = []
    if ohlc or (not any([hlc, ohlcv, vol, adj, div, split])):
        # Default to OHLC if no other options specified
        fields = ["open", "high", "low", "close"]
    elif hlc:
        fields = ["high", "low", "close"]
    elif ohlcv:
        fields = ["open", "high", "low", "close", "volume"]

    # Add individual field options
    if vol and "volume" not in fields:
        fields.append("volume")
    if adj and "adjusted_close" not in fields:
        fields.append("adjusted_close")
    if div and "dividend" not in fields:
        fields.append("dividend")
    if split and "split" not in fields:
        fields.append("split")

    # If only special fields (adj, div, split) are requested, use only those
    if adj and not any([ohlc, hlc, ohlcv, vol]) and not div and not split:
        fields = ["adjusted_close"]
    elif div and not any([ohlc, hlc, ohlcv, vol, adj]) and not split:
        fields = ["dividend"]
    elif split and not any([ohlc, hlc, ohlcv, vol, adj, div]):
        fields = ["split"]

    # Process each ticker
    all_data = []

    for symbol in tickers:
        # Download price data
        price_data = downloader.download_price_data(symbol, start_date, end_date, days)
        if price_data is None:
            click.echo(f"Error: Failed to download price data for {symbol}", err=True)
            continue

        if not price_data:
            click.echo(f"Warning: No price data found for {symbol}", err=True)
            continue

        # Download dividend data if needed
        dividends_data = None
        if div or adj:
            dividends_data = downloader.download_dividends_data(
                symbol, start_date, end_date
            )

        # Download split data if needed
        splits_data = None
        if split or adj:
            splits_data = downloader.download_splits_data(symbol, start_date, end_date)

        # Process the data
        df = process_price_data(
            symbol=symbol,
            price_data=price_data,
            dividends_data=dividends_data,
            splits_data=splits_data,
            fields=fields,
            frequency=frequency,
            calculate_adjusted=adj,
        )

        if not df.empty:
            all_data.append(df)

    if not all_data:
        click.echo("Error: No data found for any of the requested symbols", err=True)
        sys.exit(1)

    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)

    # Sort by symbol and date
    combined_df = combined_df.sort_values(["symbol", "date"])

    # Output data
    if output or filename:
        # Determine filename
        if not filename:
            if len(tickers) == 1:
                symbol_part = tickers[0]
            else:
                symbol_part = f"{len(tickers)}_symbols"

            date_part = datetime.now().strftime("%Y%m%d")
            filename = f"price_history_{symbol_part}_{date_part}.{output_format}"
        elif not filename.endswith(f".{output_format}"):
            filename = f"{filename}.{output_format}"

        save_data(combined_df, filename, output_format, directory)
        click.echo(f"Data saved to {Path(directory) / filename}")
    else:
        # Output to stdout
        if output_format == "json":
            # Convert to JSON
            data_dict = combined_df.to_dict(orient="records")
            for record in data_dict:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif isinstance(value, pd.Timestamp):
                        record[key] = value.strftime("%Y-%m-%d")
            click.echo(json.dumps(data_dict, indent=2, default=str))
        else:
            # Output CSV to stdout
            click.echo(combined_df.to_csv(index=False))
