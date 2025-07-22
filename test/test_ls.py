"""
Unit tests for the ls subprogram.
"""

import tempfile
import json
import os
from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner

from duk.main import main
from duk.commands.ls import (
    FinancialListDownloader,
    format_index_data,
    format_basic_list_data,
    format_exchange_data,
    format_company_data,
)


class TestFinancialListDownloader:
    """Test cases for FinancialListDownloader class."""

    def setup_method(self):
        """Set up test case."""
        self.patcher = patch("duk.commands.ls.get_api_key")
        self.mock_get_api_key = self.patcher.start()
        self.mock_get_api_key.return_value = "test_api_key"

        with patch("duk.commands.ls.CacheManager"):
            self.downloader = FinancialListDownloader(use_cache=False)

    def teardown_method(self):
        """Clean up test case."""
        self.patcher.stop()

    @patch("duk.commands.ls.FinancialListDownloader._make_request")
    def test_get_index_list_success(self, mock_request):
        """Test successful index list retrieval."""
        mock_data = [
            {
                "symbol": "SPX",
                "name": "S&P 500",
                "exchange": "INDEX",
                "currency": "USD",
            },
            {
                "symbol": "DJI",
                "name": "Dow Jones",
                "exchange": "INDEX",
                "currency": "USD",
            },
            {
                "symbol": "FTSE",
                "name": "FTSE 100",
                "exchange": "INDEX",
                "currency": "GBP",
            },  # Should be filtered out
        ]
        mock_request.return_value = mock_data

        result = self.downloader.get_index_list()

        assert result is not None
        assert len(result) == 2  # Only USD currency records
        assert all(item["currency"] == "USD" for item in result)
        mock_request.assert_called_once_with("index-list")

    @patch("duk.commands.ls.FinancialListDownloader._make_request")
    def test_get_sector_list_success(self, mock_request):
        """Test successful sector list retrieval."""
        mock_data = ["Technology", "Healthcare", "Financials"]
        mock_request.return_value = mock_data

        result = self.downloader.get_sector_list()

        assert result == mock_data
        mock_request.assert_called_once_with("available-sectors")

    @patch("duk.commands.ls.FinancialListDownloader._make_request")
    def test_get_industry_list_success(self, mock_request):
        """Test successful industry list retrieval."""
        mock_data = ["Software", "Pharmaceuticals", "Banking"]
        mock_request.return_value = mock_data

        result = self.downloader.get_industry_list()

        assert result == mock_data
        mock_request.assert_called_once_with("available-industries")

    @patch("duk.commands.ls.FinancialListDownloader._make_request")
    def test_get_exchange_list_success(self, mock_request):
        """Test successful exchange list retrieval."""
        mock_data = [
            {"exchangeShortName": "NASDAQ", "name": "NASDAQ", "countryCode": "US"},
            {
                "exchangeShortName": "NYSE",
                "name": "New York Stock Exchange",
                "countryCode": "US",
            },
            {
                "exchangeShortName": "LSE",
                "name": "London Stock Exchange",
                "countryCode": "UK",
            },  # Should be filtered out
        ]
        mock_request.return_value = mock_data

        result = self.downloader.get_exchange_list()

        assert result is not None
        assert len(result) == 2  # Only US exchanges
        assert all(item["countryCode"] == "US" for item in result)
        mock_request.assert_called_once_with("available-exchanges")

    @patch("duk.commands.ls.FinancialListDownloader._make_request")
    @patch("duk.commands.ls.FinancialListDownloader.get_exchange_list")
    def test_get_etf_list_success(self, mock_get_exchanges, mock_request):
        """Test successful ETF list retrieval."""
        # Mock exchange data
        mock_get_exchanges.return_value = [
            {"exchangeShortName": "NASDAQ"},
            {"exchangeShortName": "NYSE"},
        ]

        # Mock ETF data
        mock_data = [
            {
                "symbol": "SPY",
                "companyName": "SPDR S&P 500",
                "exchangeShortName": "NYSE",
            },
            {
                "symbol": "QQQ",
                "companyName": "Invesco QQQ",
                "exchangeShortName": "NASDAQ",
            },
            {
                "symbol": "FOREIGN",
                "companyName": "Foreign ETF",
                "exchangeShortName": "LSE",
            },  # Should be filtered out
        ]
        mock_request.return_value = mock_data

        result = self.downloader.get_etf_list()

        assert result is not None
        assert len(result) == 2  # Only US exchange ETFs
        assert all(item["exchangeShortName"] in ["NYSE", "NASDAQ"] for item in result)
        mock_request.assert_called_once_with(
            "company-screener", {"country": "US", "isEtf": "true", "isFund": "false"}
        )

    @patch("duk.commands.ls.FinancialListDownloader._make_request")
    def test_get_stock_list_sp500(self, mock_request):
        """Test S&P 500 stock list retrieval."""
        mock_data = [
            {"symbol": "AAPL", "companyName": "Apple Inc.", "sector": "Technology"},
            {
                "symbol": "MSFT",
                "companyName": "Microsoft Corp.",
                "sector": "Technology",
            },
        ]
        mock_request.return_value = mock_data

        result = self.downloader.get_stock_list(sp500_only=True)

        assert result == mock_data
        mock_request.assert_called_once_with("sp500-constituent")

    @patch("duk.commands.ls.FinancialListDownloader._make_request")
    def test_get_stock_list_nasdaq(self, mock_request):
        """Test NASDAQ 100 stock list retrieval."""
        mock_data = [
            {"symbol": "AAPL", "companyName": "Apple Inc.", "sector": "Technology"},
            {"symbol": "GOOGL", "companyName": "Alphabet Inc.", "sector": "Technology"},
        ]
        mock_request.return_value = mock_data

        result = self.downloader.get_stock_list(nasdaq_only=True)

        assert result == mock_data
        mock_request.assert_called_once_with("nasdaq-constituent")

    @patch("duk.commands.ls.FinancialListDownloader._make_request")
    def test_make_request_failure(self, mock_request):
        """Test handling of API request failure."""
        mock_request.return_value = None  # _make_request should return None on failure

        result = self.downloader.get_sector_list()
        assert result is None


