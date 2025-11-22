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
    type=click.Choice(["daily", "weekly", "monthly"], case_sensitive=False),
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
    "--output",
    "-o",
    type=click.Choice(["csv", "json"], case_sensitive=False),
    help="Output format (default: uses config default_output_type)",
)
@click.pass_context
def ph(ctx, symbol, start_date, end_date, frequency, limit, fields, output):
    """
    Download security price history from Financial Modeling Prep.

    SYMBOL is the security ticker symbol (case-insensitive, e.g., 'ibm' or 'IBM')

    Examples:

        # Get last 5 days of IBM price data
        duk ph ibm

        # Get last 10 days with specific fields
        duk ph IBM --limit 10 --fields date,close,volume

        # Get data for a date range
        duk ph aapl --start-date 2024-01-01 --end-date 2024-01-31

        # Get weekly data in JSON format
        duk ph msft --frequency weekly --output json
    """
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

    # Parse fields if provided
    fields_list = None
    if fields:
        fields_list = [f.strip() for f in fields.split(",")]
        logger.debug(f"Requested fields: {fields_list}")

    # Determine output format
    output_format = output if output else config.default_output_type
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

        # Format and output
        output_str = format_output(df, output_format)
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
