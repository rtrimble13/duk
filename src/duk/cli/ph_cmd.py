"""
CLI handler for price history (ph) command
"""

import sys

import click

from duk.api.ph import get_price_history
from duk.logger import get_logger

logger = get_logger("cli.ph")


@click.command()
@click.argument("symbol")
@click.option(
    "-l",
    "--limit",
    type=int,
    default=5,
    help="Number of most recent data points to return (default: 5)",
)
@click.option(
    "-f",
    "--from-date",
    "from_date",
    help="Start date in YYYY-MM-DD format",
)
@click.option(
    "-t",
    "--to-date",
    "to_date",
    help="End date in YYYY-MM-DD format",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
@click.option(
    "--fields",
    help="Comma-separated list of fields to display (default: date,close,volume)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["csv", "json", "table"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
@click.pass_context
def ph(ctx, symbol, limit, from_date, to_date, output, fields, output_format):
    """
    Download security price history from FMP.

    SYMBOL: Security symbol (e.g., IBM, AAPL)
    """
    logger.info(f"Executing ph command for symbol: {symbol}")

    # Get configuration from context
    config = ctx.obj["config"]

    # Get API key
    api_key = config.get_fmp_api_key()
    if not api_key or api_key == "YOUR_FMP_API_KEY_HERE":
        logger.error("FMP API key not configured")
        click.echo("Error: FMP API key not configured", err=True)
        click.echo(
            "Please set your API key in ~/.dukrc",
            err=True,
        )
        sys.exit(1)

    try:
        # Get price history
        df = get_price_history(
            symbol=symbol,
            api_key=api_key,
            limit=limit,
            from_date=from_date,
            to_date=to_date,
        )

        if df.empty:
            logger.warning(f"No data found for symbol: {symbol}")
            click.echo(f"No data found for symbol: {symbol}", err=True)
            sys.exit(1)

        # Select fields to display
        if fields:
            field_list = [f.strip() for f in fields.split(",")]
            # Filter to only include fields that exist in the dataframe
            available_fields = [f for f in field_list if f in df.columns]
            if not available_fields:
                logger.error("None of the specified fields exist in the data")
                click.echo(
                    "Error: None of the specified fields exist in the data",
                    err=True,
                )
                sys.exit(1)
            df = df[available_fields]
        else:
            # Default fields
            default_fields = ["date", "close", "volume"]
            available_fields = [f for f in default_fields if f in df.columns]
            if available_fields:
                df = df[available_fields]

        # Format and output
        if output:
            # Write to file
            logger.info(f"Writing output to file: {output}")
            if output_format == "csv":
                df.to_csv(output, index=False)
            elif output_format == "json":
                df.to_json(output, orient="records", indent=2)
            else:
                with open(output, "w") as f:
                    f.write(df.to_string(index=False))
            logger.info(f"Output written to {output}")
        else:
            # Write to stdout
            if output_format == "csv":
                click.echo(df.to_csv(index=False), nl=False)
            elif output_format == "json":
                click.echo(df.to_json(orient="records", indent=2))
            else:
                click.echo(df.to_string(index=False))

        logger.info("ph command completed successfully")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
