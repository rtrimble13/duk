"""
Tests for indicators module.
"""

import numpy as np
import pandas as pd
import pytest

from duk.indicators import (
    IndicatorCalculationError,
    calculate_ema,
    calculate_sma,
)


class TestCalculateSMA:
    """Tests for calculate_sma function."""

    def test_sma_basic_series(self):
        """Test SMA calculation with a Series."""
        prices = pd.Series([100, 105, 103, 108, 110])
        result = calculate_sma(prices, window=3)

        assert "value" in result.columns
        assert "value_sma_3" in result.columns
        assert len(result) == 5

        # First two values should be NaN (not enough data for window=3)
        assert pd.isna(result["value_sma_3"].iloc[0])
        assert pd.isna(result["value_sma_3"].iloc[1])

        # Third value should be average of first 3 values
        assert np.isclose(result["value_sma_3"].iloc[2], (100 + 105 + 103) / 3)

        # Fourth value should be average of values 1-3
        assert np.isclose(result["value_sma_3"].iloc[3], (105 + 103 + 108) / 3)

        # Fifth value should be average of values 2-4
        assert np.isclose(result["value_sma_3"].iloc[4], (103 + 108 + 110) / 3)

    def test_sma_dataframe_with_column(self):
        """Test SMA calculation with DataFrame and specific column."""
        df = pd.DataFrame(
            {
                "close": [100, 105, 103, 108, 110],
                "volume": [1000, 1100, 1050, 1200, 1150],
            }
        )
        result = calculate_sma(df, column="close", window=3)

        assert "close" in result.columns
        assert "close_sma_3" in result.columns
        assert "volume" in result.columns
        assert "volume_sma_3" not in result.columns  # Only close should have SMA

        # Verify calculation
        assert np.isclose(result["close_sma_3"].iloc[2], (100 + 105 + 103) / 3)

    def test_sma_dataframe_without_column(self):
        """Test SMA calculation with DataFrame on all numeric columns."""
        df = pd.DataFrame({"close": [100, 105, 103], "volume": [1000, 1100, 1050]})
        result = calculate_sma(df, window=2)

        assert "close_sma_2" in result.columns
        assert "volume_sma_2" in result.columns

        # Verify calculations
        assert np.isclose(result["close_sma_2"].iloc[1], (100 + 105) / 2)
        assert np.isclose(result["volume_sma_2"].iloc[1], (1000 + 1100) / 2)

    def test_sma_window_equals_data_length(self):
        """Test SMA when window equals data length."""
        prices = pd.Series([100, 105, 103])
        result = calculate_sma(prices, window=3)

        # First two should be NaN, last should be average of all
        assert pd.isna(result["value_sma_3"].iloc[0])
        assert pd.isna(result["value_sma_3"].iloc[1])
        assert np.isclose(result["value_sma_3"].iloc[2], (100 + 105 + 103) / 3)

    def test_sma_window_larger_than_data(self):
        """Test SMA when window is larger than data length."""
        prices = pd.Series([100, 105])
        result = calculate_sma(prices, window=3)

        # All values should be NaN (not enough data)
        assert pd.isna(result["value_sma_3"].iloc[0])
        assert pd.isna(result["value_sma_3"].iloc[1])

    def test_sma_window_one(self):
        """Test SMA with window=1 (should equal original values)."""
        prices = pd.Series([100, 105, 103])
        result = calculate_sma(prices, window=1)

        # SMA with window=1 should equal original values
        assert np.isclose(result["value_sma_1"].iloc[0], 100)
        assert np.isclose(result["value_sma_1"].iloc[1], 105)
        assert np.isclose(result["value_sma_1"].iloc[2], 103)

    def test_sma_with_nan_values(self):
        """Test SMA calculation with NaN values in data."""
        prices = pd.Series([100, np.nan, 103, 108, 110])
        result = calculate_sma(prices, window=3)

        # NaN values should propagate in rolling calculation
        assert pd.isna(result["value_sma_3"].iloc[1])
        assert pd.isna(result["value_sma_3"].iloc[2])
        assert pd.isna(result["value_sma_3"].iloc[3])

    def test_sma_invalid_window_zero(self):
        """Test SMA with window=0."""
        prices = pd.Series([100, 105, 103])
        with pytest.raises(
            IndicatorCalculationError, match="Window must be greater than 0"
        ):
            calculate_sma(prices, window=0)

    def test_sma_invalid_window_negative(self):
        """Test SMA with negative window."""
        prices = pd.Series([100, 105, 103])
        with pytest.raises(
            IndicatorCalculationError, match="Window must be greater than 0"
        ):
            calculate_sma(prices, window=-1)

    def test_sma_column_not_found(self):
        """Test SMA when specified column doesn't exist."""
        df = pd.DataFrame({"close": [100, 105, 103]})
        with pytest.raises(IndicatorCalculationError, match="Column 'price' not found"):
            calculate_sma(df, column="price", window=2)

    def test_sma_no_numeric_columns(self):
        """Test SMA when DataFrame has no numeric columns."""
        df = pd.DataFrame({"symbol": ["AAPL", "MSFT", "GOOG"]})
        with pytest.raises(IndicatorCalculationError, match="No numeric columns found"):
            calculate_sma(df, window=2)

    def test_sma_preserves_index(self):
        """Test that SMA preserves the original index."""
        index = pd.date_range("2023-01-01", periods=5)
        prices = pd.Series([100, 105, 103, 108, 110], index=index)
        result = calculate_sma(prices, window=3)

        assert result.index.equals(index)


