"""
Unit tests for the price history (ph) subprogram.
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
from click.testing import CliRunner

from duk.commands.ph import (
    PriceHistoryDownloader,
    process_price_data,
    aggregate_by_frequency,
    save_data,
    ph_command,
)


@pytest.fixture(autouse=True)
def set_fmp_api_key():
    """Set FMP_API_KEY environment variable for all tests."""
    # Reset the global config manager to ensure clean state
    import duk.config

    duk.config._config_manager = None

    with patch.dict(os.environ, {"FMP_API_KEY": "dummy_test_key"}):
        yield


class TestPriceHistoryDownloader:
    """Test the PriceHistoryDownloader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.downloader = PriceHistoryDownloader(
            use_cache=False
        )  # Disable cache for tests

        # Sample FMP price data response
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

        # Sample dividend data
        self.sample_dividend_data = [
            {
                "date": "2023-11-15",
                "dividend": 0.25,
            }
        ]

        # Sample split data
        self.sample_split_data = [
            {
                "date": "2023-10-15",
                "numerator": 2,
                "denominator": 1,
            }
        ]

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_download_price_data_success(self, mock_request):
        """Test successful price data download."""
        mock_request.return_value = self.sample_price_data

        result = self.downloader.download_price_data("AAPL")

        assert result == self.sample_price_data
        mock_request.assert_called_once()

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_download_price_data_with_date_range(self, mock_request):
        """Test price data download with date range."""
        mock_request.return_value = self.sample_price_data

        result = self.downloader.download_price_data(
            "AAPL", start_date="2023-11-01", end_date="2023-12-01"
        )

        assert result is not None
        mock_request.assert_called_once()

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_download_price_data_with_days(self, mock_request):
        """Test price data download with days parameter."""
        mock_request.return_value = self.sample_price_data

        result = self.downloader.download_price_data("AAPL", days=5)

        assert result is not None
        mock_request.assert_called_once()

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_download_price_data_failure(self, mock_request):
        """Test price data download failure."""
        mock_request.return_value = None

        result = self.downloader.download_price_data("INVALID")

        assert result is None

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_download_dividends_data_success(self, mock_request):
        """Test successful dividend data download."""
        mock_request.return_value = self.sample_dividend_data

        result = self.downloader.download_dividends_data("AAPL")

        assert result == self.sample_dividend_data
        mock_request.assert_called_once()

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_download_splits_data_success(self, mock_request):
        """Test successful split data download."""
        mock_request.return_value = self.sample_split_data

        result = self.downloader.download_splits_data("AAPL")

        assert result == self.sample_split_data
        mock_request.assert_called_once()

    def test_make_request_success(self):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None

        with patch.object(self.downloader.session, "get", return_value=mock_response):
            result = self.downloader._make_request("http://test.com", {"key": "value"})

        assert result == {"test": "data"}

    def test_make_request_failure(self):
        """Test API request failure."""
        with patch.object(
            self.downloader.session, "get", side_effect=Exception("Network error")
        ):
            result = self.downloader._make_request("http://test.com", {"key": "value"})

        assert result is None

    def test_filter_by_date_range(self):
        """Test date range filtering."""
        data = [
            {"date": "2023-11-01"},
            {"date": "2023-11-15"},
            {"date": "2023-12-01"},
        ]

        result = self.downloader._filter_by_date_range(data, "2023-11-10", "2023-11-30")

        assert len(result) == 1
        assert result[0]["date"] == "2023-11-15"


class TestGetTickersFromInput:
    """Test ticker input parsing - these tests are now deprecated as ticker input
    has changed from file/single ticker to multiple arguments."""

    def test_single_ticker_now_via_cli(self):
        """Test single ticker input via CLI arguments."""
        # This functionality is now handled by Click's argument handling
        # Test moved to CLI tests
        pass

    def test_multiple_tickers_now_via_cli(self):
        """Test multiple ticker input via CLI arguments."""
        # This functionality is now handled by Click's argument handling
        # Test moved to CLI tests
        pass


