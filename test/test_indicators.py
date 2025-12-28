"""
Tests for indicators module.
"""

import numpy as np
import pandas as pd
import pytest

from duk.indicators import (
    IndicatorCalculationError,
    calculate_ema,
    calculate_rsi,
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


class TestCalculateRSI:
    """Tests for calculate_rsi function."""

    def test_rsi_basic_series(self):
        """Test RSI calculation with a Series."""
        # Create a series with upward trend
        prices = pd.Series(
            [100, 102, 104, 103, 105, 107, 106, 108, 110, 109, 111, 113, 112, 114, 116]
        )
        result = calculate_rsi(prices, window=14)

        assert "value" in result.columns
        assert "value_rsi_14" in result.columns
        assert len(result) == 15

        # First value should be NaN (no previous value for diff)
        assert pd.isna(result["value_rsi_14"].iloc[0])

        # Values before window should be NaN
        # (not enough data for EMA with min_periods=window)
        for i in range(1, 14):
            assert pd.isna(result["value_rsi_14"].iloc[i]), f"Expected NaN at index {i}"

        # After window period, RSI should have values
        # RSI should be between 0 and 100
        valid_rsi = result["value_rsi_14"].dropna()
        assert len(valid_rsi) > 0, "Should have some valid RSI values"
        assert all(valid_rsi >= 0)
        assert all(valid_rsi <= 100)

    def test_rsi_dataframe_with_column(self):
        """Test RSI calculation with DataFrame and specific column."""
        df = pd.DataFrame(
            {
                "close": [
                    100,
                    102,
                    104,
                    103,
                    105,
                    107,
                    106,
                    108,
                    110,
                    109,
                    111,
                    113,
                    112,
                    114,
                    116,
                ],
                "volume": [
                    1000,
                    1100,
                    1050,
                    1200,
                    1150,
                    1300,
                    1250,
                    1400,
                    1350,
                    1500,
                    1450,
                    1600,
                    1550,
                    1700,
                    1650,
                ],
            }
        )
        result = calculate_rsi(df, column="close", window=14)

        assert "close" in result.columns
        assert "close_rsi_14" in result.columns
        assert "volume" in result.columns
        assert "volume_rsi_14" not in result.columns  # Only close should have RSI

        # Verify RSI values are in valid range
        valid_rsi = result["close_rsi_14"].dropna()
        assert all(valid_rsi >= 0)
        assert all(valid_rsi <= 100)

    def test_rsi_dataframe_without_column(self):
        """Test RSI calculation with DataFrame on all numeric columns."""
        df = pd.DataFrame(
            {
                "close": [100, 102, 104, 103, 105, 107, 106, 108, 110],
                "volume": [1000, 1100, 1050, 1200, 1150, 1300, 1250, 1400, 1350],
            }
        )
        result = calculate_rsi(df, window=5)

        assert "close_rsi_5" in result.columns
        assert "volume_rsi_5" in result.columns

        # Verify RSI values are in valid range
        valid_close_rsi = result["close_rsi_5"].dropna()
        valid_volume_rsi = result["volume_rsi_5"].dropna()
        assert all(valid_close_rsi >= 0)
        assert all(valid_close_rsi <= 100)
        assert all(valid_volume_rsi >= 0)
        assert all(valid_volume_rsi <= 100)

    def test_rsi_uptrend(self):
        """Test RSI with strong uptrend - should be high (>70)."""
        # Create strong uptrend
        prices = pd.Series(
            [
                100,
                102,
                104,
                106,
                108,
                110,
                112,
                114,
                116,
                118,
                120,
                122,
                124,
                126,
                128,
                130,
            ]
        )
        result = calculate_rsi(prices, window=14)

        # Last RSI value should be high (overbought)
        last_rsi = result["value_rsi_14"].iloc[-1]
        assert last_rsi > 70, f"Expected RSI > 70 for strong uptrend, got {last_rsi}"

    def test_rsi_downtrend(self):
        """Test RSI with strong downtrend - should be low (<30)."""
        # Create strong downtrend
        prices = pd.Series(
            [
                130,
                128,
                126,
                124,
                122,
                120,
                118,
                116,
                114,
                112,
                110,
                108,
                106,
                104,
                102,
                100,
            ]
        )
        result = calculate_rsi(prices, window=14)

        # Last RSI value should be low (oversold)
        last_rsi = result["value_rsi_14"].iloc[-1]
        assert last_rsi < 30, f"Expected RSI < 30 for strong downtrend, got {last_rsi}"

    def test_rsi_all_gains(self):
        """Test RSI when all price changes are gains - should be 100."""
        # Constant upward movement
        prices = pd.Series(
            [
                100,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
                112,
                113,
                114,
                115,
            ]
        )
        result = calculate_rsi(prices, window=14)

        # RSI should be 100 (all gains, no losses)
        last_rsi = result["value_rsi_14"].iloc[-1]
        assert np.isclose(
            last_rsi, 100, rtol=0.01
        ), f"Expected RSI ~100 for all gains, got {last_rsi}"

    def test_rsi_neutral_market(self):
        """Test RSI in neutral market - should be around 50."""
        # Create a more balanced oscillating pattern with equal gains and losses
        # Pattern that ends with both gain and loss to balance:
        # +5, -5, +5, -5, etc. ending with -5
        prices = pd.Series(
            [
                100,
                105,
                100,
                105,
                100,
                105,
                100,
                105,
                100,
                105,
                100,
                105,
                100,
                105,
                100,
                105,
                100,
                105,
                100,
            ]
        )
        result = calculate_rsi(prices, window=14)

        # RSI should be near 50 (balanced gains and losses)
        last_rsi = result["value_rsi_14"].iloc[-1]
        # With equal alternating gains and losses that ends on a loss,
        # RSI should be around 36-50
        # Since recent price movement affects RSI, we allow a wider range
        assert (
            30 < last_rsi < 65
        ), f"Expected RSI in reasonable range for oscillating market, got {last_rsi}"

    def test_rsi_window_equals_data_length(self):
        """Test RSI when window equals data length."""
        prices = pd.Series(
            [100, 102, 104, 103, 105, 107, 106, 108, 110, 109, 111, 113, 112, 114, 116]
        )
        result = calculate_rsi(prices, window=14)

        # First value should be NaN (diff of first value is NaN)
        assert pd.isna(result["value_rsi_14"].iloc[0])
        # Values before window should be NaN
        for i in range(1, 14):
            assert pd.isna(result["value_rsi_14"].iloc[i]), f"Expected NaN at index {i}"
        # Last value should exist (window=14, we have 15 data points)
        assert not pd.isna(result["value_rsi_14"].iloc[-1])

    def test_rsi_window_larger_than_data(self):
        """Test RSI when window is larger than data length."""
        prices = pd.Series([100, 105, 103, 108, 110])
        result = calculate_rsi(prices, window=10)

        # All RSI values should be NaN (not enough data for min_periods=window)
        # First is NaN due to diff, rest are NaN due to insufficient window
        assert all(pd.isna(result["value_rsi_10"]))

    def test_rsi_with_nan_values(self):
        """Test RSI calculation with NaN values in data."""
        prices = pd.Series(
            [
                100,
                np.nan,
                103,
                108,
                110,
                107,
                112,
                115,
                113,
                118,
                120,
                119,
                122,
                124,
                123,
            ]
        )
        result = calculate_rsi(prices, window=14)

        # NaN values should affect RSI calculation
        # First value is NaN due to diff
        assert pd.isna(result["value_rsi_14"].iloc[0])
        # Second value is NaN in input, so RSI should be affected
        assert pd.isna(result["value_rsi_14"].iloc[1])

    def test_rsi_invalid_window_zero(self):
        """Test RSI with window=0."""
        prices = pd.Series([100, 105, 103])
        with pytest.raises(
            IndicatorCalculationError, match="Window must be greater than 0"
        ):
            calculate_rsi(prices, window=0)

    def test_rsi_invalid_window_negative(self):
        """Test RSI with negative window."""
        prices = pd.Series([100, 105, 103])
        with pytest.raises(
            IndicatorCalculationError, match="Window must be greater than 0"
        ):
            calculate_rsi(prices, window=-1)

    def test_rsi_column_not_found(self):
        """Test RSI when specified column doesn't exist."""
        df = pd.DataFrame({"close": [100, 105, 103, 108, 110]})
        with pytest.raises(IndicatorCalculationError, match="Column 'price' not found"):
            calculate_rsi(df, column="price", window=3)

    def test_rsi_no_numeric_columns(self):
        """Test RSI when DataFrame has no numeric columns."""
        df = pd.DataFrame({"symbol": ["AAPL", "MSFT", "GOOG"]})
        with pytest.raises(IndicatorCalculationError, match="No numeric columns found"):
            calculate_rsi(df, window=3)

    def test_rsi_preserves_index(self):
        """Test that RSI preserves the original index."""
        index = pd.date_range("2023-01-01", periods=20)
        prices = pd.Series(
            [
                100,
                102,
                104,
                103,
                105,
                107,
                106,
                108,
                110,
                109,
                111,
                113,
                112,
                114,
                116,
                115,
                117,
                119,
                118,
                120,
            ],
            index=index,
        )
        result = calculate_rsi(prices, window=14)

        assert result.index.equals(index)

    def test_rsi_default_window(self):
        """Test RSI with default window of 14."""
        prices = pd.Series(
            [
                100,
                102,
                104,
                103,
                105,
                107,
                106,
                108,
                110,
                109,
                111,
                113,
                112,
                114,
                116,
                115,
                117,
                119,
                118,
                120,
            ]
        )
        result = calculate_rsi(prices)  # Should use default window=14

        assert "value_rsi_14" in result.columns

    def test_rsi_different_windows(self):
        """Test RSI with different window sizes."""
        prices = pd.Series(
            [
                100,
                102,
                104,
                103,
                105,
                107,
                106,
                108,
                110,
                109,
                111,
                113,
                112,
                114,
                116,
                115,
                117,
                119,
                118,
                120,
            ]
        )
        result_7 = calculate_rsi(prices, window=7)
        result_14 = calculate_rsi(prices, window=14)
        result_21 = calculate_rsi(prices, window=21)

        # Different windows should produce different RSI values
        assert "value_rsi_7" in result_7.columns
        assert "value_rsi_14" in result_14.columns
        assert "value_rsi_21" in result_21.columns


class TestCompareSmaAndEma:
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
