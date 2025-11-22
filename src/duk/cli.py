"""
Command-line interface for duk.

This module provides the main CLI entry point and command handlers using Click.
"""

import os
import sys
from pathlib import Path

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
    "--out",
    is_flag=False,
    flag_value="",
    default=None,
    help=(
        "Write output to file. If no path specified, "
        "uses default output directory from config."
    ),
)
@click.option(
    "--output-format",
    type=click.Choice(["table", "csv", "json"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
@click.pass_context
def ph(ctx, symbol, limit, from_date, to_date, fields, out, output_format):
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

        # Format output based on output_format
        if output_format == "csv":
            output_data = df.to_csv(index=False)
        elif output_format == "json":
            output_data = df.to_json(orient="records", date_format="iso", indent=2)
        else:  # table
            output_data = df.to_string(index=False)

        # Determine output destination
        if out is not None:
            # User wants to write to file
            config = ctx.obj["config"]

            if out == "":
                # No path specified, use default from config
                output_dir = config.get_output_dir()
                output_dir = os.path.expanduser(output_dir)
            else:
                # Specific path provided
                output_dir = os.path.expanduser(out)

            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Generate filename based on symbol and format
            file_extension = output_format if output_format != "table" else "txt"
            filename = f"{symbol.upper()}_{output_format}.{file_extension}"
            output_path = Path(output_dir) / filename

            # Write to file
            with open(output_path, "w") as f:
                f.write(output_data)

            click.echo(f"Output written to: {output_path}")
            logger.info(f"Output written to: {output_path}")
        else:
            # No -o/--out option, output to stdout
            click.echo(output_data)

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
