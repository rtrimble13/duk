"""
Technical indicators for financial time series data.

This module provides functions for computing technical indicators
such as simple moving averages (SMA), exponential moving averages (EMA),
and relative strength index (RSI).
"""

import logging
from typing import Union

import pandas as pd

logger = logging.getLogger(__name__)


class IndicatorCalculationError(Exception):
    """Exception raised for indicator calculation errors."""

    pass


def calculate_sma(
    data: Union[pd.Series, pd.DataFrame],
    column: str = None,
    window: int = 20,
) -> pd.DataFrame:
    """
    Calculate Simple Moving Average (SMA) on a dataset.

    The simple moving average is the arithmetic mean of data points over
    a specified window period.

    Args:
        data: Input data as Series or DataFrame. If DataFrame and column is specified,
            SMA is calculated on that column. If column is None, SMA is calculated
            on all numeric columns.
        column: Name of column to calculate SMA on. Only used if data is DataFrame.
            If None, calculates SMA on all numeric columns.
        window: Number of periods for the moving average window. Must be > 0.

    Returns:
        DataFrame with original data and SMA column(s). SMA columns are named
        as '{column}_sma_{window}'. When input is a Series, the series is
        converted to a DataFrame with column name 'value', so the SMA column
        will be 'value_sma_{window}'.

    Raises:
        IndicatorCalculationError: If window is invalid, column doesn't exist,
            or data contains no numeric columns.

    Examples:
        >>> prices = pd.Series([100, 105, 103, 108, 110])
        >>> df = calculate_sma(prices, window=3)
        >>> # Returns DataFrame with 'value' and 'value_sma_3' columns

        >>> df = pd.DataFrame({'close': [100, 105, 103, 108, 110]})
        >>> result = calculate_sma(df, column='close', window=3)
        >>> # Returns DataFrame with 'close' and 'close_sma_3' columns
    """
    if window <= 0:
        raise IndicatorCalculationError("Window must be greater than 0")

    # Convert Series to DataFrame for consistent processing
    if isinstance(data, pd.Series):
        df = data.to_frame(name="value")
        columns_to_process = ["value"]
    else:
        df = data.copy()
        if column is not None:
            # Validate column exists
            if column not in df.columns:
                raise IndicatorCalculationError(
                    f"Column '{column}' not found in DataFrame. "
                    f"Available columns: {list(df.columns)}"
                )
            columns_to_process = [column]
        else:
            # Process all numeric columns
            columns_to_process = df.select_dtypes(include=["number"]).columns.tolist()
            if not columns_to_process:
                raise IndicatorCalculationError("No numeric columns found in DataFrame")

    logger.debug(
        f"Calculating SMA with window={window} on columns: {columns_to_process}"
    )

    # Calculate SMA for each column
    for col in columns_to_process:
        sma_col_name = f"{col}_sma_{window}"
        df[sma_col_name] = df[col].rolling(window=window, min_periods=window).mean()

    logger.info(f"Calculated SMA with window={window}")

    return df


def calculate_ema(
    data: Union[pd.Series, pd.DataFrame],
    column: str = None,
    window: int = 20,
    adjust: bool = False,
) -> pd.DataFrame:
    """
    Calculate Exponential Moving Average (EMA) on a dataset.

    The exponential moving average is a weighted moving average that gives
    more weight to recent data points. The smoothing factor (alpha) is
    calculated as 2 / (window + 1).

    Args:
        data: Input data as Series or DataFrame. If DataFrame and column is specified,
            EMA is calculated on that column. If column is None, EMA is calculated
            on all numeric columns.
        column: Name of column to calculate EMA on. Only used if data is DataFrame.
            If None, calculates EMA on all numeric columns.
        window: Number of periods for the EMA calculation. Must be > 0.
            Used to calculate smoothing factor alpha = 2 / (window + 1).
        adjust: Whether to use adjustment in beginning periods. Default False.
            If False, uses recursive calculation (typical for financial analysis).
            If True, uses weights that sum to 1.

    Returns:
        DataFrame with original data and EMA column(s). EMA columns are named
        as '{column}_ema_{window}'. When input is a Series, the series is
        converted to a DataFrame with column name 'value', so the EMA column
        will be 'value_ema_{window}'.

    Raises:
        IndicatorCalculationError: If window is invalid, column doesn't exist,
            or data contains no numeric columns.

    Examples:
        >>> prices = pd.Series([100, 105, 103, 108, 110])
        >>> df = calculate_ema(prices, window=3)
        >>> # Returns DataFrame with 'value' and 'value_ema_3' columns

        >>> df = pd.DataFrame({'close': [100, 105, 103, 108, 110]})
        >>> result = calculate_ema(df, column='close', window=3)
        >>> # Returns DataFrame with 'close' and 'close_ema_3' columns
    """
    if window <= 0:
        raise IndicatorCalculationError("Window must be greater than 0")

    # Convert Series to DataFrame for consistent processing
    if isinstance(data, pd.Series):
        df = data.to_frame(name="value")
        columns_to_process = ["value"]
    else:
        df = data.copy()
        if column is not None:
            # Validate column exists
            if column not in df.columns:
                raise IndicatorCalculationError(
                    f"Column '{column}' not found in DataFrame. "
                    f"Available columns: {list(df.columns)}"
                )
            columns_to_process = [column]
        else:
            # Process all numeric columns
            columns_to_process = df.select_dtypes(include=["number"]).columns.tolist()
            if not columns_to_process:
                raise IndicatorCalculationError("No numeric columns found in DataFrame")

    logger.debug(
        f"Calculating EMA with window={window}, adjust={adjust} "
        f"on columns: {columns_to_process}"
    )

    # Calculate EMA for each column
    for col in columns_to_process:
        ema_col_name = f"{col}_ema_{window}"
        # Use pandas ewm (exponentially weighted moving average)
        # span parameter is equivalent to window for consistency with SMA
        df[ema_col_name] = (
            df[col].ewm(span=window, adjust=adjust, min_periods=window).mean()
        )

    logger.info(f"Calculated EMA with window={window}, adjust={adjust}")

    return df


