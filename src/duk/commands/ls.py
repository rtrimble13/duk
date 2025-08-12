"""
List subprogram for downloading financial lists and information.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
import pandas as pd
import requests

from duk.config import get_api_key
from duk.cache import CacheManager


logger = logging.getLogger(__name__)


class FinancialListDownloader:
    """Class for downloading financial lists from Financial Modeling Prep API."""

    # Financial Modeling Prep API endpoints
    BASE_URL = "https://financialmodelingprep.com/stable"

    def __init__(self, use_cache: bool = True):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "duk-list-downloader/0.1.0"})
        # Load FMP API key from configuration system
        self.api_key = get_api_key("fmp_api_key")
        if not self.api_key:
            logger.error("FMP API key not found in configuration")
            logger.error("Configure your API key in one of these locations:")
            logger.error("  - /usr/local/etc/tb.rc")
            logger.error("  - ~/.tbrc")
            logger.error("  - duk/etc/tb.rc")
            logger.error("  - Environment variable: FMP_API_KEY")
            sys.exit(1)

        # Initialize cache manager
        self.use_cache = use_cache
        if self.use_cache:
            try:
                self.cache = CacheManager()
            except Exception as e:
                logger.warning(f"Failed to initialize cache: {e}")
                self.use_cache = False

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Make API request to Financial Modeling Prep."""
        try:
            if params is None:
                params = {}
            params["apikey"] = self.api_key

            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Handle both list and dict responses
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "data" in result:
                return result["data"]
            else:
                logger.warning(f"Unexpected response format from {endpoint}")
                return []
        except Exception as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return None

    def get_index_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get index list from FMP API."""
        logger.info("Downloading index list")

        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get_list_data("index")
            if cached_data:
                logger.debug("Cache hit for index list")
                return cached_data

        # Fetch from API
        data = self._make_request("index-list")
        if data:
            # Filter for USD currency only
            filtered_data = [item for item in data if item.get("currency") == "USD"]
            logger.info(
                f"Downloaded {len(filtered_data)} index records "
                f"(filtered from {len(data)})"
            )

            # Store in cache
            if self.use_cache and filtered_data:
                self.cache.store_list_data("index", filtered_data)

            return filtered_data
        return None

    def get_sector_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get sector list from FMP API."""
        logger.info("Downloading sector list")

        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get_list_data("sector")
            if cached_data:
                logger.debug("Cache hit for sector list")
                return cached_data

        # Fetch from API
        data = self._make_request("available-sectors")
        if data:
            logger.info(f"Downloaded {len(data)} sector records")

            # Store in cache
            if self.use_cache:
                self.cache.store_list_data("sector", data)

            return data
        return None

    def get_industry_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get industry list from FMP API."""
        logger.info("Downloading industry list")

        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get_list_data("industry")
            if cached_data:
                logger.debug("Cache hit for industry list")
                return cached_data

        # Fetch from API
        data = self._make_request("available-industries")
        if data:
            logger.info(f"Downloaded {len(data)} industry records")

            # Store in cache
            if self.use_cache:
                self.cache.store_list_data("industry", data)

            return data
        return None

    def get_exchange_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get exchange list from FMP API, filtered for US exchanges."""
        logger.info("Downloading exchange list")

        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get_list_data("exchange")
            if cached_data:
                logger.debug("Cache hit for exchange list")
                return cached_data

        # Fetch from API
        data = self._make_request("available-exchanges")
        if data:
            # Filter for US country code only
            filtered_data = [item for item in data if item.get("countryCode") == "US"]
            logger.info(
                f"Downloaded {len(filtered_data)} exchange records "
                f"(filtered from {len(data)})"
            )

            # Store in cache
            if self.use_cache and filtered_data:
                self.cache.store_list_data("exchange", filtered_data)

            return filtered_data
        return None

    def get_etf_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get ETF list from FMP API."""
        logger.info("Downloading ETF list")

        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get_list_data("etf")
            if cached_data:
                logger.debug("Cache hit for ETF list")
                return cached_data

        # Get US exchanges for filtering
        exchanges = self.get_exchange_list()
        if not exchanges:
            logger.error("Failed to get exchange list for ETF filtering")
            return None

        us_exchange_names = {
            ex.get("exchangeShortName")
            for ex in exchanges
            if ex.get("exchangeShortName")
        }

        # Fetch ETF data from API
        params = {"country": "US", "isEtf": "true", "isFund": "false"}
        data = self._make_request("company-screener", params)
        if data:
            # Filter by US exchanges
            filtered_data = [
                item
                for item in data
                if item.get("exchangeShortName") in us_exchange_names
            ]
            logger.info(
                f"Downloaded {len(filtered_data)} ETF records "
                f"(filtered from {len(data)})"
            )

            # Store in cache
            if self.use_cache and filtered_data:
                self.cache.store_list_data("etf", filtered_data)

            return filtered_data
        return None

    def get_fund_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get fund list from FMP API."""
        logger.info("Downloading fund list")

        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get_list_data("fund")
            if cached_data:
                logger.debug("Cache hit for fund list")
                return cached_data

        # Get US exchanges for filtering
        exchanges = self.get_exchange_list()
        if not exchanges:
            logger.error("Failed to get exchange list for fund filtering")
            return None

        us_exchange_names = {
            ex.get("exchangeShortName")
            for ex in exchanges
            if ex.get("exchangeShortName")
        }

        # Fetch fund data from API
        params = {"country": "US", "isEtf": "false", "isFund": "true"}
        data = self._make_request("company-screener", params)
        if data:
            # Filter by US exchanges
            filtered_data = [
                item
                for item in data
                if item.get("exchangeShortName") in us_exchange_names
            ]
            logger.info(
                f"Downloaded {len(filtered_data)} fund records "
                f"(filtered from {len(data)})"
            )

            # Store in cache
            if self.use_cache and filtered_data:
                self.cache.store_list_data("fund", filtered_data)

            return filtered_data
        return None

    def get_stock_list(
        self, sp500_only: bool = False, nasdaq_only: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """Get stock list from FMP API with optional filtering."""
        logger.info("Downloading stock list")

        # Build cache key based on filters
        cache_key = "stock"
        if sp500_only:
            cache_key = "stock_sp500"
        elif nasdaq_only:
            cache_key = "stock_nasdaq"

        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get_list_data(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for {cache_key} list")
                return cached_data

        # Handle special filtering cases
        if sp500_only:
            data = self._make_request("sp500-constituent")
            if data:
                logger.info(f"Downloaded {len(data)} S&P 500 stock records")
                # Store in cache
                if self.use_cache:
                    self.cache.store_list_data(cache_key, data)
                return data
        elif nasdaq_only:
            data = self._make_request("nasdaq-constituent")
            if data:
                logger.info(f"Downloaded {len(data)} NASDAQ 100 stock records")
                # Store in cache
                if self.use_cache:
                    self.cache.store_list_data(cache_key, data)
                return data
        else:
            # Get all US stocks
            # Get US exchanges for filtering
            exchanges = self.get_exchange_list()
            if not exchanges:
                logger.error("Failed to get exchange list for stock filtering")
                return None

            us_exchange_names = {
                ex.get("exchangeShortName")
                for ex in exchanges
                if ex.get("exchangeShortName")
            }

            # Fetch stock data from API
            params = {"country": "US", "isEtf": "false", "isFund": "false"}
            data = self._make_request("company-screener", params)
            if data:
                # Filter by US exchanges
                filtered_data = [
                    item
                    for item in data
                    if item.get("exchangeShortName") in us_exchange_names
                ]
                logger.info(
                    f"Downloaded {len(filtered_data)} stock records "
                    f"(filtered from {len(data)})"
                )

                # Store in cache
                if self.use_cache and filtered_data:
                    self.cache.store_list_data(cache_key, filtered_data)

                return filtered_data
        return None


def format_index_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Format index data for output."""
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    # Select and rename columns as needed
    columns = ["symbol", "name", "exchange"]
    available_columns = [col for col in columns if col in df.columns]
    return df[available_columns]


def format_basic_list_data(data: List[Dict[str, Any]], list_type: str) -> pd.DataFrame:
    """Format basic list data (sectors, industries) for output."""
    if not data:
        return pd.DataFrame()

    # For sectors and industries, data might be just strings or dictionaries
    if data and isinstance(data[0], str):
        return pd.DataFrame({list_type: data})
    else:
        return pd.DataFrame(data)


def format_exchange_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Format exchange data for output."""
    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data)


def format_company_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Format company data (ETF, fund, stock) for output."""
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # Standardize company name field
    if "companyName" not in df.columns and "name" in df.columns:
        df["companyName"] = df["name"]
    elif "name" in df.columns:
        # Both fields exist, fill companyName with name where companyName is missing
        df["companyName"] = df["companyName"].fillna(df["name"])

    # Select specific columns for ETF/fund/stock data
    columns = ["symbol", "companyName", "sector", "industry"]
    available_columns = [col for col in columns if col in df.columns]
    return df[available_columns]


def save_data(data: pd.DataFrame, filename: str, format_type: str, directory: str):
    """Save data to file."""
    filepath = Path(directory) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if format_type.lower() == "json":
        # Convert to JSON with proper handling
        data_dict = data.to_dict(orient="records")
        # Convert any NaN values to None for JSON serialization
        for record in data_dict:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None

        with open(filepath, "w") as f:
            json.dump(data_dict, f, indent=2, default=str)
    else:  # CSV
        data.to_csv(filepath, index=False)

    logger.info(f"Data saved to {filepath}")


@click.command()
@click.argument("list_type", required=False)
@click.option(
    "--sp500",
    "--s&p",
    "sp500_filter",
    is_flag=True,
    help="Filter stocks to S&P 500 constituents only",
)
@click.option(
    "--nasdaq",
    "nasdaq_filter",
    is_flag=True,
    help="Filter stocks to NASDAQ 100 constituents only",
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
    "--no-cache",
    is_flag=True,
    help="Disable caching and always fetch fresh data from API",
)
@click.pass_context
def ls_command(
    ctx,
    list_type,
    sp500_filter,
    nasdaq_filter,
    output,
    filename,
    output_format,
    directory,
    no_cache,
):
    """List financial information.

    Lists available financial data based on the specified list type.

    Examples:
      duk ls                     # Show available list types
      duk ls index               # List all USD indexes
      duk ls sector              # List all available sectors
      duk ls industry            # List all available industries
      duk ls exchange            # List US exchanges
      duk ls etf                 # List US ETFs
      duk ls fund                # List US funds
      duk ls stock               # List US stocks
      duk ls stock --sp500       # List S&P 500 stocks only
      duk ls stock --nasdaq      # List NASDAQ 100 stocks only
    """
    # Available list types
    available_lists = [
        "index",
        "sector",
        "industry",
        "exchange",
        "etf",
        "fund",
        "stock",
    ]

    # If no list type specified, show available options
    if not list_type:
        click.echo("Available lists:")
        for lst in available_lists:
            click.echo(f"  {lst}")
        return

    # Validate list type
    if list_type not in available_lists:
        click.echo(
            f"Error: Unknown list type '{list_type}'. "
            f"Available types: {', '.join(available_lists)}",
            err=True,
        )
        sys.exit(1)

    # Validate stock filter options
    if (sp500_filter or nasdaq_filter) and list_type != "stock":
        click.echo(
            "Error: --sp500 and --nasdaq options can only be used "
            "with 'stock' list type",
            err=True,
        )
        sys.exit(1)

    if sp500_filter and nasdaq_filter:
        click.echo("Error: Cannot specify both --sp500 and --nasdaq filters", err=True)
        sys.exit(1)

    # Create downloader
    downloader = FinancialListDownloader(use_cache=not no_cache)

    # Download data based on list type
    data = None
    if list_type == "index":
        data = downloader.get_index_list()
        df = format_index_data(data) if data else pd.DataFrame()
    elif list_type == "sector":
        data = downloader.get_sector_list()
        df = format_basic_list_data(data, "sector") if data else pd.DataFrame()
    elif list_type == "industry":
        data = downloader.get_industry_list()
        df = format_basic_list_data(data, "industry") if data else pd.DataFrame()
    elif list_type == "exchange":
        data = downloader.get_exchange_list()
        df = format_exchange_data(data) if data else pd.DataFrame()
    elif list_type == "etf":
        data = downloader.get_etf_list()
        df = format_company_data(data) if data else pd.DataFrame()
    elif list_type == "fund":
        data = downloader.get_fund_list()
        df = format_company_data(data) if data else pd.DataFrame()
    elif list_type == "stock":
        data = downloader.get_stock_list(
            sp500_only=sp500_filter, nasdaq_only=nasdaq_filter
        )
        df = format_company_data(data) if data else pd.DataFrame()

    # Check if data was retrieved
    if data is None:
        click.echo(f"Error: Failed to download {list_type} data", err=True)
        sys.exit(1)

    if df.empty:
        click.echo(f"No {list_type} data found", err=True)
        sys.exit(1)

    # Output data
    if output or filename:
        # Determine filename
        if not filename:
            suffix = ""
            if list_type == "stock":
                if sp500_filter:
                    suffix = "_sp500"
                elif nasdaq_filter:
                    suffix = "_nasdaq"
            filename = f"{list_type}_list{suffix}.{output_format}"
        elif not filename.endswith(f".{output_format}"):
            filename = f"{filename}.{output_format}"

        save_data(df, filename, output_format, directory)
        click.echo(f"Data saved to {Path(directory) / filename}")
    else:
        # Output to stdout
        if output_format == "json":
            # Convert to JSON
            data_dict = df.to_dict(orient="records")
            for record in data_dict:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
            click.echo(json.dumps(data_dict, indent=2, default=str))
        else:
            # Output CSV to stdout
            click.echo(df.to_csv(index=False))
