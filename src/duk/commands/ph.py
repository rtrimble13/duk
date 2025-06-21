"""
Price history subprogram for aggregating financial data by frequency.
"""

import logging
import sys

import click
import pandas as pd

logger = logging.getLogger(__name__)


def aggregate_by_frequency(data: pd.DataFrame, frequency: str) -> pd.DataFrame:
    """
    Aggregate data by specified frequency.

    Args:
        data: DataFrame with datetime index and numeric columns
        frequency: Frequency string ('weekly', 'monthly', 'quarterly',
                                   'semiannual', 'annual')

    Returns:
        DataFrame aggregated by the specified frequency
    """
    # Map frequency names to pandas offset strings
    # Using Python 3.8 compatible frequency strings
    freq_map = {
        "weekly": "W",
        "monthly": "M",
        "quarterly": "Q",
        "semiannual": "6M",
        "annual": "A",
    }

    if frequency not in freq_map:
        raise ValueError(
            f"Unsupported frequency: {frequency}. Supported: {list(freq_map.keys())}"
        )

    pandas_freq = freq_map[frequency]

    # Ensure data has datetime index
    if not isinstance(data.index, pd.DatetimeIndex):
        if "date" in data.columns:
            data = data.set_index("date")
        elif "record_date" in data.columns:
            data = data.set_index("record_date")
        else:
            raise ValueError(
                "Data must have datetime index or 'date'/'record_date' column"
            )

    # Convert index to datetime if not already
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)

    # Aggregate data using the pandas frequency string
    # Using last() for end-of-period values, which is common for financial data
    aggregated = data.resample(pandas_freq).last()

    # Drop rows with all NaN values
    aggregated = aggregated.dropna(how="all")

    return aggregated


@click.command()
@click.option(
    "--frequency",
    "-f",
    type=click.Choice(["weekly", "monthly", "quarterly", "semiannual", "annual"]),
    default="monthly",
    help="Aggregation frequency (default: monthly)",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Input CSV file with financial data",
)
@click.option("--output", "-o", is_flag=True, help="Save output to file")
@click.option(
    "--output-format",
    type=click.Choice(["csv", "json"]),
    default="csv",
    help="Output format (default: csv)",
)
@click.pass_context
def ph_command(ctx, frequency, input_file, output, output_format):
    """Aggregate price history data by frequency.

    This command demonstrates frequency-based aggregation using pandas
    offset strings that are compatible with Python 3.8.

    Examples:
      duk ph --frequency monthly --input-file data.csv
      duk ph --frequency semiannual --input-file data.csv --output
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    if verbose:
        logger.info(f"Starting price history aggregation with frequency: {frequency}")

    # For demonstration purposes, create sample data if no input file is provided
    if not input_file:
        # Create sample financial data
        dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
        sample_data = pd.DataFrame(
            {
                "price": range(len(dates)),
                "volume": [i * 100 for i in range(len(dates))],
            },
            index=dates,
        )

        click.echo("No input file provided. Using sample data for demonstration.")
        data = sample_data
    else:
        # Read input file
        try:
            data = pd.read_csv(input_file, index_col=0, parse_dates=True)
        except Exception as e:
            logger.error(f"Failed to read input file: {e}")
            click.echo(f"Error: Failed to read input file - {e}", err=True)
            sys.exit(1)

    # Aggregate data by frequency
    try:
        aggregated_data = aggregate_by_frequency(data, frequency)

        if verbose:
            logger.info(f"Aggregated {len(data)} rows to {len(aggregated_data)} rows")

    except Exception as e:
        logger.error(f"Aggregation failed: {e}")
        click.echo(f"Error: Aggregation failed - {e}", err=True)
        sys.exit(1)

    # Output results
    if output:
        # Save to file
        output_filename = f"aggregated_{frequency}_data.{output_format}"

        if output_format == "json":
            aggregated_data.to_json(output_filename, orient="index", date_format="iso")
        else:
            aggregated_data.to_csv(output_filename)

        click.echo(f"Data saved to {output_filename}")

        if verbose:
            logger.info(f"Output saved to {output_filename}")
    else:
        # Output to stdout
        if output_format == "json":
            click.echo(aggregated_data.to_json(orient="index", date_format="iso"))
        else:
            click.echo(aggregated_data.to_csv())
