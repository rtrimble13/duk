"""
CLI entry point for duk.

This module provides the main command-line interface using Click.
"""

import logging
import sys
from pathlib import Path

import click

from duk import __version__
from duk.config import get_config
from duk.fmp_api import get_price_history
from duk.logging_config import setup_logging


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
@click.option("--cv", is_flag=True, help="Return Date and Volume fields")
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
        logger.setLevel(logging.DEBUG)
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
        fields = ["volume"]

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
    output_df.rename(columns={"date": "Date"}, inplace=True)

    # Capitalize column names for output
    output_df.columns = [col.capitalize() for col in output_df.columns]

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


if __name__ == "__main__":
    main(obj={})
