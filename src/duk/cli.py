"""
Command-line interface for duk.

This module provides the main CLI entry point and command handlers using Click.
"""

import sys

import click

from duk import __version__
from duk.config import get_config
from duk.logger import get_logger, setup_logging


@click.group()
@click.version_option(version=__version__, prog_name="duk")
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to config file (default: ~/.dukrc)",
)
@click.pass_context
def cli(ctx, config):
    """CLI tool for downloading market and financial data."""
    # Store config path in context
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config

    # Initialize config
    if config:
        ctx.obj["config"] = get_config(config)
    else:
        ctx.obj["config"] = get_config()

    # Setup logging
    setup_logging(ctx.obj["config"])
    logger = get_logger("cli")
    logger.info(f"duk v{__version__} started")


@cli.command()
@click.argument("symbol")
@click.option(
    "-l",
    "--limit",
    type=int,
    help="Number of most recent data points to return (default: 5)",
)
@click.option(
    "-f",
    "--from-date",
    help="Start date for historical data (YYYY-MM-DD)",
)
@click.option(
    "-t",
    "--to-date",
    help="End date for historical data (YYYY-MM-DD)",
)
@click.option(
    "--fields",
    multiple=True,
    help="Fields to include in output (e.g., date open high low close volume)",
)
@click.option(
    "-o",
    "--output-format",
    type=click.Choice(["table", "csv", "json"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
@click.pass_context
def ph(ctx, symbol, limit, from_date, to_date, fields, output_format):
    """Download security price history from FMP API."""
    logger = get_logger("cli.ph")
    logger.info(f"Executing ph command for symbol: {symbol}")

    try:
        from duk.ph import get_price_history

        # Convert fields tuple to list if provided
        fields_list = list(fields) if fields else None

        # Get price history
        df = get_price_history(
            symbol=symbol,
            limit=limit,
            from_date=from_date,
            to_date=to_date,
            fields=fields_list,
        )

        if df.empty:
            click.echo(f"No data found for symbol: {symbol}", err=True)
            logger.warning(f"No data found for symbol: {symbol}")
            sys.exit(1)

        # Output format
        if output_format == "csv":
            click.echo(df.to_csv(index=False))
        elif output_format == "json":
            click.echo(df.to_json(orient="records", date_format="iso", indent=2))
        else:  # table
            click.echo(df.to_string(index=False))

        logger.info(f"Successfully output {len(df)} records")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        logger.error(f"ValueError: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        logger.exception("Unexpected error in ph command")
        sys.exit(1)


def main():
    """
    Main entry point for the CLI.
    """
    cli(obj={})


if __name__ == "__main__":
    main()