class TestDataFormatting:
    """Test cases for data formatting functions."""

    def test_format_index_data(self):
        """Test index data formatting."""
        data = [
            {
                "symbol": "SPX",
                "name": "S&P 500",
                "exchange": "INDEX",
                "currency": "USD",
            },
            {
                "symbol": "DJI",
                "name": "Dow Jones",
                "exchange": "INDEX",
                "currency": "USD",
            },
        ]

        df = format_index_data(data)

        assert len(df) == 2
        assert list(df.columns) == ["symbol", "name", "exchange"]
        assert df.iloc[0]["symbol"] == "SPX"

    def test_format_basic_list_data_strings(self):
        """Test basic list formatting with string data."""
        data = ["Technology", "Healthcare", "Financials"]

        df = format_basic_list_data(data, "sector")

        assert len(df) == 3
        assert "sector" in df.columns
        assert df.iloc[0]["sector"] == "Technology"

    def test_format_basic_list_data_dicts(self):
        """Test basic list formatting with dictionary data."""
        data = [
            {"name": "Technology", "count": 100},
            {"name": "Healthcare", "count": 80},
        ]

        df = format_basic_list_data(data, "sector")

        assert len(df) == 2
        assert "name" in df.columns
        assert "count" in df.columns

    def test_format_company_data(self):
        """Test company data formatting."""
        data = [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corp.",
                "sector": "Technology",
                "industry": "Software",
            },
        ]

        df = format_company_data(data)

        assert len(df) == 2
        assert "symbol" in df.columns
        assert "companyName" in df.columns
        # Should handle both companyName and name fields
        assert df.iloc[1]["companyName"] == "Microsoft Corp."

    def test_format_empty_data(self):
        """Test formatting with empty data."""
        assert format_index_data([]).empty
        assert format_basic_list_data([], "test").empty
        assert format_exchange_data([]).empty
        assert format_company_data([]).empty