class TestCalculateEMA:
    """Tests for calculate_ema function."""

    def test_ema_basic_series(self):
        """Test EMA calculation with a Series."""
        prices = pd.Series([100, 105, 103, 108, 110])
        result = calculate_ema(prices, window=3)

        assert "value" in result.columns
        assert "value_ema_3" in result.columns
        assert len(result) == 5

        # First two values should be NaN (not enough data for window=3)
        assert pd.isna(result["value_ema_3"].iloc[0])
        assert pd.isna(result["value_ema_3"].iloc[1])

        # Third value should exist (EMA starts with window periods)
        assert not pd.isna(result["value_ema_3"].iloc[2])

        # EMA should be different from SMA for later values
        sma_result = calculate_sma(prices, window=3)
        # Fourth value should differ from SMA (EMA weighs recent values more)
        assert not np.isclose(
            result["value_ema_3"].iloc[3], sma_result["value_sma_3"].iloc[3]
        )

    def test_ema_dataframe_with_column(self):
        """Test EMA calculation with DataFrame and specific column."""
        df = pd.DataFrame(
            {
                "close": [100, 105, 103, 108, 110],
                "volume": [1000, 1100, 1050, 1200, 1150],
            }
        )
        result = calculate_ema(df, column="close", window=3)

        assert "close" in result.columns
        assert "close_ema_3" in result.columns
        assert "volume" in result.columns
        assert "volume_ema_3" not in result.columns  # Only close should have EMA

        # Verify value exists (specific value depends on adjust parameter)
        assert not pd.isna(result["close_ema_3"].iloc[2])

    def test_ema_dataframe_without_column(self):
        """Test EMA calculation with DataFrame on all numeric columns."""
        df = pd.DataFrame({"close": [100, 105, 103], "volume": [1000, 1100, 1050]})
        result = calculate_ema(df, window=2)

        assert "close_ema_2" in result.columns
        assert "volume_ema_2" in result.columns

        # Verify values exist
        assert not pd.isna(result["close_ema_2"].iloc[1])
        assert not pd.isna(result["volume_ema_2"].iloc[1])

    def test_ema_window_equals_data_length(self):
        """Test EMA when window equals data length."""
        prices = pd.Series([100, 105, 103])
        result = calculate_ema(prices, window=3)

        # First two should be NaN, last should exist
        assert pd.isna(result["value_ema_3"].iloc[0])
        assert pd.isna(result["value_ema_3"].iloc[1])
        assert not pd.isna(result["value_ema_3"].iloc[2])

    def test_ema_window_larger_than_data(self):
        """Test EMA when window is larger than data length."""
        prices = pd.Series([100, 105])
        result = calculate_ema(prices, window=3)

        # All values should be NaN (not enough data)
        assert pd.isna(result["value_ema_3"].iloc[0])
        assert pd.isna(result["value_ema_3"].iloc[1])

    def test_ema_window_one(self):
        """Test EMA with window=1."""
        prices = pd.Series([100, 105, 103])
        result = calculate_ema(prices, window=1)

        # EMA with window=1 should equal original values
        assert np.isclose(result["value_ema_1"].iloc[0], 100)
        assert np.isclose(result["value_ema_1"].iloc[1], 105)
        assert np.isclose(result["value_ema_1"].iloc[2], 103)

    def test_ema_with_nan_values(self):
        """Test EMA calculation with NaN values in data."""
        prices = pd.Series([100, np.nan, 103, 108, 110])
        result = calculate_ema(prices, window=3)

        # NaN values should propagate in calculation
        assert pd.isna(result["value_ema_3"].iloc[1])
        # After NaN, subsequent values depend on EMA behavior with missing data
        # pandas ewm will skip NaN values

    def test_ema_invalid_window_zero(self):
        """Test EMA with window=0."""
        prices = pd.Series([100, 105, 103])
        with pytest.raises(
            IndicatorCalculationError, match="Window must be greater than 0"
        ):
            calculate_ema(prices, window=0)

    def test_ema_invalid_window_negative(self):
        """Test EMA with negative window."""
        prices = pd.Series([100, 105, 103])
        with pytest.raises(
            IndicatorCalculationError, match="Window must be greater than 0"
        ):
            calculate_ema(prices, window=-1)

    def test_ema_column_not_found(self):
        """Test EMA when specified column doesn't exist."""
        df = pd.DataFrame({"close": [100, 105, 103]})
        with pytest.raises(IndicatorCalculationError, match="Column 'price' not found"):
            calculate_ema(df, column="price", window=2)

    def test_ema_no_numeric_columns(self):
        """Test EMA when DataFrame has no numeric columns."""
        df = pd.DataFrame({"symbol": ["AAPL", "MSFT", "GOOG"]})
        with pytest.raises(IndicatorCalculationError, match="No numeric columns found"):
            calculate_ema(df, window=2)

    def test_ema_preserves_index(self):
        """Test that EMA preserves the original index."""
        index = pd.date_range("2023-01-01", periods=5)
        prices = pd.Series([100, 105, 103, 108, 110], index=index)
        result = calculate_ema(prices, window=3)

        assert result.index.equals(index)

    def test_ema_adjust_parameter(self):
        """Test EMA with adjust parameter."""
        prices = pd.Series([100, 105, 103, 108, 110])
        result_no_adjust = calculate_ema(prices, window=3, adjust=False)
        result_adjust = calculate_ema(prices, window=3, adjust=True)

        # Results should differ based on adjust parameter
        # Both should have valid values starting from index 2
        assert not pd.isna(result_no_adjust["value_ema_3"].iloc[2])
        assert not pd.isna(result_adjust["value_ema_3"].iloc[2])

        # Values should be different for indices after the window
        assert not np.isclose(
            result_no_adjust["value_ema_3"].iloc[4],
            result_adjust["value_ema_3"].iloc[4],
        )


