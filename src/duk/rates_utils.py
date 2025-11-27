"""
Rate utilities for processing treasury rate data.

This module provides functions for converting and processing treasury rate
data retrieved from APIs.
"""

import logging
import re
from typing import Any, Dict, List

import pandas as pd
from scipy.interpolate import CubicSpline

logger = logging.getLogger(__name__)

# Valid interval choices for interpolation
VALID_INTERVALS = ["day", "week", "month", "quarter", "semi-annual", "annual"]

# Conversion constants
DAYS_PER_MONTH = 30
WEEKS_PER_MONTH = 4
MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52
DAYS_PER_YEAR = 365


def treasury_rates2df(par_yields: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert treasury rates API output to a pandas DataFrame.

    Converts the output of treasury_rates_api into a pandas DataFrame
    with the date field converted to a date object and set as the index.

    Args:
        par_yields: List of dictionaries containing treasury rates data,
            as returned by treasury_rates_api. Each dictionary should
            contain a 'date' field and various rate maturity fields.

    Returns:
        pandas DataFrame with the date as the index and rate maturities
        as columns. The DataFrame is sorted by date in ascending order.

    Example:
        >>> from duk.fmp_api import treasury_rates_api
        >>> par_yields = treasury_rates_api("your_api_key")
        >>> df = treasury_rates2df(par_yields)
        >>> print(df.head())
    """
    if not par_yields:
        logger.warning("Empty par_yields input, returning empty DataFrame")
        return pd.DataFrame()

    logger.debug(f"Converting {len(par_yields)} treasury rate records to DataFrame")

    # Create DataFrame from list of dictionaries
    df = pd.DataFrame(par_yields)

    # Convert date column to datetime and set as index
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df.set_index("date")
        df = df.sort_index()
        logger.info(f"Created DataFrame with {len(df)} records")
    else:
        logger.warning("No 'date' column found in par_yields data")

    return df


def _tenor_to_months(tenor: str) -> float:
    """
    Convert a tenor string to months.

    Args:
        tenor: Tenor string like 'month1', 'month6', 'year1', 'year1.5'.

    Returns:
        The tenor value in months as a float.

    Raises:
        ValueError: If the tenor format is not recognized.
    """
    tenor = tenor.lower()

    # Match month tenors (e.g., month1, month6, month1.5)
    month_match = re.match(r"^month(\d+(?:\.\d+)?)$", tenor)
    if month_match:
        return float(month_match.group(1))

    # Match year tenors (e.g., year1, year10, year1.5)
    year_match = re.match(r"^year(\d+(?:\.\d+)?)$", tenor)
    if year_match:
        years = float(year_match.group(1))
        return years * MONTHS_PER_YEAR

    raise ValueError(f"Unrecognized tenor format: {tenor}")


def _months_to_tenor(months: float) -> str:
    """
    Convert months to a tenor string.

    Args:
        months: The tenor value in months.

    Returns:
        Tenor string in the format 'monthN' or 'yearN'.
    """
    if months < 12:
        # Use month format for less than 12 months
        if months == int(months):
            return f"month{int(months)}"
        return f"month{months}"
    else:
        # Use year format for 12 months or more
        years = months / MONTHS_PER_YEAR
        if years == int(years):
            return f"year{int(years)}"
        return f"year{round(years, 3)}"


def _get_interval_in_months(interval: str) -> float:
    """
    Convert interval string to months.

    Args:
        interval: One of 'day', 'week', 'month', 'quarter',
            'semi-annual', 'annual'.

    Returns:
        The interval value in months as a float.

    Raises:
        ValueError: If the interval is not valid.
    """
    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"Invalid interval: {interval}. "
            f"Valid choices are: {', '.join(VALID_INTERVALS)}"
        )

    if interval == "day":
        return 1 / DAYS_PER_MONTH  # 30 days per month
    elif interval == "week":
        return 1 / WEEKS_PER_MONTH  # 4 weeks per month
    elif interval == "month":
        return 1
    elif interval == "quarter":
        return 3
    elif interval == "semi-annual":
        return 6
    elif interval == "annual":
        return 12

    raise ValueError(f"Unhandled interval: {interval}")


def _generate_target_tenors(
    existing_months: List[float], interval_months: float
) -> List[float]:
    """
    Generate a list of target tenor values in months based on the interval.

    This function determines which tenor points should exist based on the
    specified interval, then adds missing points between existing tenors.

    Args:
        existing_months: List of existing tenor values in months.
        interval_months: The maximum gap allowed between tenors in months.

    Returns:
        Sorted list of tenor values in months (includes both existing
        and interpolated points).
    """
    if not existing_months:
        return []

    min_tenor = min(existing_months)
    max_tenor = max(existing_months)

    target_tenors = set(existing_months)

    # Generate target points based on interval
    current = min_tenor
    while current <= max_tenor:
        target_tenors.add(round(current, 6))
        current += interval_months

    return sorted(target_tenors)


def interpolate_rates(
    rate_curve: pd.DataFrame, interval: str = "semi-annual"
) -> pd.DataFrame:
    """
    Perform cubic spline interpolation on a yield curve dataframe.

    This function interpolates missing tenor points in a yield curve based
    on the specified interval using cubic spline interpolation.

    Args:
        rate_curve: DataFrame with rate data. Columns should be tenor names
            (e.g., 'month1', 'year1', 'year10'). Each row represents a
            different date's yield curve.
        interval: The maximum gap allowed between tenors. Valid choices are:
            'day', 'week', 'month', 'quarter', 'semi-annual', 'annual'.
            Default is 'semi-annual'.

    Returns:
        DataFrame with interpolated rates. Includes all original tenors
        plus any interpolated points required to meet the interval
        requirement.

    Raises:
        ValueError: If the interval is not valid or if rate_curve has
            fewer than 2 tenor columns.

    Example:
        >>> df = pd.DataFrame({
        ...     'month1': [4.35],
        ...     'month3': [4.45],
        ...     'year1': [4.68],
        ...     'year2': [4.20]
        ... })
        >>> result = interpolate_rates(df, interval='semi-annual')
        >>> # Result includes interpolated points like 'month6', 'year1.5'
    """
    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"Invalid interval: {interval}. "
            f"Valid choices are: {', '.join(VALID_INTERVALS)}"
        )

    if rate_curve.empty:
        logger.warning("Empty rate_curve input, returning empty DataFrame")
        return pd.DataFrame()

    logger.debug(f"Interpolating rates with interval: {interval}")

    # Get interval in months
    interval_months = _get_interval_in_months(interval)

    # Parse existing tenors and convert to months
    tenor_columns = list(rate_curve.columns)
    tenor_to_months_map = {}

    for tenor in tenor_columns:
        try:
            tenor_to_months_map[tenor] = _tenor_to_months(tenor)
        except ValueError as e:
            logger.warning(f"Skipping unrecognized tenor column: {tenor} - {e}")

    if len(tenor_to_months_map) < 2:
        raise ValueError(
            "Rate curve must have at least 2 valid tenor columns for interpolation"
        )

    existing_months = list(tenor_to_months_map.values())
    existing_tenors = list(tenor_to_months_map.keys())

    # Generate target tenor points
    target_months = _generate_target_tenors(existing_months, interval_months)

    logger.debug(
        f"Interpolating from {len(existing_months)} tenors "
        f"to {len(target_months)} tenors"
    )

    # Perform interpolation for each row
    result_data = []
    for idx, row in rate_curve.iterrows():
        # Get x (months) and y (rates) for existing data points
        x = [tenor_to_months_map[t] for t in existing_tenors]
        y = [row[t] for t in existing_tenors]

        # Handle NaN values by filtering them out
        valid_points = [
            (xi, yi) for xi, yi in zip(x, y) if pd.notna(yi)
        ]

        if len(valid_points) < 2:
            logger.warning(
                f"Row {idx} has fewer than 2 valid data points, skipping"
            )
            continue

        x_valid, y_valid = zip(*valid_points)

        # Sort by x to ensure proper spline fitting
        sorted_indices = sorted(range(len(x_valid)), key=lambda i: x_valid[i])
        x_sorted = [x_valid[i] for i in sorted_indices]
        y_sorted = [y_valid[i] for i in sorted_indices]

        # Create cubic spline
        cs = CubicSpline(x_sorted, y_sorted)

        # Interpolate at target points
        row_data = {}
        for target_month in target_months:
            tenor_str = _months_to_tenor(target_month)

            # Use original value if it exists, otherwise interpolate
            if target_month in existing_months:
                original_tenor = existing_tenors[existing_months.index(target_month)]
                row_data[tenor_str] = row[original_tenor]
            else:
                # Only interpolate within the range of existing data
                min_x = min(x_sorted)
                max_x = max(x_sorted)
                if min_x <= target_month <= max_x:
                    row_data[tenor_str] = float(cs(target_month))
                else:
                    row_data[tenor_str] = None

        result_data.append(row_data)

    if not result_data:
        logger.warning("No valid rows for interpolation")
        return pd.DataFrame()

    # Create result DataFrame with same index as input
    result_df = pd.DataFrame(result_data, index=rate_curve.index[:len(result_data)])

    # Sort columns by tenor (in months)
    sorted_columns = sorted(
        result_df.columns, key=lambda c: _tenor_to_months(c)
    )
    result_df = result_df[sorted_columns]

    logger.info(
        f"Interpolation complete: {len(rate_curve.columns)} tenors -> "
        f"{len(result_df.columns)} tenors"
    )

    return result_df