class TestProcessPriceData:
    """Test price data processing."""

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

    def test_process_basic_price_data(self):
        """Test basic price data processing."""
        result = process_price_data("AAPL", self.sample_price_data)

        assert not result.empty
        assert len(result) == 2
        assert list(result.columns) == [
            "symbol",
            "date",
            "open",
            "high",
            "low",
            "close",
        ]
        assert result["symbol"].iloc[0] == "AAPL"

    def test_process_with_custom_fields(self):
        """Test processing with custom fields."""
        result = process_price_data(
            "AAPL", self.sample_price_data, fields=["high", "low", "close"]
        )

        assert list(result.columns) == ["symbol", "date", "high", "low", "close"]

    def test_process_with_volume(self):
        """Test processing with volume."""
        result = process_price_data(
            "AAPL", self.sample_price_data, fields=["close", "volume"]
        )

        assert "volume" in result.columns
        # Data is sorted by date, so first record is the earliest date (2023-11-30)
        assert result["volume"].iloc[0] == 900000

    def test_process_empty_data(self):
        """Test processing empty data."""
        result = process_price_data("AAPL", [])

        assert result.empty

    def test_process_with_dividends(self):
        """Test processing with dividend data."""
        dividend_data = [{"date": "2023-12-01", "dividend": 0.25}]

        result = process_price_data(
            "AAPL",
            self.sample_price_data,
            dividends_data=dividend_data,
            fields=["close", "dividend"],
        )

        assert "dividend" in result.columns
        assert result[result["date"] == "2023-12-01"]["dividend"].iloc[0] == 0.25

    def test_process_with_splits(self):
        """Test processing with split data."""
        split_data = [{"date": "2023-12-01", "numerator": 2, "denominator": 1}]

        result = process_price_data(
            "AAPL",
            self.sample_price_data,
            splits_data=split_data,
            fields=["close", "split"],
        )

        assert "split" in result.columns
        assert result[result["date"] == "2023-12-01"]["split"].iloc[0] == 2.0

    def test_process_with_adjusted_prices(self):
        """Test processing with adjusted prices."""
        result = process_price_data(
            "AAPL",
            self.sample_price_data,
            fields=["close", "adjusted_close"],
            calculate_adjusted=True,
        )

        assert "adjusted_close" in result.columns


