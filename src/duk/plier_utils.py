"""
Plier utilities for data manipulation operations.

This module provides functions for manipulating dataframes including
grabbing/stripping columns, joining datasets, and cutting rows.
"""

import logging
from typing import List

import pandas as pd

logger = logging.getLogger(__name__)


def parse_column_spec(spec: str, df: pd.DataFrame) -> List[str]:
    """
    Parse a column specification and return list of column names.

    Args:
        spec: Comma-separated column names or indices (e.g., "close,volume" or "0,2,-1")
        df: DataFrame to get columns from

    Returns:
        List of column names

    Raises:
        ValueError: If column name/index doesn't exist or is invalid
    """
    if not spec:
        return []

    columns = []
    parts = [p.strip() for p in spec.split(",")]

    for part in parts:
        # Check if it's a numeric index
        try:
            idx = int(part)
            # Handle negative indices
            if idx < 0:
                idx = len(df.columns) + idx
            if idx < 0 or idx >= len(df.columns):
                raise ValueError(
                    f"Column index {part} out of range (0 to {len(df.columns) - 1})"
                )
            columns.append(df.columns[idx])
        except ValueError as e:
            # Check if this is a parsing error (not a number) vs a range error
            if "invalid literal" in str(e):
                # Not a number, treat as column name
                if part not in df.columns:
                    raise ValueError(f"Column '{part}' not found in dataframe")
                columns.append(part)
            else:
                # Re-raise other ValueErrors (e.g., out of range)
                raise

    return columns


def grab_columns(df: pd.DataFrame, columns_spec: str) -> pd.DataFrame:
    """
    Retain only specified columns in the dataframe.

    Args:
        df: Input DataFrame
        columns_spec: Comma-separated column names or indices

    Returns:
        DataFrame with only specified columns

    Raises:
        ValueError: If column specification is invalid
    """
    columns = parse_column_spec(columns_spec, df)
    logger.info(f"Grabbing columns: {columns}")

    # Always include date column if it exists and wasn't specified
    date_col = None
    for col in ["date", "Date", "DATE"]:
        if col in df.columns and col not in columns:
            date_col = col
            break

    if date_col:
        result_df = df[[date_col] + columns]
    else:
        result_df = df[columns]

    logger.debug(f"Result has {len(result_df.columns)} columns")
    return result_df


def strip_columns(df: pd.DataFrame, columns_spec: str) -> pd.DataFrame:
    """
    Remove specified columns from the dataframe.

    Args:
        df: Input DataFrame
        columns_spec: Comma-separated column names or indices

    Returns:
        DataFrame with specified columns removed

    Raises:
        ValueError: If column specification is invalid
    """
    columns = parse_column_spec(columns_spec, df)
    logger.info(f"Stripping columns: {columns}")

    result_df = df.drop(columns=columns)
    logger.debug(f"Result has {len(result_df.columns)} columns")
    return result_df


def join_datasets(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Join multiple datasets on their date column.

    Args:
        dataframes: List of DataFrames to join

    Returns:
        Joined DataFrame sorted by date

    Raises:
        ValueError: If not enough dataframes or date column is missing
    """
    if len(dataframes) < 2:
        raise ValueError("At least 2 datasets are required for join operation")

    logger.info(f"Joining {len(dataframes)} datasets")

    # Find date column in first dataframe
    date_col = None
    for col in ["date", "Date", "DATE"]:
        if col in dataframes[0].columns:
            date_col = col
            break

    if date_col is None:
        raise ValueError("Date column not found in first dataset")

    # Verify all dataframes have a date column
    for i, df in enumerate(dataframes):
        has_date = any(col in df.columns for col in ["date", "Date", "DATE"])
        if not has_date:
            raise ValueError(f"Date column not found in dataset {i + 1}")

    # Normalize date column names to 'date'
    normalized_dfs = []
    for df in dataframes:
        df_copy = df.copy()
        for col in ["Date", "DATE"]:
            if col in df_copy.columns:
                df_copy = df_copy.rename(columns={col: "date"})
                break
        normalized_dfs.append(df_copy)

    # Perform outer join on date column
    result_df = normalized_dfs[0]
    for i, df in enumerate(normalized_dfs[1:], start=1):
        result_df = pd.merge(
            result_df, df, on="date", how="outer", suffixes=("", f"_{i}")
        )
        logger.debug(f"Merged dataset {i + 1}")

    # Sort by date and reset index
    result_df = result_df.sort_values("date").reset_index(drop=True)
    logger.info(
        f"Join complete: {len(result_df)} rows, {len(result_df.columns)} columns"
    )

    return result_df


def cut_rows(df: pd.DataFrame, cut_value: int) -> pd.DataFrame:
    """
    Remove rows from the start or end of the dataframe.

    Args:
        df: Input DataFrame
        cut_value: Number of rows to remove (positive=from start, negative=from end)
                   Cannot be 0 or equal to/exceed the dataframe size

    Returns:
        DataFrame with rows removed and index reset

    Raises:
        ValueError: If cut_value is invalid
    """
    if cut_value == 0:
        raise ValueError("cut_value cannot be 0")

    if abs(cut_value) >= len(df):
        raise ValueError(
            f"Cannot cut {abs(cut_value)} rows from dataframe with {len(df)} rows"
        )

    if cut_value > 0:
        logger.info(f"Cutting first {cut_value} rows")
        result_df = df.iloc[cut_value:].reset_index(drop=True)
    else:
        logger.info(f"Cutting last {abs(cut_value)} rows")
        result_df = df.iloc[:cut_value].reset_index(drop=True)

    logger.debug(f"Result has {len(result_df)} rows")
    return result_df
