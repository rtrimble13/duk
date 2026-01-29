"""
Unit tests for plier command.
"""

import os
import tempfile

import pandas as pd
from click.testing import CliRunner

from duk.cli import main


class TestPlierCommand:
    """Test cases for plier command functionality."""

    def test_plier_help(self):
        """Test plier command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["plier", "--help"])

        assert result.exit_code == 0
        assert "Perform data manipulation" in result.output
        assert "--grab" in result.output
        assert "--strip" in result.output
        assert "--join" in result.output
        assert "--cut" in result.output

    def test_plier_missing_input(self):
        """Test plier command without input file."""
        runner = CliRunner()
        result = runner.invoke(main, ["plier", "--grab", "close"])

        assert result.exit_code != 0

    def test_plier_no_operation(self):
        """Test plier command without any operation."""
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

            result = runner.invoke(main, ["plier", "-i", input_file])

            assert result.exit_code == 1
            assert "At least one operation" in result.output

    def test_plier_grab_and_strip_mutual_exclusion(self):
        """Test that grab and strip cannot be used together."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "open": [99.0, 104.0],
                    "close": [100.0, 105.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["plier", "-i", input_file, "--grab", "close", "--strip", "open"]
            )

            assert result.exit_code == 1
            assert "cannot be used together" in result.output

    def test_plier_grab_by_column_names(self):
        """Test grabbing columns by name."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "open": [99.0, 104.0],
                    "close": [100.0, 105.0],
                    "volume": [1000, 1100],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["plier", "-i", input_file, "--grab", "close,volume"])

            assert result.exit_code == 0
            assert "date" in result.output
            assert "close" in result.output
            assert "volume" in result.output
            assert "open" not in result.output

    def test_plier_grab_by_positive_indices(self):
        """Test grabbing columns by positive indices."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "open": [99.0, 104.0],
                    "close": [100.0, 105.0],
                    "volume": [1000, 1100],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["plier", "-i", input_file, "--grab", "2,3"])

            assert result.exit_code == 0
            assert "close" in result.output
            assert "volume" in result.output

    def test_plier_grab_by_negative_indices(self):
        """Test grabbing columns by negative indices."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "open": [99.0, 104.0],
                    "close": [100.0, 105.0],
                    "volume": [1000, 1100],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["plier", "-i", input_file, "--grab", "-2,-1"])

            assert result.exit_code == 0
            assert "close" in result.output
            assert "volume" in result.output

    def test_plier_strip_by_column_names(self):
        """Test stripping columns by name."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "open": [99.0, 104.0],
                    "close": [100.0, 105.0],
                    "volume": [1000, 1100],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["plier", "-i", input_file, "--strip", "open,volume"])

            assert result.exit_code == 0
            assert "date,close" in result.output
            # Ensure open and volume are not in the data columns
            lines = [line for line in result.output.split("\n") if not line.startswith("202")]  # Filter log lines
            csv_output = "\n".join(lines)
            assert ",open" not in csv_output and "open," not in csv_output
            assert ",volume" not in csv_output and "volume," not in csv_output

    def test_plier_strip_by_indices(self):
        """Test stripping columns by indices."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "open": [99.0, 104.0],
                    "close": [100.0, 105.0],
                    "volume": [1000, 1100],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["plier", "-i", input_file, "--strip", "1,3"])

            assert result.exit_code == 0
            assert "date" in result.output
            assert "close" in result.output

    def test_plier_join_two_files(self):
        """Test joining two files."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first CSV file
            file1 = os.path.join(tmpdir, "prices1.csv")
            df1 = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0],
                }
            )
            df1.to_csv(file1, index=False)

            # Create second CSV file
            file2 = os.path.join(tmpdir, "prices2.csv")
            df2 = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "volume": [1000, 1100],
                }
            )
            df2.to_csv(file2, index=False)

            result = runner.invoke(main, ["plier", "-i", file1, "-i", file2, "--join"])

            assert result.exit_code == 0
            assert "date" in result.output
            assert "close" in result.output
            assert "volume" in result.output

    def test_plier_join_three_files(self):
        """Test joining three files."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create three CSV files
            file1 = os.path.join(tmpdir, "prices1.csv")
            df1 = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0],
                }
            )
            df1.to_csv(file1, index=False)

            file2 = os.path.join(tmpdir, "prices2.csv")
            df2 = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "volume": [1000, 1100],
                }
            )
            df2.to_csv(file2, index=False)

            file3 = os.path.join(tmpdir, "prices3.csv")
            df3 = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "open": [99.0, 104.0],
                }
            )
            df3.to_csv(file3, index=False)

            result = runner.invoke(
                main, ["plier", "-i", file1, "-i", file2, "-i", file3, "--join"]
            )

            assert result.exit_code == 0
            assert "close" in result.output
            assert "volume" in result.output
            assert "open" in result.output

    def test_plier_join_requires_multiple_files(self):
        """Test that join requires at least 2 files."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create single CSV file
            file1 = os.path.join(tmpdir, "prices.csv")
            df1 = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0],
                }
            )
            df1.to_csv(file1, index=False)

            result = runner.invoke(main, ["plier", "-i", file1, "--join"])

            assert result.exit_code == 1
            assert "at least 2 input files" in result.output

    def test_plier_cut_positive(self):
        """Test cutting rows from the start."""
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

            result = runner.invoke(main, ["plier", "-i", input_file, "--cut", "2"])

            assert result.exit_code == 0
            # Should have 2 rows remaining (4 - 2)
            # Filter out log lines (they contain " - duk" pattern)
            data_lines = [line for line in result.output.strip().split("\n") if " - duk" not in line]
            # Header + 2 data rows = 3 lines
            assert len(data_lines) == 3

    def test_plier_cut_negative(self):
        """Test cutting rows from the end."""
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

            result = runner.invoke(main, ["plier", "-i", input_file, "--cut", "-2"])

            assert result.exit_code == 0
            # Should have 2 rows remaining (4 - 2)
            # Filter out log lines (they contain " - duk" pattern)
            data_lines = [line for line in result.output.strip().split("\n") if " - duk" not in line]
            # Header + 2 data rows = 3 lines
            assert len(data_lines) == 3

    def test_plier_combined_operations(self):
        """Test combining join and cut operations."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two CSV files
            file1 = os.path.join(tmpdir, "prices1.csv")
            df1 = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df1.to_csv(file1, index=False)

            file2 = os.path.join(tmpdir, "prices2.csv")
            df2 = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
                    ),
                    "volume": [1000, 1100, 1050, 1150],
                }
            )
            df2.to_csv(file2, index=False)

            result = runner.invoke(
                main, ["plier", "-i", file1, "-i", file2, "--join", "--cut", "2"]
            )

            assert result.exit_code == 0
            assert "close" in result.output
            assert "volume" in result.output
            # Should have 2 rows remaining (4 - 2)
            # Filter out log lines (they contain " - duk" pattern)
            data_lines = [line for line in result.output.strip().split("\n") if " - duk" not in line]
            assert len(data_lines) == 3  # Header + 2 data rows

    def test_plier_output_to_file(self):
        """Test writing output to file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "open": [99.0, 104.0],
                    "close": [100.0, 105.0],
                }
            )
            df.to_csv(input_file, index=False)

            output_file = os.path.join(tmpdir, "result.csv")

            result = runner.invoke(
                main, ["plier", "-i", input_file, "--grab", "close", "-o", output_file]
            )

            assert result.exit_code == 0
            assert os.path.exists(output_file)

            # Verify output file content
            result_df = pd.read_csv(output_file)
            assert "date" in result_df.columns
            assert "close" in result_df.columns
            assert "open" not in result_df.columns

    def test_plier_json_input(self):
        """Test reading JSON input."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input JSON file
            input_file = os.path.join(tmpdir, "prices.json")
            df = pd.DataFrame(
                {
                    "date": ["2023-01-02", "2023-01-03"],
                    "close": [100.0, 105.0],
                    "volume": [1000, 1100],
                }
            )
            df.to_json(input_file, orient="records")

            result = runner.invoke(main, ["plier", "-i", input_file, "--grab", "close"])

            assert result.exit_code == 0
            assert "close" in result.output

    def test_plier_json_output(self):
        """Test JSON output format."""
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

            result = runner.invoke(main, ["plier", "-i", input_file, "--grab", "close", "--json"])

            assert result.exit_code == 0
            assert "[{" in result.output  # JSON array format

    def test_plier_quiet_flag(self):
        """Test quiet flag suppresses output."""
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

            output_file = os.path.join(tmpdir, "result.csv")

            result = runner.invoke(
                main,
                ["plier", "-i", input_file, "--grab", "close", "-o", output_file, "-q"],
            )

            assert result.exit_code == 0
            # With quiet flag, only file write message should be present
            assert "Data written to" in result.output
            # Data should not be printed
            assert "100.0" not in result.output or "date" not in result.output

    def test_plier_precision(self):
        """Test precision parameter."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV file with high precision values
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                    "close": [100.123456, 105.987654],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["plier", "-i", input_file, "--grab", "close", "-p", "2"]
            )

            assert result.exit_code == 0
            # Values should be rounded to 2 decimal places
            assert "100.12" in result.output
            assert "105.99" in result.output
