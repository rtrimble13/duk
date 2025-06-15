"""
Treasury rate subprogram for downloading par treasury yield data.
"""

import json
import logging
import sys
from datetime import timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
import pandas as pd
import requests
import numpy as np
from dateutil.parser import parse as parse_date
from scipy import interpolate


logger = logging.getLogger(__name__)


class TreasuryRateDownloader:
    """Class for downloading treasury rate data from treasury.gov."""

    # Treasury.gov API endpoint for daily treasury par yield curve rates
    BASE_URL = (
        "https://api.fiscaldata.treasury.gov/services/api/v1/"
        "accounting/od/daily_treasury_par_yield_curve_rates"
    )

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "duk-treasury-downloader/0.1.0"})

    def get_latest_date(self) -> Optional[str]:
        """Get the most recent date available in the treasury data."""
        try:
            # Get just one record to find the latest date
            params = {"sort": "-record_date", "page[size]": "1"}
            response = self._make_request(params)
            if response and len(response["data"]) > 0:
                return response["data"][0]["record_date"]
        except Exception as e:
            logger.error(f"Failed to get latest date: {e}")
        return None

    def download_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Download treasury par yield curve data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            days: Number of days to download from start_date
                  (or latest date if start_date not provided)

        Returns:
            List of treasury rate records or None if failed
        """
        try:
            params = {"sort": "record_date"}

            # Handle date parameters
            if days and not start_date:
                # Get latest date and calculate start date
                latest = self.get_latest_date()
                if not latest:
                    logger.error("Could not determine latest date")
                    return None
                end_date = latest
                start_date_obj = parse_date(latest) - timedelta(days=days - 1)
                start_date = start_date_obj.strftime("%Y-%m-%d")
            elif days and start_date:
                # Calculate end date from start date + days
                start_date_obj = parse_date(start_date)
                end_date_obj = start_date_obj + timedelta(days=days - 1)
                end_date = end_date_obj.strftime("%Y-%m-%d")
            elif start_date and not end_date:
                # If only start date provided, get just that date
                end_date = start_date
            elif not start_date and not end_date and not days:
                # Default: get most recent date
                latest = self.get_latest_date()
                if not latest:
                    logger.error("Could not determine latest date")
                    return None
                start_date = end_date = latest

            # Build filter for date range
            if start_date and end_date:
                if start_date == end_date:
                    date_filter = f"record_date:eq:{start_date}"
                else:
                    date_filter = (
                        f"record_date:gte:{start_date},record_date:lte:{end_date}"
                    )
                params["filter"] = date_filter

            logger.info(f"Downloading treasury data from {start_date} to {end_date}")
            response = self._make_request(params)

            if response:
                logger.info(f"Downloaded {len(response['data'])} records")
                return response["data"]

        except Exception as e:
            logger.error(f"Failed to download treasury data: {e}")

        return None

    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API request to treasury.gov."""
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None