class TestLSCommand:
    """Integration tests for the ls CLI command."""

    def setup_method(self):
        """Set up test case."""
        self.runner = CliRunner()

    def test_ls_no_args(self):
        """Test ls command with no arguments."""
        result = self.runner.invoke(main, ["ls"])

        assert result.exit_code == 0
        assert "Available lists:" in result.output
        assert "index" in result.output
        assert "sector" in result.output
        assert "stock" in result.output

    def test_ls_help(self):
        """Test ls command help."""
        result = self.runner.invoke(main, ["ls", "--help"])

        assert result.exit_code == 0
        assert "List financial information" in result.output
        assert "--sp500" in result.output
        assert "--nasdaq" in result.output

    def test_ls_invalid_list_type(self):
        """Test ls command with invalid list type."""
        result = self.runner.invoke(main, ["ls", "invalid"])

        assert result.exit_code == 1
        assert "Unknown list type 'invalid'" in result.output

    def test_ls_sp500_without_stock(self):
        """Test --sp500 flag without stock list type."""
        result = self.runner.invoke(main, ["ls", "sector", "--sp500"])

        assert result.exit_code == 1
        assert (
            "--sp500 and --nasdaq options can only be used with 'stock'"
            in result.output
        )

    def test_ls_conflicting_filters(self):
        """Test conflicting --sp500 and --nasdaq flags."""
        result = self.runner.invoke(main, ["ls", "stock", "--sp500", "--nasdaq"])

        assert result.exit_code == 1
        assert "Cannot specify both --sp500 and --nasdaq filters" in result.output

    @patch("duk.commands.ls.FinancialListDownloader.get_sector_list")
    def test_ls_sector_success(self, mock_get_sectors):
        """Test successful sector listing."""
        mock_get_sectors.return_value = ["Technology", "Healthcare", "Financials"]

        result = self.runner.invoke(main, ["ls", "sector", "--no-cache"])

        assert result.exit_code == 0
        assert "Technology" in result.output

    @patch("duk.commands.ls.FinancialListDownloader.get_sector_list")
    def test_ls_sector_failure(self, mock_get_sectors):
        """Test sector listing with API failure."""
        mock_get_sectors.return_value = None

        result = self.runner.invoke(main, ["ls", "sector", "--no-cache"])

        assert result.exit_code == 1
        assert "Failed to download sector data" in result.output

    @patch("duk.commands.ls.FinancialListDownloader.get_stock_list")
    def test_ls_stock_sp500(self, mock_get_stocks):
        """Test stock listing with S&P 500 filter."""
        mock_data = [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "sector": "Technology",
                "industry": "Electronics",
            },
        ]
        mock_get_stocks.return_value = mock_data

        result = self.runner.invoke(main, ["ls", "stock", "--sp500", "--no-cache"])

        assert result.exit_code == 0
        assert "AAPL" in result.output
        mock_get_stocks.assert_called_once_with(sp500_only=True, nasdaq_only=False)

    @patch("duk.commands.ls.FinancialListDownloader.get_index_list")
    def test_ls_index_json_output(self, mock_get_index):
        """Test index listing with JSON output."""
        mock_data = [
            {"symbol": "SPX", "name": "S&P 500", "exchange": "INDEX"},
        ]
        mock_get_index.return_value = mock_data

        result = self.runner.invoke(
            main, ["ls", "index", "--format", "json", "--no-cache"]
        )

        assert result.exit_code == 0
        output_data = json.loads(result.output)
        assert len(output_data) == 1
        assert output_data[0]["symbol"] == "SPX"

    @patch("duk.commands.ls.FinancialListDownloader.get_sector_list")
    def test_ls_sector_file_output(self, mock_get_sectors):
        """Test sector listing with file output."""
        mock_get_sectors.return_value = ["Technology", "Healthcare"]

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                ["ls", "sector", "--output", "--directory", temp_dir, "--no-cache"],
            )

            assert result.exit_code == 0
            assert "Data saved to" in result.output

            # Check that file was created
            files = os.listdir(temp_dir)
            assert len(files) == 1
            assert files[0] == "sector_list.csv"
