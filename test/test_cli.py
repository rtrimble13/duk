"""
Integration tests for the CLI functionality.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from duk.main import main


@pytest.fixture(autouse=True)
def set_fmp_api_key():
    """Set FMP_API_KEY environment variable for all tests."""
    # Reset the global config manager to ensure clean state
    import duk.config

    duk.config._config_manager = None

    with patch.dict(os.environ, {"FMP_API_KEY": "dummy_test_key"}):
        yield


class TestTreasuryCLI:
    """Integration tests for the treasury CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.sample_data = [
            {
                "record_date": "2023-12-01",
                "1_mo": "5.50",
                "2_mo": "5.40",
                "3_mo": "5.35",
                "1_yr": "4.95",
                "2_yr": "4.85",
                "10_yr": "4.45",
                "30_yr": "4.25",
            }
        ]

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_basic_command(self, mock_request):
        """Test basic tr command functionality."""
        # Mock the API calls
        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},  # get_latest_date
            {"data": self.sample_data},  # download_data
        ]

        result = self.runner.invoke(main, ["tr"])

        assert result.exit_code == 0
        assert "record_date" in result.output
        assert "2023-12-01" in result.output
        assert "5.5" in result.output

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_json_output(self, mock_request):
        """Test tr command with JSON output."""
        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": self.sample_data},
        ]

        result = self.runner.invoke(main, ["tr", "--format", "json"])

        assert result.exit_code == 0
        # Parse JSON output to verify structure
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["record_date"] == "2023-12-01"
        assert data[0]["1_mo"] == 5.50

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_file_output(self, mock_request):
        """Test tr command with file output."""
        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": self.sample_data},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(main, ["tr", "--output", "--directory", tmpdir])

            assert result.exit_code == 0
            assert "Data saved to" in result.output
            assert "treasury_par_yields_20231201.csv" in result.output

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_specific_date(self, mock_request):
        """Test tr command with specific date."""
        mock_request.return_value = {"data": self.sample_data}

        result = self.runner.invoke(main, ["tr", "--date", "2023-12-01", "--no-cache"])

        assert result.exit_code == 0
        assert "2023-12-01" in result.output

        # Verify correct API call was made
        expected_params = {"from": "2023-12-01", "to": "2023-12-01"}
        mock_request.assert_called_once_with(expected_params)

    def test_tr_invalid_date_combination(self):
        """Test tr command with invalid date combination."""
        result = self.runner.invoke(
            main, ["tr", "--date", "2023-12-01", "--start-date", "2023-11-01"]
        )

        assert result.exit_code == 1
        assert "Cannot specify --date with --start-date" in result.output

    def test_tr_help(self):
        """Test tr command help."""
        result = self.runner.invoke(main, ["tr", "--help"])

        assert result.exit_code == 0
        assert "Download treasury par yield curve rates" in result.output
        assert "--date" in result.output
        assert "--format" in result.output

    def test_main_help(self):
        """Test main command help."""
        result = self.runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "TurningBull Data Utility Knife" in result.output
        assert "tr" in result.output

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_interpolation_basic(self, mock_request):
        """Test tr command with basic interpolation."""
        # Use more complete sample data for interpolation
        complete_sample_data = [
            {
                "record_date": "2023-12-01",
                "1_mo": "5.50",
                "3_mo": "5.35",
                "6_mo": "5.15",
                "1_yr": "4.95",
                "2_yr": "4.85",
                "5_yr": "4.65",
                "10_yr": "4.45",
                "30_yr": "4.25",
            }
        ]

        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},  # get_latest_date
            {"data": complete_sample_data},  # download_data
        ]

        result = self.runner.invoke(main, ["tr", "--interpolate"])

        assert result.exit_code == 0
        assert "calendar_date" in result.output
        assert "maturity_years" in result.output
        assert "interpolated_rate" in result.output
        assert "2023-12-01" in result.output

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_interpolation_quarterly(self, mock_request):
        """Test tr command with quarterly interpolation."""
        complete_sample_data = [
            {
                "record_date": "2023-12-01",
                "1_mo": "5.50",
                "3_mo": "5.35",
                "6_mo": "5.15",
                "1_yr": "4.95",
                "2_yr": "4.85",
                "5_yr": "4.65",
                "10_yr": "4.45",
                "30_yr": "4.25",
            }
        ]

        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": complete_sample_data},
        ]

        result = self.runner.invoke(
            main, ["tr", "--interpolate", "--interpolate-interval", "quarter"]
        )

        assert result.exit_code == 0
        assert "calendar_date" in result.output
        assert "interpolated_rate" in result.output

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_interpolation_file_output(self, mock_request):
        """Test tr command with interpolation and file output."""
        complete_sample_data = [
            {
                "record_date": "2023-12-01",
                "1_mo": "5.50",
                "3_mo": "5.35",
                "6_mo": "5.15",
                "1_yr": "4.95",
                "2_yr": "4.85",
                "5_yr": "4.65",
                "10_yr": "4.45",
                "30_yr": "4.25",
            }
        ]

        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": complete_sample_data},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(
                main, ["tr", "--interpolate", "--output", "--directory", tmpdir]
            )

            assert result.exit_code == 0
            assert "Data saved to" in result.output
            assert (
                "treasury_par_yields_interpolated_semiannual_20231201.csv"
                in result.output
            )

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_interpolation_insufficient_data(self, mock_request):
        """Test tr command with interpolation when there's insufficient data."""
        # Only provide 1 data point - insufficient for any interpolation
        insufficient_data = [
            {
                "record_date": "2023-12-01",
                "1_yr": "4.95",
            }
        ]

        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": insufficient_data},
        ]

        result = self.runner.invoke(main, ["tr", "--interpolate", "--no-cache"])

        # Should exit with code 1 because no data could be interpolated
        assert result.exit_code == 1
        assert "No data could be interpolated" in result.output

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_bootstrap_spot_rates_basic(self, mock_request):
        """Test tr command with bootstrap spot rates flag."""
        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": self.sample_data},
        ]

        result = self.runner.invoke(main, ["tr", "--bootstrap-spot-rates"])

        assert result.exit_code == 0
        assert "interpolated_rate" in result.output
        assert "interpolated_spot_rate" in result.output
        assert "calendar_date" in result.output

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_bootstrap_spot_rates_with_interval(self, mock_request):
        """Test tr command with bootstrap spot rates and specific interval."""
        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": self.sample_data},
        ]

        result = self.runner.invoke(
            main, ["tr", "--bootstrap-spot-rates", "--interpolate-interval", "quarter"]
        )

        assert result.exit_code == 0
        assert "interpolated_rate" in result.output
        assert "interpolated_spot_rate" in result.output

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_bootstrap_spot_rates_file_output(self, mock_request):
        """Test tr command with bootstrap spot rates and file output."""
        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": self.sample_data},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(
                main,
                ["tr", "--bootstrap-spot-rates", "--output", "--directory", tmpdir],
            )

            assert result.exit_code == 0
            assert "Data saved to" in result.output
            assert "bootstrap" in result.output
            assert (
                "treasury_par_yields_interpolated_bootstrap_semiannual_20231201.csv"
                in result.output
            )

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_tr_bootstrap_spot_rates_json_output(self, mock_request):
        """Test tr command with bootstrap spot rates and JSON format."""
        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": self.sample_data},
        ]

        result = self.runner.invoke(
            main, ["tr", "--bootstrap-spot-rates", "--format", "json"]
        )

        assert result.exit_code == 0
        # Parse JSON to verify structure
        output_lines = result.output.strip().split("\n")
        json_output = "\n".join(output_lines)
        data = json.loads(json_output)

        assert isinstance(data, list)
        assert len(data) > 0
        assert "calendar_date" in data[0]
        assert "interpolated_rate" in data[0]
        assert "interpolated_spot_rate" in data[0]
        assert "maturity_years" in data[0]

    def test_man_page_exists(self):
        """Test that the man page file exists and has expected content."""
        from pathlib import Path

        # Get the project root directory
        project_root = Path(__file__).parent.parent
        man_page_path = project_root / "doc" / "duk.1"

        # Check that man page file exists
        assert man_page_path.exists(), f"Man page file not found at {man_page_path}"

        # Read and verify basic content
        with open(man_page_path, "r") as f:
            content = f.read()

        # Check for essential man page elements
        assert ".TH DUK 1" in content, "Man page header not found"
        assert ".SH NAME" in content, "NAME section not found"
        assert ".SH SYNOPSIS" in content, "SYNOPSIS section not found"
        assert ".SH DESCRIPTION" in content, "DESCRIPTION section not found"
        assert (
            "TurningBull Data Utility Knife" in content
        ), "Project description not found"
        assert "tr" in content, "TR subcommand not documented"
        assert "ph" in content, "PH subcommand not documented"


