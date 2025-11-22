"""Tests for CLI module."""

from io import StringIO
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from duk.cli import cmd_ph, create_parser, main


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_creation(self):
        """Test that parser is created correctly."""
        parser = create_parser()
        assert parser is not None

    def test_ph_command_parsing(self):
        """Test parsing of ph command arguments."""
        parser = create_parser()

        # Basic command
        args = parser.parse_args(["ph", "IBM"])
        assert args.command == "ph"
        assert args.symbol == "IBM"
        assert args.limit is None

        # With limit
        args = parser.parse_args(["ph", "IBM", "--limit", "10"])
        assert args.limit == 10

        # With date range
        args = parser.parse_args(
            ["ph", "IBM", "--from-date", "2024-01-01", "--to-date", "2024-01-31"]
        )
        assert args.from_date == "2024-01-01"
        assert args.to_date == "2024-01-31"

        # With fields
        args = parser.parse_args(["ph", "IBM", "--fields", "date", "close", "volume"])
        assert args.fields == ["date", "close", "volume"]

        # With output format
        args = parser.parse_args(["ph", "IBM", "--output-format", "csv"])
        assert args.output_format == "csv"

    def test_version_argument(self):
        """Test --version argument."""
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])

        assert exc_info.value.code == 0


class TestCmdPh:
    """Tests for cmd_ph function."""

    def test_successful_execution(self):
        """Test successful execution of ph command."""
        # Mock arguments
        args = Mock()
        args.symbol = "IBM"
        args.limit = 5
        args.from_date = None
        args.to_date = None
        args.fields = None
        args.output_format = "table"

        # Mock price history data
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                "close": [100.0, 101.0],
            }
        )

        with patch("duk.ph.get_price_history", return_value=mock_df):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                exit_code = cmd_ph(args)

                assert exit_code == 0
                output = mock_stdout.getvalue()
                assert "2024-01-01" in output
                assert "100.0" in output

    def test_csv_output_format(self):
        """Test CSV output format."""
        args = Mock()
        args.symbol = "IBM"
        args.limit = 5
        args.from_date = None
        args.to_date = None
        args.fields = None
        args.output_format = "csv"

        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        with patch("duk.ph.get_price_history", return_value=mock_df):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                exit_code = cmd_ph(args)

                assert exit_code == 0
                output = mock_stdout.getvalue()
                assert "date,close" in output or "date" in output

    def test_json_output_format(self):
        """Test JSON output format."""
        args = Mock()
        args.symbol = "IBM"
        args.limit = 5
        args.from_date = None
        args.to_date = None
        args.fields = None
        args.output_format = "json"

        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        with patch("duk.ph.get_price_history", return_value=mock_df):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                exit_code = cmd_ph(args)

                assert exit_code == 0
                output = mock_stdout.getvalue()
                assert '"date"' in output or '"close"' in output

    def test_empty_data(self):
        """Test handling of empty data."""
        args = Mock()
        args.symbol = "INVALID"
        args.limit = 5
        args.from_date = None
        args.to_date = None
        args.fields = None
        args.output_format = "table"

        mock_df = pd.DataFrame()

        with patch("duk.ph.get_price_history", return_value=mock_df):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                exit_code = cmd_ph(args)

                assert exit_code == 1
                error_output = mock_stderr.getvalue()
                assert "No data found" in error_output

    def test_value_error_handling(self):
        """Test handling of ValueError."""
        args = Mock()
        args.symbol = ""
        args.limit = 5
        args.from_date = None
        args.to_date = None
        args.fields = None
        args.output_format = "table"

        with patch(
            "duk.ph.get_price_history",
            side_effect=ValueError("Invalid symbol"),
        ):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                exit_code = cmd_ph(args)

                assert exit_code == 1
                error_output = mock_stderr.getvalue()
                assert "Error:" in error_output

    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors."""
        args = Mock()
        args.symbol = "IBM"
        args.limit = 5
        args.from_date = None
        args.to_date = None
        args.fields = None
        args.output_format = "table"

        with patch(
            "duk.ph.get_price_history",
            side_effect=Exception("Unexpected error"),
        ):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                exit_code = cmd_ph(args)

                assert exit_code == 1
                error_output = mock_stderr.getvalue()
                assert "Unexpected error:" in error_output


class TestMain:
    """Tests for main function."""

    def test_main_with_ph_command(self):
        """Test main function with ph command."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        test_args = ["duk", "ph", "IBM"]

        with patch("sys.argv", test_args):
            with patch("duk.ph.get_price_history", return_value=mock_df):
                with patch("sys.stdout", new_callable=StringIO):
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 0
