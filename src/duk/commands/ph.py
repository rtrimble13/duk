"""
Price history subprogram for downloading historical security price data.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
import pandas as pd
import requests
from dateutil.parser import parse as parse_date

from duk.config import get_api_key
from duk.cache import CacheManager


logger = logging.getLogger(__name__)


class PriceHistoryDownloader:
    """Class for downloading historical security price data from FMP."""

    # Financial Modeling Prep API endpoints
    PRICE_HISTORY_URL = (
        "https://financialmodelingprep.com/stable/historical-price-eod/full"
    )
    DIVIDENDS_URL = "https://financialmodelingprep.com/stable/dividends"
    SPLITS_URL = "https://financialmodelingprep.com/stable/splits"

    def __init__(self, use_cache: bool = True):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "duk-price-history-downloader/0.1.0"}
        )
        # Load FMP API key from configuration system
        self.api_key = get_api_key("fmp_api_key")
        if not self.api_key:
            logger.error("FMP API key not found in configuration")
            logger.error("Configure your API key in one of these locations:")
            logger.error("  - ~/.dukrc")
            logger.error("  - Environment variable: FMP_API_KEY")
            sys.exit(1)

        # Initialize cache manager
        self.use_cache = use_cache
        if self.use_cache:
            try:
                self.cache = CacheManager()
            except Exception as e:
                logger.warning(
                    f"Failed to initialize cache: {e}. Proceeding without cache."
                )
                self.use_cache = False

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
        # Check cache first if enabled
        if self.use_cache:
            cached_data = self.cache.get_price_data(
                symbol, "price", start_date, end_date, days
            )
            if cached_data is not None:
                logger.info(
                    f"Retrieved {len(cached_data)} price records for {symbol} "
                    f"from cache"
                )
                return cached_data

        # If not in cache or cache disabled, fetch from API
        data = self._fetch_price_data_from_api(symbol, start_date, end_date, days)

        # Store in cache if successful and cache is enabled
        if data is not None and self.use_cache:
            self.cache.store_price_data(
                symbol, data, "price", start_date, end_date, days
            )

        return data

    def _fetch_price_data_from_api(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch price data from API (extracted from original download_price_data method).
        """
        try:
            params = {"apikey": self.api_key}

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
        # Check cache first if enabled
        if self.use_cache:
            cached_data = self.cache.get_price_data(
                symbol, "dividend", start_date, end_date
            )
            if cached_data is not None:
                logger.info(
                    f"Retrieved {len(cached_data)} dividend records for {symbol} "
                    f"from cache"
                )
                return cached_data

        # If not in cache or cache disabled, fetch from API
        data = self._fetch_dividends_data_from_api(symbol, start_date, end_date)

        # Store in cache if successful and cache is enabled
        if data is not None and self.use_cache:
            self.cache.store_price_data(symbol, data, "dividend", start_date, end_date)

        return data

    def _fetch_dividends_data_from_api(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch dividend data from API (extracted from original method)."""
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
        # Check cache first if enabled
        if self.use_cache:
            cached_data = self.cache.get_price_data(
                symbol, "split", start_date, end_date
            )
            if cached_data is not None:
                logger.info(
                    f"Retrieved {len(cached_data)} split records for {symbol} "
                    f"from cache"
                )
                return cached_data

        # If not in cache or cache disabled, fetch from API
        data = self._fetch_splits_data_from_api(symbol, start_date, end_date)

        # Store in cache if successful and cache is enabled
        if data is not None and self.use_cache:
            self.cache.store_price_data(symbol, data, "split", start_date, end_date)

        return data

    def _fetch_splits_data_from_api(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch split data from API (extracted from original method)."""
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

    # Map frequency to pandas offset - handle version compatibility
    # Use 'ME' for pandas 2.0+ and 'M' for older versions
    import pandas as pd

    pandas_version = pd.__version__
    major_version = int(pandas_version.split(".")[0])

    if major_version >= 2:
        # pandas 2.0+ uses 'ME' instead of deprecated 'M'
        monthly_freq = "ME"
        semiannual_freq = "6ME"
    else:
        # pandas < 2.0 uses 'M'
        monthly_freq = "M"
        semiannual_freq = "6M"

    freq_map = {
        "weekly": "W",
        "monthly": monthly_freq,
        "quarterly": "Q",
        "semiannual": semiannual_freq,
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
@click.argument("tickers", nargs=-1, required=True)
@click.option(
    "--start-date", "-s", help="Start date for date range (YYYY-MM-DD format)"
)
@click.option("--end-date", "-e", help="End date for date range (YYYY-MM-DD format)")
@click.option(
    "--num-records",
    "-n",
    type=int,
    help="Number of records to return (default: 5)",
)
@click.option("--filename", "-o", help="Specify filename (overrides default naming)")
@click.option("--csv", is_flag=True, help="Write output to CSV file")
@click.option("--json", is_flag=True, help="Write output to JSON file")
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
@click.option("--no-close", is_flag=True, help="Remove close data from output")
@click.option("--vol", is_flag=True, help="Append volume data")
@click.option("--adj", is_flag=True, help="Append adjusted close prices")
@click.option("--div", is_flag=True, help="Append dividend payments")
@click.option("--split", is_flag=True, help="Append split ratio")
@click.option(
    "--combine", is_flag=True, help="Combine data from multiple tickers into one output"
)
@click.option("--verbose", is_flag=True, help="Output logging to stdout")
@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable caching and always fetch fresh data from API",
)
@click.pass_context
def ph_command(
    ctx,
    tickers,
    start_date,
    end_date,
    num_records,
    filename,
    csv,
    json,
    directory,
    frequency,
    ohlc,
    no_close,
    vol,
    adj,
    div,
    split,
    combine,
    verbose,
    no_cache,
):
    """Download historical security price data.

    TICKERS can be one or more ticker symbols separated by spaces.

    By default, returns the 5 most recent close prices for the
    specified ticker(s).

    Examples:
      duk ph AAPL                           # Latest 5 days close for AAPL
      duk ph AAPL -n 30                     # Last 30 days close for AAPL
      duk ph AAPL --start-date 2023-01-01 --end-date 2023-12-31  # Year 2023 data
      duk ph AAPL --ohlc --vol              # OHLC with volume
      duk ph AAPL --ohlc --adj              # OHLC with adjusted close
      duk ph AAPL --div --split             # Only dividend and split data
      duk ph AAPL --frequency monthly       # Monthly aggregated data
      duk ph AAPL MSFT GOOGL                # Multiple tickers (separate outputs)
      duk ph AAPL MSFT --combine            # Multiple tickers (combined output)
      duk ph AAPL --csv                     # Write to CSV file
      duk ph AAPL --json                    # Write to JSON file
    """
    # Setup verbose logging if requested
    if verbose:
        # Add console handler if verbose is requested
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting ph command for tickers: {tickers}")

    downloader = PriceHistoryDownloader(use_cache=not no_cache)

    # Handle default value for num_records if not provided
    num_records_was_explicitly_set = num_records is not None
    if num_records is None:
        num_records = 5

    logger.debug(f"Number of records requested: {num_records}")

    # Validate date arguments
    if start_date and end_date and num_records_was_explicitly_set:
        click.echo(
            "Error: Cannot specify --num-records with both --start-date and --end-date",
            err=True,
        )
        sys.exit(1)

    # Handle date parameter calculations and validation
    # Calculate actual start/end dates based on num_records parameter
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

    # Get list of tickers (now directly from arguments)
    ticker_list = list(tickers)
    logger.info(f"Processing {len(ticker_list)} ticker(s): {ticker_list}")

    # Determine which fields to include
    fields = []

    # Default is close only
    if not any([ohlc, vol, adj, div, split]):
        fields = ["close"]
        logger.debug("Using default field: close")
    else:
        # Build fields list based on flags
        if ohlc:
            fields = ["open", "high", "low", "close"]
            logger.debug("Adding OHLC fields")
        elif not no_close:
            # If no ohlc but other flags, start with close
            fields = ["close"]
            logger.debug("Adding close field")

    # Remove close if --no-close is specified
    if no_close and "close" in fields:
        fields.remove("close")
        logger.debug("Removed close field due to --no-close flag")

    # Add individual field options
    if vol and "volume" not in fields:
        fields.append("volume")
        logger.debug("Added volume field")
    if adj and "adjusted_close" not in fields:
        fields.append("adjusted_close")
        logger.debug("Added adjusted_close field")
    if div and "dividend" not in fields:
        fields.append("dividend")
        logger.debug("Added dividend field")
    if split and "split" not in fields:
        fields.append("split")
        logger.debug("Added split field")

    logger.info(f"Final fields to include: {fields}")

    # Determine output format
    output_to_file = csv or json
    if csv and json:
        click.echo("Error: Cannot specify both --csv and --json", err=True)
        sys.exit(1)

    output_format = None
    if csv:
        output_format = "csv"
        logger.debug("Output format: CSV")
    elif json:
        output_format = "json"
        logger.debug("Output format: JSON")
    else:
        output_format = "csv"  # Default for stdout
        logger.debug("Output format: stdout (CSV)")

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
            click.echo(f"Error: Failed to download price data for {symbol}", err=True)
            continue

        if not price_data:
            logger.warning(f"No price data found for {symbol}")
            click.echo(f"Warning: No price data found for {symbol}", err=True)
            continue

        # If --num-records was explicitly specified, ensure we return exactly
        # that many records
        if num_records_was_explicitly_set and price_data:
            # Sort by date descending (most recent first) for proper limiting
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
        if div or adj:
            logger.debug(f"Downloading dividend data for {symbol}")
            dividends_data = downloader.download_dividends_data(
                symbol, start_date, end_date
            )

        # Download split data if needed
        splits_data = None
        if split or adj:
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
            calculate_adjusted=adj,
        )

        if not df.empty:
            logger.info(f"Processed {len(df)} records for {symbol}")
            all_data.append(df)

    if not all_data:
        logger.error("No data found for any of the requested symbols")
        click.echo("Error: No data found for any of the requested symbols", err=True)
        sys.exit(1)

    # Handle output based on combine flag
    if combine or len(ticker_list) == 1:
        # Combine all data into one output
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values(["symbol", "date"])
        logger.info(f"Combined data: {len(combined_df)} total records")

        # Output data
        if output_to_file:
            # Determine filename
            if not filename:
                if len(ticker_list) == 1:
                    symbol_part = ticker_list[0]
                else:
                    symbol_part = f"{len(ticker_list)}_symbols"

                date_part = datetime.now().strftime("%Y%m%d")
                filename = f"price_history_{symbol_part}_{date_part}.{output_format}"
            elif not filename.endswith(f".{output_format}"):
                filename = f"{filename}.{output_format}"

            save_data(combined_df, filename, output_format, directory)
            logger.info(f"Data saved to {Path(directory) / filename}")
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
    else:
        # Output each ticker separately
        for i, df in enumerate(all_data):
            symbol = ticker_list[i]
            logger.info(f"Outputting data for {symbol}: {len(df)} records")

            if output_to_file:
                # Determine filename for this ticker
                if not filename:
                    date_part = datetime.now().strftime("%Y%m%d")
                    ticker_filename = (
                        f"price_history_{symbol}_{date_part}.{output_format}"
                    )
                else:
                    # Use provided filename with ticker appended
                    base_name = (
                        filename.rsplit(".", 1)[0] if "." in filename else filename
                    )
                    ticker_filename = f"{base_name}_{symbol}.{output_format}"

                save_data(df, ticker_filename, output_format, directory)
                logger.info(f"Data saved to {Path(directory) / ticker_filename}")
                click.echo(f"Data saved to {Path(directory) / ticker_filename}")
            else:
                # Output to stdout with separator for multiple tickers
                if i > 0:
                    click.echo("\n")  # Separator between tickers

                if output_format == "json":
                    # Convert to JSON
                    data_dict = df.to_dict(orient="records")
                    for record in data_dict:
                        for key, value in record.items():
                            if pd.isna(value):
                                record[key] = None
                            elif isinstance(value, pd.Timestamp):
                                record[key] = value.strftime("%Y-%m-%d")
                    click.echo(json.dumps(data_dict, indent=2, default=str))
                else:
                    # Output CSV to stdout
                    click.echo(df.to_csv(index=False))

    logger.info("ph command completed successfully")
