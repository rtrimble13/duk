"""
CLI entry point for duk.

This module provides the main command-line interface using Click.
"""

import sys

import click

from duk import __version__
from duk.config import get_config
from duk.logging_config import setup_logging
from duk.ph import format_output, get_price_history


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
@click.option(
    "--start-date",
    "-s",
    help="Start date in YYYY-MM-DD format",
)
@click.option(
    "--end-date",
    "-e",
    help="End date in YYYY-MM-DD format",
)
@click.option(
    "--frequency",
    "-f",
    default="daily",
    type=click.Choice(
        ["daily", "weekly", "monthly", "quarterly", "semi-annual", "annual"],
        case_sensitive=False,
    ),
    help="Data frequency (default: daily)",
)
@click.option(
    "--limit",
    "-l",
    default=5,
    type=int,
    help="Number of data points to return (default: 5)",
)
@click.option(
    "--fields",
    help="Comma-separated list of fields to return " "(e.g., 'date,close,volume')",
)
@click.option(
    "--ohlc",
    is_flag=True,
    help="Return OHLC data (date, open, high, low, close)",
)
@click.option(
    "--hlc",
    is_flag=True,
    help="Return HLC data (date, high, low, close)",
)
@click.option(
    "--csv",
    is_flag=True,
    help="Output in CSV format",
)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.option(
    "--output",
    "-o",
    "output",
    default=None,
    is_flag=False,
    flag_value="",
    help="Write output to file. If specified without a path, uses default "
    "output directory. If a path is provided, writes to that location.",
)
@click.pass_context
def ph(
    ctx,
    symbol,
    start_date,
    end_date,
    frequency,
    limit,
    fields,
    ohlc,
    hlc,
    csv,
    json,
    output,
):
    """
    Download security price history from Financial Modeling Prep.

    SYMBOL is the security ticker symbol (case-insensitive, e.g., 'ibm' or 'IBM')

    Examples:

        # Get last 5 days of IBM price data
        duk ph ibm

        # Get OHLC data in CSV format
        duk ph IBM --ohlc --csv

        # Get HLC data and save to file
        duk ph IBM --hlc -o

        # Get data for a date range in JSON format
        duk ph aapl --start-date 2024-01-01 --end-date 2024-01-31 --json

        # Save weekly data to custom path
        duk ph msft --frequency weekly -o /path/to/output.csv
    """
    from pathlib import Path

    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    logger.info(f"Price history command initiated for symbol: {symbol}")

    # Get API key from config
    api_key = config.fmp_key
    if not api_key:
        logger.error("FMP API key not configured")
        click.echo(
            "Error: FMP API key not found. " "Please set fmp_key in ~/.dukrc",
            err=True,
        )
        sys.exit(1)

    # Validate mutually exclusive field options
    field_option_count = sum([bool(fields), ohlc, hlc])
    if field_option_count > 1:
        logger.error("Multiple field options specified")
        click.echo(
            "Error: Only one of --fields, --ohlc, or --hlc can be specified",
            err=True,
        )
        sys.exit(1)

    # Determine fields based on options
    fields_list = None
    if ohlc:
        fields_list = ["date", "open", "high", "low", "close"]
        logger.debug("Using OHLC fields")
    elif hlc:
        fields_list = ["date", "high", "low", "close"]
        logger.debug("Using HLC fields")
    elif fields:
        fields_list = [f.strip() for f in fields.split(",")]
        logger.debug(f"Requested fields: {fields_list}")

    # Determine output format
    if csv and json:
        logger.error("Both --csv and --json specified")
        click.echo("Error: Only one of --csv or --json can be specified", err=True)
        sys.exit(1)

    if csv:
        output_format = "csv"
    elif json:
        output_format = "json"
    else:
        output_format = config.default_output_type

    logger.debug(f"Output format: {output_format}")

    try:
        # Get price history
        df = get_price_history(
            symbol=symbol,
            api_key=api_key,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            limit=limit,
            fields=fields_list,
        )

        if df.empty:
            logger.warning(f"No data found for {symbol}")
            click.echo(f"No data found for {symbol}", err=True)
            sys.exit(1)

        # Format output
        output_str = format_output(df, output_format)

        # Handle output destination
        if output is not None:
            # Determine output file path
            if output == "":
                # Use default output directory
                output_dir = Path(config.default_output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                ext = "csv" if output_format == "csv" else "json"
                output_file = (
                    output_dir / f"{symbol.lower()}_price_history_{frequency}.{ext}"
                )
            else:
                # Use provided path
                output_file = Path(output)
                output_file.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(output_file, "w") as f:
                f.write(output_str)

            logger.info(f"Output written to {output_file}")
            click.echo(f"Output written to {output_file}")
        else:
            # Output to stdout
            click.echo(output_str)

        logger.info(f"Price history successfully retrieved and displayed for {symbol}")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main(obj={})