def calculate_rsi(
    data: Union[pd.Series, pd.DataFrame],
    column: str = None,
    window: int = 14,
) -> pd.DataFrame:
    """
    Calculate Relative Strength Index (RSI) on a dataset.

    The RSI is a momentum oscillator that measures the speed and magnitude
    of recent price changes to evaluate overbought or oversold conditions.
    RSI values range from 0 to 100, with values above 70 typically indicating
    overbought conditions and values below 30 indicating oversold conditions.

    The RSI is calculated using Wilder's smoothing method:
    1. Calculate price changes (gains and losses)
    2. Calculate average gains and losses over the window period using
       exponential moving average (Wilder's smoothing)
    3. RS (Relative Strength) = Average Gain / Average Loss
    4. RSI = 100 - (100 / (1 + RS))

    Args:
        data: Input data as Series or DataFrame. If DataFrame and column is specified,
            RSI is calculated on that column. If column is None, RSI is calculated
            on all numeric columns.
        column: Name of column to calculate RSI on. Only used if data is DataFrame.
            If None, calculates RSI on all numeric columns.
        window: Number of periods for RSI calculation. Must be > 0. Default is 14.
            Used to calculate the exponential moving average of gains and losses.

    Returns:
        DataFrame with original data and RSI column(s). RSI columns are named
        as '{column}_rsi_{window}'. When input is a Series, the series is
        converted to a DataFrame with column name 'value', so the RSI column
        will be 'value_rsi_{window}'.

    Raises:
        IndicatorCalculationError: If window is invalid, column doesn't exist,
            or data contains no numeric columns.

    Examples:
        >>> prices = pd.Series([100, 105, 103, 108, 110, 107, 112, 115])
        >>> df = calculate_rsi(prices, window=3)
        >>> # Returns DataFrame with 'value' and 'value_rsi_3' columns

        >>> df = pd.DataFrame({'close': [100, 105, 103, 108, 110, 107, 112, 115]})
        >>> result = calculate_rsi(df, column='close', window=14)
        >>> # Returns DataFrame with 'close' and 'close_rsi_14' columns
    """
    if window <= 0:
        raise IndicatorCalculationError("Window must be greater than 0")

    # Convert Series to DataFrame for consistent processing
    if isinstance(data, pd.Series):
        df = data.to_frame(name="value")
        columns_to_process = ["value"]
    else:
        df = data.copy()
        if column is not None:
            # Validate column exists
            if column not in df.columns:
                raise IndicatorCalculationError(
                    f"Column '{column}' not found in DataFrame. "
                    f"Available columns: {list(df.columns)}"
                )
            columns_to_process = [column]
        else:
            # Process all numeric columns
            columns_to_process = df.select_dtypes(include=["number"]).columns.tolist()
            if not columns_to_process:
                raise IndicatorCalculationError("No numeric columns found in DataFrame")

    logger.debug(
        f"Calculating RSI with window={window} on columns: {columns_to_process}"
    )

    # Calculate RSI for each column
    for col in columns_to_process:
        rsi_col_name = f"{col}_rsi_{window}"

        # Calculate price changes
        delta = df[col].diff()

        # Separate gains and losses
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        # Calculate average gain and loss using Wilder's smoothing
        # (EMA with alpha = 1/window)
        # Wilder's smoothing uses adjust=False for recursive calculation
        avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
        avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

        # Calculate RS and RSI
        # Handle division by zero - when avg_loss is 0, RS is undefined
        # We need to handle this case: if avg_loss is 0 and avg_gain > 0, RSI = 100
        # If both are 0, RSI is undefined (NaN)
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # When avg_loss is 0 and avg_gain > 0 (all gains), RSI should be 100
        # When both avg_loss and avg_gain are 0, RSI should remain NaN
        rsi = rsi.where(~((avg_loss == 0) & (avg_gain > 0)), 100)

        df[rsi_col_name] = rsi

    logger.info(f"Calculated RSI with window={window}")

    return df
