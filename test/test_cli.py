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

        result = self.runner.invoke(main, ["tr", "--date", "2023-12-01"])

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
        # Only provide 2 data points - insufficient for cubic spline
        insufficient_data = [
            {
                "record_date": "2023-12-01",
                "1_yr": "4.95",
                "10_yr": "4.45",
            }
        ]

        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},
            {"data": insufficient_data},
        ]

        result = self.runner.invoke(main, ["tr", "--interpolate"])

        assert result.exit_code == 1
        assert (
            "Interpolation failed" in result.output
            or "Not enough valid data points" in result.output
        )

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
