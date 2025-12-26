"""
CLI entry point for duk.

This module provides the main command-line interface using Click.
"""

import logging
import sys
from pathlib import Path

import click
import pandas as pd

from duk import __version__
from duk.config import get_config
from duk.fmp_api import (
    actively_trading_list_api,
    get_price_history,
    get_yield_curve,
    industry_list_api,
    sector_list_api,
)
from duk.logging_config import setup_logging
from duk.ls_utils import process_industries, process_sectors, screen_securities

# Key rate tenors for yield curve analysis
KEY_RATE_TENORS = ["year1", "year5", "year10", "year20", "year30"]


@click.group()
@click.version_option(version=__version__, message="%(version)s")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file (default: ~/.dukrc)",
)
@click.pass_context
def main(ctx, config):
    """
    duk - A CLI tool for downloading markets and financial data.

    Use 'duk <subprogram> --help' for information on specific subprograms.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)

    # Load configuration
    ctx.obj["config"] = get_config(config)

    # Setup logging
    cfg = ctx.obj["config"]
    logger = setup_logging(
        log_level=cfg.log_level,
        log_dir=cfg.log_dir,
        console_output=True,
    )
    ctx.obj["logger"] = logger

    logger.debug("duk initialized")
    logger.debug(f"Configuration loaded from: {cfg.config_path}")
    logger.debug(f"Log level: {cfg.log_level}")


@main.command()
@click.argument("symbol")
@click.option("-v", "--verbose", is_flag=True, help="Print all logging to stdout")
@click.option(
    "-q", "--quiet", is_flag=True, help="Suppress printing price history data to stdout"
)
@click.option("-s", "--start-date", help="Start date (YYYY-MM-DD)")
@click.option("-e", "--end-date", help="End date (YYYY-MM-DD)")
@click.option("-n", "--limit", type=int, help="Limit number of records to return")
@click.option(
    "-f",
    "--frequency",
    type=click.Choice(
        ["day", "week", "month", "quarter", "semi-annual", "annual"],
        case_sensitive=False,
    ),
    default="day",
    help="Data frequency (default: day)",
)
@click.option("--ohlc", is_flag=True, help="Return Date, Open, High, Low, Close fields")
@click.option("--hlc", is_flag=True, help="Return Date, High, Low, Close fields")
@click.option("--close", is_flag=True, help="Return Date and Close fields")
@click.option(
    "--hlcv", is_flag=True, help="Return Date, High, Low, Close, Volume fields"
)
@click.option("--cv", is_flag=True, help="Return Date, Close, Volume fields")
@click.option("--adj", is_flag=True, help="Retrieve dividend-adjusted price history")
@click.option("--csv", "output_csv", is_flag=True, help="Output data as CSV (default)")
@click.option("--json", "output_json", is_flag=True, help="Output data as JSON")
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help=(
        "Write data to file. If path is a directory, "
        "format filename as <symbol>_<start>_<end>.<ext>"
    ),
)
@click.pass_context
def ph(
    ctx,
    symbol,
    verbose,
    quiet,
    start_date,
    end_date,
    limit,
    frequency,
    ohlc,
    hlc,
    close,
    hlcv,
    cv,
    adj,
    output_csv,
    output_json,
    output,
):
    """
    Request price history for a symbol.

    SYMBOL: The ticker symbol (e.g., AAPL, MSFT). Case insensitive.
    """
    # Get logger from context
    logger = ctx.obj.get("logger", logging.getLogger("duk"))

    # Adjust logging based on verbose flag
    if verbose:
        logger.setLevel(logging.INFO)
        # Enable console output for all handlers
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, logging.FileHandler
            ):
                handler.setLevel(logging.DEBUG)

    # Make symbol uppercase for consistency
    symbol = symbol.upper()

    logger.info(f"Requesting price history for {symbol}")

    # Get API key from configuration
    cfg = ctx.obj["config"]
    api_key = cfg.fmp_key

    if not api_key:
        logger.error("FMP API key not configured")
        click.echo(
            "Error: FMP API key not configured. Set FMP_API_KEY environment variable "
            "or add fmp_key to [api] section in ~/.dukrc",
            err=True,
        )
        sys.exit(1)

    # Determine output format
    if output_csv and output_json:
        logger.error("Only one output format can be specified")
        click.echo(
            "Error: Only one of --csv or --json can be specified",
            err=True,
        )
        sys.exit(1)

    # Default to CSV if neither is specified
    output_format = "json" if output_json else "csv"

    # Determine which fields to return
    fields = None
    field_filters = [ohlc, hlc, close, hlcv, cv]
    if sum(field_filters) > 1:
        logger.error("Only one field filter option can be specified")
        click.echo(
            "Error: Only one of --ohlc, --hlc, --close, --hlcv, --cv can be specified",
            err=True,
        )
        sys.exit(1)

    if ohlc:
        fields = ["open", "high", "low", "close"]
    elif hlc:
        fields = ["high", "low", "close"]
    elif close:
        fields = ["close"]
    elif hlcv:
        fields = ["high", "low", "close", "volume"]
    elif cv:
        fields = ["close", "volume"]

    # Fetch price history
    try:
        df = get_price_history(
            api_key=api_key,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            limit=limit,
            fields=fields,
            adjusted=adj,
        )
    except Exception as e:
        logger.error(f"Failed to fetch price history: {e}")
        click.echo(f"Error: Failed to fetch price history: {e}", err=True)
        sys.exit(1)

    if df.empty:
        logger.warning(f"No data returned for {symbol}")
        if not quiet:
            click.echo(f"No data found for {symbol}")
        sys.exit(0)

    logger.info(f"Retrieved {len(df)} records for {symbol}")

    # Prepare output
    # Reset index to include date as a column in output
    output_df = df.reset_index()

    # Handle output to file
    if output:
        output_path = Path(output)

        # If output is a directory, format filename
        if output_path.is_dir():
            start_str = start_date or "earliest"
            end_str = end_date or "latest"
            ext = "json" if output_format == "json" else "csv"
            filename = f"{symbol}_{start_str}_{end_str}.{ext}"
            output_path = output_path / filename

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file based on format
        if output_format == "json":
            output_df.to_json(output_path, orient="records", date_format="iso")
        else:
            output_df.to_csv(output_path, index=False)

        logger.info(f"Data written to {output_path}")

        if not quiet:
            click.echo(f"Data written to {output_path}")

    # Print to stdout unless quiet flag is set
    if not quiet:
        if output_format == "json":
            click.echo(output_df.to_json(orient="records", date_format="iso"))
        else:
            click.echo(output_df.to_csv(index=False))


@main.command()
@click.option("-v", "--verbose", is_flag=True, help="Print all logging to stdout")
@click.option(
    "-q", "--quiet", is_flag=True, help="Suppress printing yield curve data to stdout"
)
@click.option("-s", "--start-date", help="Start date (YYYY-MM-DD)")
@click.option("-e", "--end-date", help="End date (YYYY-MM-DD)")
@click.option("-n", "--limit", type=int, help="Limit number of records to return")
@click.option(
    "-z",
    "--zero-rates",
    is_flag=True,
    help="Return zero rate yield curve (bootstrapped from par rates)",
)
@click.option(
    "--tenors",
    help=(
        "Filter tenor range. Specify as 'start_tenor, end_tenor'. "
        "Example: 'month6, year10' to return tenors from 6 months to 10 years."
    ),
)
@click.option(
    "--key-rates",
    is_flag=True,
    help="Return only key rate tenors: year1, year5, year10, year20, year30",
)
@click.option(
    "-i",
    "--interval",
    type=click.Choice(
        ["day", "week", "month", "quarter", "semi-annual", "annual"],
        case_sensitive=False,
    ),
    help="Interpolation interval between tenors",
)
@click.option("--csv", "output_csv", is_flag=True, help="Output data as CSV (default)")
@click.option("--json", "output_json", is_flag=True, help="Output data as JSON")
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help=(
        "Write data to file. If path is a directory, "
        "format filename as yc_<start>_<end>.<ext>"
    ),
)
@click.option(
    "-p",
    "--precision",
    type=int,
    default=4,
    help="Decimal precision for yield rates (default: 4)",
)
@click.pass_context
def yc(
    ctx,
    verbose,
    quiet,
    start_date,
    end_date,
    limit,
    zero_rates,
    tenors,
    key_rates,
    interval,
    output_csv,
    output_json,
    output,
    precision,
):
    """
    Request yield curve data.

    Retrieves treasury yield curve data from the FMP API.
    """
    # Get logger from context
    logger = ctx.obj.get("logger", logging.getLogger("duk"))

    # Adjust logging based on verbose flag
    if verbose:
        logger.setLevel(logging.INFO)
        # Enable console output for all handlers
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, logging.FileHandler
            ):
                handler.setLevel(logging.DEBUG)

    logger.info("Requesting yield curve data")

    # Get API key from configuration
    cfg = ctx.obj["config"]
    api_key = cfg.fmp_key

    if not api_key:
        logger.error("FMP API key not configured")
        click.echo(
            "Error: FMP API key not configured. Set FMP_API_KEY environment variable "
            "or add fmp_key to [api] section in ~/.dukrc",
            err=True,
        )
        sys.exit(1)

    # Determine output format
    if output_csv and output_json:
        logger.error("Only one output format can be specified")
        click.echo(
            "Error: Only one of --csv or --json can be specified",
            err=True,
        )
        sys.exit(1)

    # Default to CSV if neither is specified
    output_format = "json" if output_json else "csv"

    # Handle tenors parameter and key-rates mutual exclusivity
    if tenors and key_rates:
        logger.error("Cannot use both --tenors and --key-rates")
        click.echo(
            "Error: Cannot use both --tenors and --key-rates. Choose one.",
            err=True,
        )
        sys.exit(1)

    # Parse tenors parameter
    tenors_tuple = None
    if tenors:
        try:
            # Parse the tenors string (e.g., "month6, year10")
            tenor_parts = [t.strip() for t in tenors.split(",")]
            if len(tenor_parts) != 2:
                raise ValueError("tenors must have exactly 2 values")
            tenors_tuple = (tenor_parts[0], tenor_parts[1])
        except Exception as e:
            logger.error(f"Invalid tenors format: {e}")
            click.echo(
                f"Error: Invalid tenors format. Use format: 'start_tenor, end_tenor'. "
                f"Example: 'month6, year10'. Error: {e}",
                err=True,
            )
            sys.exit(1)

    # Handle key-rates option
    if key_rates:
        tenors_tuple = (KEY_RATE_TENORS[0], KEY_RATE_TENORS[-1])

    # Fetch yield curve
    try:
        df = get_yield_curve(
            api_key=api_key,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            zero_rates=zero_rates,
            tenors=tenors_tuple,
            interval=interval,
        )
    except Exception as e:
        logger.error(f"Failed to fetch yield curve: {e}")
        click.echo(f"Error: Failed to fetch yield curve: {e}", err=True)
        sys.exit(1)

    if df.empty:
        logger.warning("No data returned for yield curve")
        if not quiet:
            click.echo("No yield curve data found")
        sys.exit(0)

    # Apply precision to yield rates
    rate_columns = df.select_dtypes(include=["float", "int"]).columns
    # Exclude non-rate columns like 'date' or 'years'
    rate_columns = [col for col in rate_columns if col not in ["date", "years"]]
    df[rate_columns] = df[rate_columns].round(precision)

    # Filter for key-rates if specified (after fetching data)
    if key_rates:
        # Check if we have a single-date response (tenor-indexed)
        if "years" in df.columns:
            # Single date format - filter by index (tenor names)
            available_key_tenors = [t for t in KEY_RATE_TENORS if t in df.index]
            df = df.loc[available_key_tenors]
        else:
            # Multiple date format - filter by columns (tenor names)
            available_key_tenors = [t for t in KEY_RATE_TENORS if t in df.columns]
            df = df[available_key_tenors]

    logger.info(f"Retrieved yield curve data with {len(df)} records")

    # Prepare output
    # Reset index to include date/tenor as a column in output
    output_df = df.reset_index()

    # Handle output to file
    if output:
        output_path = Path(output)

        # If output is a directory, format filename
        if output_path.is_dir():
            start_str = start_date or "earliest"
            end_str = end_date or "latest"
            ext = "json" if output_format == "json" else "csv"
            filename = f"yc_{start_str}_{end_str}.{ext}"
            output_path = output_path / filename

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file based on format
        if output_format == "json":
            output_df.to_json(output_path, orient="records", date_format="iso")
        else:
            output_df.to_csv(output_path, index=False)

        logger.info(f"Data written to {output_path}")

        if not quiet:
            click.echo(f"Data written to {output_path}")

    # Print to stdout unless quiet flag is set
    if not quiet:
        if output_format == "json":
            click.echo(output_df.to_json(orient="records", date_format="iso"))
        else:
            click.echo(output_df.to_csv(index=False))


@main.command()
@click.option("-v", "--verbose", is_flag=True, help="Print all logging to stdout")
@click.option(
    "-q", "--quiet", is_flag=True, help="Suppress printing list data to stdout"
)
@click.option("-n", "--limit", type=int, help="Limit number of records to return")
@click.option(
    "--sectors",
    "sectors",
    flag_value="__LIST_ALL__",
    default=None,
    help="List all market sectors or screen by sectors (comma-separated)",
)
@click.option(
    "--industries",
    "industries",
    flag_value="__LIST_ALL__",
    default=None,
    help="List all industries or screen by industries (comma-separated)",
)
@click.option(
    "--market-cap",
    help="Filter by market cap (use >value or <value syntax)",
)
@click.option(
    "--price",
    help="Filter by stock price (use >value or <value syntax)",
)
@click.option(
    "--volume",
    help="Filter by trading volume (use >value or <value syntax)",
)
@click.option(
    "--beta",
    help="Filter by beta value (use >value or <value syntax)",
)
@click.option(
    "--dividend",
    help="Filter by dividend (use >value or <value syntax)",
)
@click.option(
    "--exchange",
    help="Filter by exchange (e.g., NASDAQ, NYSE)",
)
@click.option(
    "--country",
    help="Filter by country code (e.g., US)",
)
@click.option(
    "--is-etf",
    is_flag=True,
    help="Filter for ETFs only",
)
@click.option(
    "--is-fund",
    is_flag=True,
    help="Filter for funds only",
)
@click.option(
    "--is-actively-trading",
    is_flag=True,
    help="Filter for actively trading securities only",
)
@click.option("--csv", "output_csv", is_flag=True, help="Output data as CSV (default)")
@click.option("--json", "output_json", is_flag=True, help="Output data as JSON")
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Write data to file",
)
@click.pass_context
def ls(
    ctx,
    verbose,
    quiet,
    limit,
    sectors,
    industries,
    market_cap,
    price,
    volume,
    beta,
    dividend,
    exchange,
    country,
    is_etf,
    is_fund,
    is_actively_trading,
    output_csv,
    output_json,
    output,
):
    """
    List company and market information.

    By default, returns actively trading securities with symbol and name.
    Use --sectors to list market sectors or --sectors="Tech,Healthcare" to screen.
    Use --industries to list industries or --industries="Software,Banking" to screen.

    Screening supports comparison operators:
    - Use > for greater than (e.g., --price=">50")
    - Use < for less than (e.g., --market-cap="<1000000000")
    """
    # Get logger from context
    logger = ctx.obj.get("logger", logging.getLogger("duk"))

    # Adjust logging based on verbose flag
    if verbose:
        logger.setLevel(logging.INFO)
        # Enable console output for all handlers
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, logging.FileHandler
            ):
                handler.setLevel(logging.DEBUG)

    # Get API key from configuration
    cfg = ctx.obj["config"]
    api_key = cfg.fmp_key

    if not api_key:
        logger.error("FMP API key not configured")
        click.echo(
            "Error: FMP API key not configured. Set FMP_API_KEY environment variable "
            "or add fmp_key to [api] section in ~/.dukrc",
            err=True,
        )
        sys.exit(1)

    # Helper function to parse comparison operators
    def parse_filter_value(value_str):
        """Parse filter values with > or < operators.

        Args:
            value_str: String like ">100" or "<50" or "100"

        Returns:
            Tuple of (more_than, lower_than) where one will be None
        """
        if not value_str:
            return None, None

        value_str = value_str.strip()

        if value_str.startswith(">"):
            try:
                return float(value_str[1:]), None
            except ValueError:
                raise ValueError(f"Invalid numeric value: {value_str[1:]}")
        elif value_str.startswith("<"):
            try:
                return None, float(value_str[1:])
            except ValueError:
                raise ValueError(f"Invalid numeric value: {value_str[1:]}")
        else:
            # No operator, treat as exact value (not used in screening API)
            raise ValueError(
                f"Filter value must start with > or < operator: {value_str}"
            )

    # Determine if we're doing screening or listing
    screening_params = [
        market_cap,
        price,
        volume,
        beta,
        dividend,
        exchange,
        country,
        is_etf,
        is_fund,
        is_actively_trading,
    ]
    has_screening_params = any(param for param in screening_params)

    # Parse sectors and industries
    sectors_list = None
    industries_list = None
    is_sectors_flag = sectors == "__LIST_ALL__"  # Flag mode
    is_industries_flag = industries == "__LIST_ALL__"  # Flag mode

    if sectors and not is_sectors_flag:
        # Sectors with values - use for screening
        sectors_list = [s.strip() for s in sectors.split(",")]
    if industries and not is_industries_flag:
        # Industries with values - use for screening
        industries_list = [i.strip() for i in industries.split(",")]

    # Check for mutually exclusive options in list mode
    if is_sectors_flag and is_industries_flag:
        logger.error("Only one list type option can be specified")
        click.echo(
            "Error: Only one of --sectors or --industries can be specified",
            err=True,
        )
        sys.exit(1)

    # Check if screening with both sectors and industries values
    if sectors_list and industries_list and not has_screening_params:
        logger.error("Cannot use both --sectors and --industries values without screening parameters")
        click.echo(
            "Error: When providing values for --sectors and --industries, "
            "at least one screening parameter must be specified",
            err=True,
        )
        sys.exit(1)

    # Determine output format
    if output_csv and output_json:
        logger.error("Only one output format can be specified")
        click.echo(
            "Error: Only one of --csv or --json can be specified",
            err=True,
        )
        sys.exit(1)

    # Default to CSV if neither is specified
    output_format = "json" if output_json else "csv"

    # Decide between listing and screening
    use_screening = (
        (sectors_list or industries_list or has_screening_params)
        and not is_sectors_flag
        and not is_industries_flag
    )

    try:
        if use_screening:
            logger.info("Using security screening")

            # Parse filter parameters
            market_cap_more, market_cap_lower = parse_filter_value(market_cap)
            price_more, price_lower = parse_filter_value(price)
            beta_more, beta_lower = parse_filter_value(beta)
            dividend_more, dividend_lower = parse_filter_value(dividend)

            # Volume needs to be parsed as int
            volume_more, volume_lower = None, None
            if volume:
                volume_more_float, volume_lower_float = parse_filter_value(volume)
                if volume_more_float is not None:
                    volume_more = int(volume_more_float)
                if volume_lower_float is not None:
                    volume_lower = int(volume_lower_float)

            # Call screen_securities
            df = screen_securities(
                api_key=api_key,
                marketCapMoreThan=market_cap_more,
                marketCapLowerThan=market_cap_lower,
                sector=sectors_list,
                industry=industries_list,
                betaMoreThan=beta_more,
                betaLowerThan=beta_lower,
                priceMoreThan=price_more,
                priceLowerThan=price_lower,
                dividendMoreThan=dividend_more,
                dividendLowerThan=dividend_lower,
                volumeMoreThan=volume_more,
                volumeLowerThan=volume_lower,
                exchange=exchange,
                country=country,
                isEtf=is_etf if is_etf else None,
                isFund=is_fund if is_fund else None,
                isActivelyTrading=is_actively_trading if is_actively_trading else None,
                limit=limit,
            )

            if df.empty:
                logger.warning("No screening results returned")
                if not quiet:
                    click.echo("No data found")
                sys.exit(0)

            logger.info(f"Retrieved {len(df)} screening results")

            # Reset index if it was set to symbol
            if df.index.name == "symbol":
                df = df.reset_index()

        else:
            # Traditional listing mode
            if is_sectors_flag:
                logger.info("Requesting sector list")
                data = sector_list_api(api_key)
            elif is_industries_flag:
                logger.info("Requesting industry list")
                data = industry_list_api(api_key)
            else:
                logger.info("Requesting actively trading list")
                data = actively_trading_list_api(api_key)

            if not data:
                logger.warning("No data returned")
                if not quiet:
                    click.echo("No data found")
                sys.exit(0)

            logger.info(f"Retrieved {len(data)} records")

            # Process data based on list type
            if is_sectors_flag:
                df = process_sectors(data)
            elif is_industries_flag:
                df = process_industries(data)
            else:
                # Convert to DataFrame for actively trading list
                df = pd.DataFrame(data)
                # Filter to expected columns
                expected_cols = ["symbol", "name"]
                available_cols = [col for col in expected_cols if col in df.columns]
                if available_cols:
                    df = df[available_cols]

            # Apply limit if specified
            if limit is not None and limit > 0:
                df = df.head(limit)
                logger.debug(f"Limiting to {limit} records")

    except ValueError as e:
        logger.error(f"Invalid parameter value: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to fetch list data: {e}")
        click.echo(f"Error: Failed to fetch list data: {e}", err=True)
        sys.exit(1)

    # Handle output to file
    if output:
        output_path = Path(output)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file based on format
        if output_format == "json":
            df.to_json(output_path, orient="records", date_format="iso")
        else:
            df.to_csv(output_path, index=False)

        logger.info(f"Data written to {output_path}")

        if not quiet:
            click.echo(f"Data written to {output_path}")

    # Print to stdout unless quiet flag is set
    if not quiet:
        if output_format == "json":
            click.echo(df.to_json(orient="records", date_format="iso"))
        else:
            click.echo(df.to_csv(index=False))


if __name__ == "__main__":
    main(obj={})
