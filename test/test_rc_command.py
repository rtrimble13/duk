"""
Unit tests for rc command.
"""

import json
import os
import tempfile
from test.test_utils import verify_dataframe_precision

import pandas as pd
from click.testing import CliRunner

from duk.cli import main


class TestRcCommand:
    """Test cases for rc command functionality."""

    def test_rc_help(self):
        """Test rc command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["rc", "--help"])

        assert result.exit_code == 0
        assert "Compute returns from price data" in result.output
        assert "--input" in result.output
        assert "--simple" in result.output
        assert "--log" in result.output
        assert "--lookback" in result.output

    def test_rc_missing_input(self):
        """Test rc command without input file."""
        runner = CliRunner()
        result = runner.invoke(main, ["rc", "--simple"])

        assert result.exit_code != 0
        assert "input" in result.output.lower() or "missing" in result.output.lower()

    def test_rc_no_return_option(self):
        """Test rc command without any return calculation option."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file])

            assert result.exit_code == 1
            assert "At least one return calculation option" in result.output

    def test_rc_simple_returns(self):
        """Test computing simple returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple"])

            assert result.exit_code == 0
            assert "close_simple_ret" in result.output
            # Check that we have the date column
            assert "date" in result.output or "Date" in result.output

    def test_rc_log_returns(self):
        """Test computing log returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--log"])

            assert result.exit_code == 0
            assert "close_log_ret" in result.output

    def test_rc_price_differences(self):
        """Test computing price differences."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--diff"])

            assert result.exit_code == 0
            assert "close_diff" in result.output

    def test_rc_cumulative_simple_returns(self):
        """Test computing cumulative simple returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--cum-simple"])

            assert result.exit_code == 0
            assert "close_cum_simple" in result.output

    def test_rc_cumulative_log_returns(self):
        """Test computing cumulative log returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--cum-log"])

            assert result.exit_code == 0
            assert "close_cum_log" in result.output

    def test_rc_annualized_simple_returns(self):
        """Test computing annualized simple returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file with daily data
            dates = pd.date_range("2023-01-02", periods=10, freq="D")
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": dates,
                    "close": [100.0 + i for i in range(10)],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--annual-simple"])

            assert result.exit_code == 0
            assert "close_annual_simple" in result.output

    def test_rc_annualized_log_returns(self):
        """Test computing annualized log returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file with daily data
            dates = pd.date_range("2023-01-02", periods=10, freq="D")
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": dates,
                    "close": [100.0 + i for i in range(10)],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--annual-log"])

            assert result.exit_code == 0
            assert "close_annual_log" in result.output

    def test_rc_with_lookback(self):
        """Test computing returns with lookback period."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "--lookback", "2"]
            )

            assert result.exit_code == 0
            assert "close_simple_ret_l2" in result.output

    def test_rc_with_append(self):
        """Test including input price data in output."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "--append"]
            )

            assert result.exit_code == 0
            # Should have both close and close_simple_ret columns
            assert "close," in result.output or "close\n" in result.output
            assert "close_simple_ret" in result.output

    def test_rc_multiple_columns(self):
        """Test computing returns for multiple price columns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file with multiple columns
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "open": [99.0, 104.0, 102.0],
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple"])

            assert result.exit_code == 0
            assert "open_simple_ret" in result.output
            assert "close_simple_ret" in result.output

    def test_rc_json_input(self):
        """Test reading JSON input file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input JSON file
            input_file = os.path.join(tmpdir, "prices.json")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_json(input_file, orient="records", date_format="iso")

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple"])

            assert result.exit_code == 0
            assert "close_simple_ret" in result.output

    def test_rc_csv_output(self):
        """Test CSV output format."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple", "--csv"])

            assert result.exit_code == 0
            # CSV format has comma-separated values
            # Check that CSV output is present (may have logging before it)
            assert "close_simple_ret" in result.output
            assert "," in result.output  # CSV has commas

    def test_rc_json_output(self):
        """Test JSON output format."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple", "--json"])

            assert result.exit_code == 0
            # JSON format should be parseable
            # Find the JSON output (last line that starts with '[')
            lines = result.output.split("\n")
            json_line = None
            for line in lines:
                if line.strip().startswith("["):
                    json_line = line.strip()
                    break

            assert json_line is not None, "No JSON output found"
            try:
                data = json.loads(json_line)
                assert isinstance(data, list)
            except json.JSONDecodeError:
                assert False, f"Output is not valid JSON: {json_line}"

    def test_rc_output_to_file(self):
        """Test writing output to file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            output_file = os.path.join(tmpdir, "returns.csv")
            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "-o", output_file]
            )

            assert result.exit_code == 0
            assert os.path.exists(output_file)
            assert f"Data written to {output_file}" in result.output

            # Verify file contents
            output_df = pd.read_csv(output_file)
            assert "close_simple_ret" in output_df.columns

    def test_rc_quiet_mode(self):
        """Test quiet mode suppresses output."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "--quiet"]
            )

            assert result.exit_code == 0
            # Output should not contain data (only minimal output)
            assert "close_simple_ret" not in result.output

    def test_rc_quiet_mode_with_output_file(self):
        """Test quiet mode with output file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            output_file = os.path.join(tmpdir, "returns.csv")
            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "-o", output_file, "-q"]
            )

            assert result.exit_code == 0
            # Should not print data but should mention file was written
            assert os.path.exists(output_file)

    def test_rc_missing_date_column(self):
        """Test error when input lacks date column."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file without date column
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "timestamp": ["2023-01-02", "2023-01-03", "2023-01-04"],
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple"])

            assert result.exit_code == 1
            assert "date" in result.output.lower()

    def test_rc_empty_input_file(self):
        """Test error when input file is empty."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame()
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple"])

            assert result.exit_code == 1
            # Error could be either "no data" or "no columns to parse"
            assert (
                "no data" in result.output.lower()
                or "no columns" in result.output.lower()
            )

    def test_rc_no_numeric_columns(self):
        """Test error when input has no numeric columns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create CSV file with only text columns
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "symbol": ["AAPL", "AAPL", "AAPL"],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple"])

            assert result.exit_code == 1
            assert "numeric" in result.output.lower()

    def test_rc_csv_and_json_mutually_exclusive(self):
        """Test that --csv and --json cannot be used together."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "--csv", "--json"]
            )

            assert result.exit_code == 1
            assert "Only one" in result.output

    def test_rc_multiple_return_types(self):
        """Test computing multiple return types at once."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "--log", "--diff"]
            )

            assert result.exit_code == 0
            assert "close_simple_ret" in result.output
            assert "close_log_ret" in result.output
            assert "close_diff" in result.output

    def test_rc_infer_daily_frequency(self):
        """Test inferring daily frequency for annualized returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input with daily data
            dates = pd.date_range("2023-01-02", periods=5, freq="D")
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": dates,
                    "close": [100.0, 101.0, 102.0, 103.0, 104.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--annual-simple"])

            assert result.exit_code == 0
            assert "close_annual_simple" in result.output

    def test_rc_infer_monthly_frequency(self):
        """Test inferring monthly frequency for annualized returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input with monthly data
            dates = pd.date_range("2023-01-01", periods=5, freq="MS")
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": dates,
                    "close": [100.0, 101.0, 102.0, 103.0, 104.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--annual-simple"])

            assert result.exit_code == 0
            assert "close_annual_simple" in result.output

    def test_rc_verbose_mode(self):
        """Test verbose mode."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "--verbose"]
            )

            assert result.exit_code == 0
            # Verbose mode should not fail

    def test_rc_lookback_with_cumulative(self):
        """Test lookback with cumulative returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        [
                            "2023-01-02",
                            "2023-01-03",
                            "2023-01-04",
                            "2023-01-05",
                            "2023-01-06",
                        ]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0, 110.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["rc", "-i", input_file, "--cum-simple", "-l", "2"]
            )

            assert result.exit_code == 0
            assert "close_cum_simple_l2" in result.output

    def test_rc_lookback_with_annualized(self):
        """Test lookback with annualized returns."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input with daily data
            dates = pd.date_range("2023-01-02", periods=10, freq="D")
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": dates,
                    "close": [100.0 + i for i in range(10)],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["rc", "-i", input_file, "--annual-simple", "-l", "2"]
            )

            assert result.exit_code == 0
            assert "close_annual_simple_l2" in result.output

    def test_rc_case_insensitive_date_column(self):
        """Test that Date column (different case) is recognized."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file with 'Date' column
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "Date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["rc", "-i", input_file, "--simple"])

            assert result.exit_code == 0
            assert "close_simple_ret" in result.output

    def test_rc_precision_default(self):
        """Test default precision (3 decimal places) for rc command."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input with values that will generate many decimal places
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.123456789, 105.987654321, 103.456789012],
                }
            )
            df.to_csv(input_file, index=False)

            # Run without specifying precision (should use default of 3)
            result = runner.invoke(main, ["rc", "-i", input_file, "--simple"])

            assert result.exit_code == 0
            # Check that output has 3 decimal places max
            # The return values should be rounded to 3 decimals
            # Parse CSV output to check precision
            import csv
            from io import StringIO

            csv_data = StringIO(result.output.strip())
            reader = csv.DictReader(csv_data)
            for row in reader:
                if "close_simple_ret" in row and row["close_simple_ret"] != "":
                    value = float(row["close_simple_ret"])
                    # Check that the value has at most 3 decimal places
                    # by verifying round(value, 3) == value
                    assert round(value, 3) == value

    def test_rc_precision_custom(self):
        """Test custom precision for rc command."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input with values that will generate many decimal places
            input_file = os.path.join(tmpdir, "prices.csv")
            output_file = os.path.join(tmpdir, "output.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.123456789, 105.987654321, 103.456789012],
                }
            )
            df.to_csv(input_file, index=False)

            # Run with precision=2
            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "-p", "2", "-o", output_file]
            )

            assert result.exit_code == 0

            # Read output file and verify precision
            output_df = pd.read_csv(output_file)
            verify_dataframe_precision(output_df, 2)

    def test_rc_precision_zero(self):
        """Test precision=0 for rc command (integer rounding)."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input
            input_file = os.path.join(tmpdir, "prices.csv")
            output_file = os.path.join(tmpdir, "output.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
                    "close": [100.5, 105.7, 103.3],
                }
            )
            df.to_csv(input_file, index=False)

            # Run with precision=0
            result = runner.invoke(
                main, ["rc", "-i", input_file, "--simple", "-p", "0", "-o", output_file]
            )

            assert result.exit_code == 0

            # Read output file and verify precision
            output_df = pd.read_csv(output_file)
            verify_dataframe_precision(output_df, 0)