class TestCompareSmaaEma:
    """Tests comparing SMA and EMA behavior."""

    def test_ema_more_responsive_than_sma(self):
        """Test that EMA is more responsive to recent changes than SMA."""
        # Create a series with a sudden jump
        prices = pd.Series([100, 100, 100, 100, 100, 120, 120, 120])
        sma_result = calculate_sma(prices, window=5)
        ema_result = calculate_ema(prices, window=5)

        # After the jump (index 5), EMA should respond faster than SMA
        # At index 6, EMA should be closer to 120 than SMA
        sma_val = sma_result["value_sma_5"].iloc[6]
        ema_val = ema_result["value_ema_5"].iloc[6]

        # EMA should be higher (closer to the new price of 120)
        assert ema_val > sma_val

    def test_sma_ema_converge_with_stable_prices(self):
        """Test that SMA and EMA converge with stable prices."""
        # Create a series of constant prices
        prices = pd.Series([100] * 20)
        sma_result = calculate_sma(prices, window=10)
        ema_result = calculate_ema(prices, window=10, adjust=False)

        # With constant prices, both should converge to the price
        # Check last value
        assert np.isclose(sma_result["value_sma_10"].iloc[-1], 100)
        assert np.isclose(ema_result["value_ema_10"].iloc[-1], 100, rtol=0.01)