def format_data_for_pandas(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert treasury data to pandas-friendly format."""
    if not data:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Convert date column to datetime
    if "record_date" in df.columns:
        df["record_date"] = pd.to_datetime(df["record_date"])

    # Convert rate columns to numeric, handling None values
    rate_columns = [
        col for col in df.columns if col.endswith("_yr") or col.endswith("_mo")
    ]
    for col in rate_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def maturity_to_years(maturity_str: str) -> float:
    """Convert maturity string (e.g., '1_mo', '10_yr') to decimal years."""
    if maturity_str.endswith("_mo"):
        months = int(maturity_str.split("_")[0])
        return months / 12.0
    elif maturity_str.endswith("_yr"):
        years = int(maturity_str.split("_")[0])
        return float(years)
    else:
        raise ValueError(f"Unknown maturity format: {maturity_str}")


def get_interpolation_maturities(interval: str) -> np.ndarray:
    """Get maturity points (in years) for interpolation based on interval."""
    if interval == "day":
        # Daily from 1 day to 30 years (365 * 30 points would be too many,
        # so we'll be reasonable)
        return np.concatenate(
            [
                np.linspace(1 / 365, 1 / 12, 5),  # days to 1 month
                np.linspace(1 / 12, 1, 12),  # monthly for first year
                np.linspace(1, 5, 49),  # quarterly for 2-5 years
                np.linspace(5, 30, 26),  # yearly for 5-30 years
            ]
        )
    elif interval == "month":
        # Monthly intervals from 1 month to 30 years
        return np.concatenate(
            [
                np.arange(1 / 12, 1, 1 / 12),  # monthly for first year
                np.arange(1, 30.1, 1 / 12),  # monthly for all years
            ]
        )
    elif interval == "quarter":
        # Quarterly intervals from 3 months to 30 years
        return np.arange(0.25, 30.25, 0.25)
    elif interval == "semiannual":
        # Semiannual intervals from 6 months to 30 years
        return np.arange(0.5, 30.5, 0.5)
    else:
        raise ValueError(f"Unknown interpolation interval: {interval}")


def interpolate_yield_curve(df_row: pd.Series, interval: str) -> pd.DataFrame:
    """
    Interpolate a single row's yield curve using cubic spline.

    Args:
        df_row: Single row from treasury DataFrame containing rates
        interval: Interpolation interval ('day', 'month', 'quarter', 'semiannual')

    Returns:
        DataFrame with interpolated rates
    """
    # Get rate columns and their corresponding maturities
    rate_columns = [
        col for col in df_row.index if col.endswith("_yr") or col.endswith("_mo")
    ]

    # Filter out columns with NaN values for interpolation
    valid_columns = [col for col in rate_columns if not pd.isna(df_row[col])]

    if len(valid_columns) < 3:
        # Need at least 3 points for cubic spline
        raise ValueError("Not enough valid data points for cubic spline interpolation")

    # Convert maturity strings to years and get corresponding rates
    maturities = np.array([maturity_to_years(col) for col in valid_columns])
    rates = np.array([df_row[col] for col in valid_columns])

    # Sort by maturity (should already be sorted, but ensure it)
    sort_idx = np.argsort(maturities)
    maturities = maturities[sort_idx]
    rates = rates[sort_idx]

    # Get target interpolation points
    target_maturities = get_interpolation_maturities(interval)

    # Filter target maturities to be within the available range
    min_maturity = maturities.min()
    max_maturity = maturities.max()
    target_maturities = target_maturities[
        (target_maturities >= min_maturity) & (target_maturities <= max_maturity)
    ]

    # Perform cubic spline interpolation
    cs = interpolate.CubicSpline(maturities, rates)
    interpolated_rates = cs(target_maturities)

    # Create result DataFrame
    record_date = df_row["record_date"]

    result_data = []
    for maturity, rate in zip(target_maturities, interpolated_rates):
        result_data.append(
            {
                "calendar_date": (
                    record_date.strftime("%Y-%m-%d")
                    if isinstance(record_date, pd.Timestamp)
                    else record_date.strftime("%Y-%m-%d")
                ),
                "maturity_years": maturity,
                "interpolated_rate": rate,
            }
        )

    return pd.DataFrame(result_data)


def save_data(data: pd.DataFrame, filename: str, format_type: str, directory: str):
    """Save data to file."""
    filepath = Path(directory) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if format_type.lower() == "json":
        # Convert to JSON with proper date handling
        data_dict = data.to_dict(orient="records")
        # Convert datetime objects to strings for JSON serialization
        for record in data_dict:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, pd.Timestamp):
                    record[key] = value.strftime("%Y-%m-%d")

        with open(filepath, "w") as f:
            json.dump(data_dict, f, indent=2, default=str)
    else:  # CSV
        data.to_csv(filepath, index=False)

    logger.info(f"Data saved to {filepath}")


@click.command()
@click.option("--date", "-d", help="Specific date to download (YYYY-MM-DD format)")
@click.option(
    "--start-date", "-s", help="Start date for date range (YYYY-MM-DD format)"
)
@click.option("--end-date", "-e", help="End date for date range (YYYY-MM-DD format)")
@click.option(
    "--days",
    "-n",
    type=int,
    help="Number of days to download from start date (or latest date if no start date)",
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
    "--interpolate", "-i", is_flag=True, help="Perform cubic spline interpolation"
)
@click.option(
    "--interpolate-interval",
    type=click.Choice(["day", "month", "quarter", "semiannual"]),
    default="semiannual",
    help="Interpolation interval (default: semiannual)",
)
@click.pass_context
def tr_command(
    ctx,
    date,
    start_date,
    end_date,
    days,
    output,
    filename,
    output_format,
    directory,
    interpolate,
    interpolate_interval,
):
    """Download treasury par yield curve rates.

    By default, downloads the most recent available data and prints to stdout.

    Examples:
      duk tr                           # Latest data to stdout
      duk tr --date 2023-12-01         # Specific date to stdout
      duk tr --days 5                  # Last 5 days to stdout
      duk tr --days 30 --output        # Last 30 days to file
      duk tr --start-date 2023-01-01 --end-date 2023-01-31 --output
      duk tr --interpolate             # Latest data with semiannual interpolation
      duk tr --interpolate --interpolate-interval monthly  # Monthly interpolation
    """
    downloader = TreasuryRateDownloader()

    # Validate date arguments
    if date and (start_date or end_date):
        click.echo(
            "Error: Cannot specify --date with --start-date or --end-date", err=True
        )
        sys.exit(1)

    # Use --date as start_date for simplicity
    if date:
        start_date = date
        end_date = date

    # Download data
    data = downloader.download_data(start_date, end_date, days)
    if not data:
        click.echo("Error: Failed to download treasury data", err=True)
        sys.exit(1)

    # Convert to DataFrame
    df = format_data_for_pandas(data)

    if df.empty:
        click.echo("No data found for the specified criteria", err=True)
        sys.exit(1)

    # Perform interpolation if requested
    if interpolate:
        try:
            logger.info(
                f"Performing cubic spline interpolation with "
                f"{interpolate_interval} intervals"
            )
            interpolated_data = []

            for _, row in df.iterrows():
                interpolated_row = interpolate_yield_curve(row, interpolate_interval)
                interpolated_data.append(interpolated_row)

            # Combine all interpolated data
            df = pd.concat(interpolated_data, ignore_index=True)

            # Update filename for interpolated data
            if output or filename:
                if not filename:
                    last_date = df["calendar_date"].iloc[0].replace("-", "")
                    filename = (
                        f"treasury_par_yields_interpolated_"
                        f"{interpolate_interval}_{last_date}.{output_format}"
                    )

        except Exception as e:
            logger.error(f"Interpolation failed: {e}")
            click.echo(f"Error: Interpolation failed - {e}", err=True)
            sys.exit(1)

    # Output data
    if output or filename:
        # Determine filename
        if not filename:
            if interpolate:
                # Filename already set in interpolation block
                pass
            else:
                # Get last date in the data for filename
                last_date = df["record_date"].max().strftime("%Y%m%d")
                filename = f"treasury_par_yields_{last_date}.{output_format}"
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
                    elif isinstance(value, pd.Timestamp):
                        record[key] = value.strftime("%Y-%m-%d")
            click.echo(json.dumps(data_dict, indent=2, default=str))
        else:
            # Output CSV to stdout
            click.echo(df.to_csv(index=False))