class TestAggregateByFrequency:
    """Test frequency aggregation."""

    def setup_method(self):
        """Set up test fixtures."""
        dates = pd.date_range(start="2023-01-01", periods=30, freq="D")
        self.df = pd.DataFrame(
            {
                "symbol": "AAPL",
                "date": dates,
                "open": range(100, 130),
                "high": range(105, 135),
                "low": range(95, 125),
                "close": range(102, 132),
                "volume": range(1000000, 1030000, 1000),
            }
        )

    def test_daily_frequency(self):
        """Test daily frequency (should return unchanged)."""
        result = aggregate_by_frequency(self.df, "daily")
        assert len(result) == len(self.df)

    def test_weekly_frequency(self):
        """Test weekly frequency aggregation."""
        result = aggregate_by_frequency(self.df, "weekly")
        assert len(result) < len(self.df)
        assert len(result) >= 4  # At least 4 weeks in 30 days

    def test_monthly_frequency(self):
        """Test monthly frequency aggregation."""
        result = aggregate_by_frequency(self.df, "monthly")
        assert len(result) == 1  # Only one month

    def test_unknown_frequency(self):
        """Test unknown frequency (should return unchanged)."""
        result = aggregate_by_frequency(self.df, "unknown")
        assert len(result) == len(self.df)

    def test_empty_dataframe(self):
        """Test aggregation with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = aggregate_by_frequency(empty_df, "weekly")
        assert result.empty


class TestSaveData:
    """Test data saving functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_df = pd.DataFrame(
            {
                "symbol": ["AAPL", "AAPL"],
                "date": pd.to_datetime(["2023-12-01", "2023-11-30"]),
                "close": [152.0, 150.0],
            }
        )

    def test_save_csv(self):
        """Test saving to CSV format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = "test_data.csv"
            save_data(self.sample_df, filename, "csv", tmpdir)

            output_path = Path(tmpdir) / filename
            assert output_path.exists()

            # Verify content
            loaded_df = pd.read_csv(output_path)
            assert len(loaded_df) == 2
            assert "symbol" in loaded_df.columns

    def test_save_json(self):
        """Test saving to JSON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = "test_data.json"
            save_data(self.sample_df, filename, "json", tmpdir)

            output_path = Path(tmpdir) / filename
            assert output_path.exists()

            # Verify content
            with open(output_path, "r") as f:
                data = json.load(f)
            assert len(data) == 2
            assert data[0]["symbol"] == "AAPL"

    def test_save_creates_directory(self):
        """Test that save_data creates missing directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = Path(tmpdir) / "nested" / "directory"
            filename = "test_data.csv"

            save_data(self.sample_df, filename, "csv", str(nested_dir))

            output_path = nested_dir / filename
            assert output_path.exists()


class TestPhCommandCLI:
    """Test the ph_command CLI interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
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

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_single_ticker_default_output(self, mock_download):
        """Test single ticker with default output (close only)."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(ph_command, ["AAPL", "--no-cache"])

        assert result.exit_code == 0
        # Should output CSV to stdout
        assert "symbol,date,close" in result.output
        assert "AAPL" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_single_ticker_ohlc(self, mock_download):
        """Test single ticker with OHLC flag."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(ph_command, ["AAPL", "--ohlc", "--no-cache"])

        assert result.exit_code == 0
        # Should include OHLC columns
        assert "open" in result.output
        assert "high" in result.output
        assert "low" in result.output
        assert "close" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_multiple_tickers(self, mock_download):
        """Test multiple tickers without combine."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(ph_command, ["AAPL", "MSFT", "--no-cache"])

        assert result.exit_code == 0
        # Should have multiple CSV outputs (separate for each ticker)
        assert "AAPL" in result.output
        assert "MSFT" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_multiple_tickers_combined(self, mock_download):
        """Test multiple tickers with combine flag."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(
            ph_command, ["AAPL", "MSFT", "--combine", "--no-cache"]
        )

        assert result.exit_code == 0
        # Should have single combined output
        assert "AAPL" in result.output
        assert "MSFT" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_num_records_option(self, mock_download):
        """Test --num-records option."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(ph_command, ["AAPL", "-n", "10", "--no-cache"])

        assert result.exit_code == 0

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_csv_output(self, mock_download):
        """Test CSV file output."""
        mock_download.return_value = self.sample_price_data

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(ph_command, ["AAPL", "--csv", "--no-cache"])

            assert result.exit_code == 0
            assert "Data saved to" in result.output
            # Check that a CSV file was created
            csv_files = list(Path("var").glob("*.csv"))
            assert len(csv_files) > 0

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_json_output(self, mock_download):
        """Test JSON file output."""
        mock_download.return_value = self.sample_price_data

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(ph_command, ["AAPL", "--json", "--no-cache"])

            assert result.exit_code == 0
            assert "Data saved to" in result.output
            # Check that a JSON file was created
            json_files = list(Path("var").glob("*.json"))
            assert len(json_files) > 0

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_no_close_flag(self, mock_download):
        """Test --no-close flag removes close from output."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(
            ph_command, ["AAPL", "--ohlc", "--no-close", "--no-cache"]
        )

        assert result.exit_code == 0
        # Should have open, high, low but not close
        assert "open" in result.output
        assert "high" in result.output
        assert "low" in result.output
        # Close column should not be in header
        output_lines = result.output.split("\n")
        header = output_lines[0] if output_lines else ""
        # The header should not have a standalone 'close' field
        # (it might have 'adjusted_close' but not 'close' by itself)
        fields = header.split(",")
        assert "close" not in fields

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_vol_flag(self, mock_download):
        """Test --vol flag appends volume."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(ph_command, ["AAPL", "--vol", "--no-cache"])

        assert result.exit_code == 0
        assert "volume" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_frequency_option(self, mock_download):
        """Test --frequency option."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(
            ph_command, ["AAPL", "--frequency", "weekly", "--no-cache"]
        )

        assert result.exit_code == 0

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_date_range(self, mock_download):
        """Test date range with start and end dates."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(
            ph_command,
            [
                "AAPL",
                "--start-date",
                "2023-11-01",
                "--end-date",
                "2023-12-01",
                "--no-cache",
            ],
        )

        assert result.exit_code == 0

    def test_csv_and_json_error(self):
        """Test that specifying both --csv and --json is an error."""
        result = self.runner.invoke(ph_command, ["AAPL", "--csv", "--json"])

        assert result.exit_code == 1
        assert "Cannot specify both --csv and --json" in result.output

    def test_no_tickers_error(self):
        """Test that no tickers provided is an error."""
        result = self.runner.invoke(ph_command, [])

        assert result.exit_code != 0

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_verbose_flag(self, mock_download):
        """Test --verbose flag enables logging to stdout."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(ph_command, ["AAPL", "--verbose", "--no-cache"])

        # Verbose should add logging output
        # We can't easily test the exact logging output, but we can verify
        # the command completes successfully
        assert result.exit_code == 0