class TestPriceHistoryCLI:
    """Integration tests for the price history CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

        # Sample FMP price data response (direct list format)
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
    def test_ph_basic_command(self, mock_request):
        """Test basic ph command functionality."""
        mock_request.return_value = self.sample_price_data

        # Use explicit date range to avoid issues with current date
        result = self.runner.invoke(
            main,
            ["ph", "AAPL", "--start-date", "2023-11-01", "--end-date", "2023-12-01"],
        )

        assert result.exit_code == 0
        assert "symbol" in result.output
        assert "date" in result.output
        assert "AAPL" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_ph_json_output(self, mock_download):
        """Test ph command with JSON output."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(
            main,
            [
                "ph",
                "AAPL",
                "--start-date",
                "2023-11-01",
                "--end-date",
                "2023-12-01",
                "--no-cache",
            ],
        )

        assert result.exit_code == 0
        # Output is CSV by default to stdout
        assert "AAPL" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_ph_ohlcv_output(self, mock_download):
        """Test ph command with OHLC and volume output."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(
            main,
            [
                "ph",
                "AAPL",
                "--start-date",
                "2023-11-01",
                "--end-date",
                "2023-12-01",
                "--ohlc",
                "--vol",
                "--no-cache",
            ],
        )

        assert result.exit_code == 0
        assert "volume" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    @patch("duk.commands.ph.datetime")
    def test_ph_with_days(self, mock_datetime, mock_download):
        """Test ph command with num-records parameter."""
        from datetime import datetime

        mock_download.return_value = self.sample_price_data
        # Mock datetime.now to return a predictable date
        mock_datetime.now.return_value = datetime(2023, 12, 1)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        result = self.runner.invoke(
            main, ["ph", "AAPL", "--num-records", "2", "--no-cache"]
        )

        assert result.exit_code == 0
        assert "AAPL" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_ph_with_date_range(self, mock_request):
        """Test ph command with date range."""
        mock_request.return_value = self.sample_price_data

        result = self.runner.invoke(
            main,
            ["ph", "AAPL", "--start-date", "2023-01-01", "--end-date", "2023-12-31"],
        )

        assert result.exit_code == 0
        assert "AAPL" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_ph_file_output(self, mock_download):
        """Test ph command with file output."""
        mock_download.return_value = self.sample_price_data

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(
                main,
                [
                    "ph",
                    "AAPL",
                    "--start-date",
                    "2023-11-01",
                    "--end-date",
                    "2023-12-01",
                    "--csv",
                    "--directory",
                    tmpdir,
                    "--no-cache",
                ],
            )

            assert result.exit_code == 0
            assert "Data saved to" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader.download_price_data")
    def test_ph_multiple_tickers_file(self, mock_download):
        """Test ph command with multiple tickers."""
        mock_download.return_value = self.sample_price_data

        result = self.runner.invoke(
            main,
            [
                "ph",
                "AAPL",
                "MSFT",
                "--start-date",
                "2023-11-01",
                "--end-date",
                "2023-12-01",
                "--no-cache",
            ],
        )

        assert result.exit_code == 0
        assert "AAPL" in result.output
        assert "MSFT" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_ph_with_adjustments(self, mock_request):
        """Test ph command with dividend and split adjustments."""

        # Mock different API calls based on URL
        def mock_request_side_effect(url, params):
            if "historical-price-eod" in url:
                return self.sample_price_data
            elif "dividends" in url:
                return self.sample_dividend_data
            elif "splits" in url:
                return self.sample_split_data
            return None

        mock_request.side_effect = mock_request_side_effect

        result = self.runner.invoke(
            main,
            [
                "ph",
                "AAPL",
                "--start-date",
                "2023-11-01",
                "--end-date",
                "2023-12-01",
                "--adj",
                "--div",
                "--split",
            ],
        )

        assert result.exit_code == 0
        assert "adjusted_close" in result.output or "dividend" in result.output

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_ph_frequency_aggregation(self, mock_request):
        """Test ph command with frequency aggregation."""
        mock_request.return_value = self.sample_price_data

        result = self.runner.invoke(
            main,
            [
                "ph",
                "AAPL",
                "--start-date",
                "2023-11-01",
                "--end-date",
                "2023-12-01",
                "--frequency",
                "weekly",
            ],
        )

        assert result.exit_code == 0
        assert "AAPL" in result.output

    def test_ph_help(self):
        """Test ph command help."""
        result = self.runner.invoke(main, ["ph", "--help"])

        assert result.exit_code == 0
        assert "Download historical security price data" in result.output
        assert "TICKER" in result.output

    def test_ph_invalid_ticker_file(self):
        """Test ph command with invalid ticker file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("")  # Empty file
            f.flush()

            try:
                result = self.runner.invoke(main, ["ph", f.name])

                assert result.exit_code == 1
                assert "Error:" in result.output
            finally:
                os.unlink(f.name)

    @patch("duk.commands.ph.PriceHistoryDownloader._make_request")
    def test_ph_api_failure(self, mock_request):
        """Test ph command with API failure."""
        mock_request.return_value = None

        result = self.runner.invoke(main, ["ph", "INVALID"])

        assert result.exit_code == 1
        assert "Error:" in result.output
