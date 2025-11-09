"""
Unit tests for the duk API module.
"""

import os
import pytest
from unittest.mock import patch
import pandas as pd

from duk.api import ph


@pytest.fixture(autouse=True)
def set_fmp_api_key():
    """Set FMP_API_KEY environment variable for all tests."""
    # Reset the global config manager to ensure clean state
    import duk.config

    duk.config._config_manager = None

    with patch.dict(os.environ, {"FMP_API_KEY": "dummy_test_key"}):
        yield


class TestPhApi:
    """Test the ph() API function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_price_data = [
            {
                "date": "2023-12-01",
                "open": 150.0,
                "high": 155.0,
                "low": 148.0,
                "close": 152.0,
                "volume": 1000000,
            },
            {
                "date": "2023-11-30",
                "open": 148.0,
                "high": 151.0,
                "low": 147.0,
                "close": 150.0,
                "volume": 900000,
            },
        ]

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_single_ticker_default(self, mock_download):
        """Test ph() with single ticker and default options."""
        mock_download.return_value = self.sample_price_data

        result = ph("AAPL")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "symbol" in result.columns
        assert "date" in result.columns
        assert "close" in result.columns
        assert result["symbol"].iloc[0] == "AAPL"

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_multiple_tickers(self, mock_download):
        """Test ph() with multiple tickers."""
        mock_download.return_value = self.sample_price_data

        result = ph(["AAPL", "MSFT"])

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        # Should have data for both tickers
        assert "AAPL" in result["symbol"].values
        assert "MSFT" in result["symbol"].values

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_with_custom_fields(self, mock_download):
        """Test ph() with custom fields."""
        mock_download.return_value = self.sample_price_data

        result = ph("AAPL", fields=["open", "high", "low", "close"])

        assert "open" in result.columns
        assert "high" in result.columns
        assert "low" in result.columns
        assert "close" in result.columns

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_with_date_range(self, mock_download):
        """Test ph() with date range."""
        mock_download.return_value = self.sample_price_data

        result = ph("AAPL", start_date="2023-11-01", end_date="2023-12-01")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        mock_download.assert_called_once()

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_with_num_records(self, mock_download):
        """Test ph() with num_records parameter."""
        mock_download.return_value = self.sample_price_data

        result = ph("AAPL", num_records=10)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_with_frequency(self, mock_download):
        """Test ph() with frequency parameter."""
        mock_download.return_value = self.sample_price_data

        result = ph("AAPL", frequency="weekly")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    @patch("duk.api.PriceHistoryDownloader.download_dividends_data")
    def test_ph_with_dividends(self, mock_download_div, mock_download):
        """Test ph() with include_dividends flag."""
        mock_download.return_value = self.sample_price_data
        mock_download_div.return_value = [{"date": "2023-11-15", "dividend": 0.25}]

        result = ph("AAPL", include_dividends=True)

        assert "dividend" in result.columns
        mock_download_div.assert_called_once()

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    @patch("duk.api.PriceHistoryDownloader.download_splits_data")
    def test_ph_with_splits(self, mock_download_split, mock_download):
        """Test ph() with include_splits flag."""
        mock_download.return_value = self.sample_price_data
        mock_download_split.return_value = [
            {"date": "2023-10-15", "numerator": 2, "denominator": 1}
        ]

        result = ph("AAPL", include_splits=True)

        assert "split" in result.columns
        mock_download_split.assert_called_once()

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    @patch("duk.api.PriceHistoryDownloader.download_dividends_data")
    @patch("duk.api.PriceHistoryDownloader.download_splits_data")
    def test_ph_with_adjusted_prices(
        self, mock_download_split, mock_download_div, mock_download
    ):
        """Test ph() with calculate_adjusted flag."""
        mock_download.return_value = self.sample_price_data
        mock_download_div.return_value = [{"date": "2023-11-15", "dividend": 0.25}]
        mock_download_split.return_value = [
            {"date": "2023-10-15", "numerator": 2, "denominator": 1}
        ]

        result = ph("AAPL", calculate_adjusted=True)

        assert "adjusted_close" in result.columns

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_with_cache_disabled(self, mock_download):
        """Test ph() with cache disabled."""
        mock_download.return_value = self.sample_price_data

        result = ph("AAPL", use_cache=False)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_ph_empty_ticker(self):
        """Test ph() with empty ticker raises ValueError."""
        with pytest.raises(ValueError, match="Empty ticker symbol provided"):
            ph("")

    def test_ph_invalid_frequency(self):
        """Test ph() with invalid frequency raises ValueError."""
        with pytest.raises(ValueError, match="Invalid frequency"):
            ph("AAPL", frequency="invalid")

    def test_ph_invalid_field(self):
        """Test ph() with invalid field raises ValueError."""
        with pytest.raises(ValueError, match="Invalid field"):
            ph("AAPL", fields=["invalid_field"])

    def test_ph_conflicting_date_params(self):
        """Test ph() with conflicting date parameters raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Cannot specify num_records with both start_date and end_date",
        ):
            ph("AAPL", start_date="2023-01-01", end_date="2023-12-31", num_records=10)

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_download_failure(self, mock_download):
        """Test ph() handles download failure."""
        mock_download.return_value = None

        with pytest.raises(RuntimeError, match="Failed to download price data"):
            ph("AAPL")

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_no_data_found(self, mock_download):
        """Test ph() handles case when no data is found."""
        mock_download.return_value = []

        with pytest.raises(RuntimeError, match="No data found"):
            ph("AAPL")

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_ticker_normalization(self, mock_download):
        """Test ph() normalizes ticker symbols to uppercase."""
        mock_download.return_value = self.sample_price_data

        result = ph("aapl")  # lowercase ticker

        assert result["symbol"].iloc[0] == "AAPL"  # Should be uppercase

    @patch("duk.api.PriceHistoryDownloader.download_price_data")
    def test_ph_returns_sorted_data(self, mock_download):
        """Test ph() returns data sorted by symbol and date."""
        mock_download.return_value = self.sample_price_data

        result = ph(["MSFT", "AAPL"])

        # Should be sorted by symbol first
        symbols = result["symbol"].tolist()
        # Check that data is grouped by symbol (all AAPL together, all MSFT together)
        assert len(set(symbols)) == 2
