"""
Tests for FMP API module.
"""

import datetime as dt
from unittest import mock

import pytest
import requests

from duk.fmp_api import (
    FMPAPIError,
    adjusted_price_history_api,
    price_history_api,
    treasury_rates_api,
)


class TestPriceHistoryAPI:
    """Tests for price_history_api function."""

    def test_price_history_api_success(self):
        """Test successful API call with historical data."""
        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-03",
                    "open": 150.0,
                    "high": 155.0,
                    "low": 149.0,
                    "close": 154.0,
                    "volume": 1000000,
                },
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = price_history_api("AAPL", "test_api_key")

            assert len(result) == 2
            assert result[0]["date"] == "2023-01-03"
            assert result[0]["close"] == 154.0
            assert result[1]["date"] == "2023-01-02"

    def test_price_history_api_with_date_range(self):
        """Test API call with from and to dates."""
        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-06-01",
                    "open": 160.0,
                    "close": 162.0,
                }
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            from_date = dt.datetime.strptime("2023-06-01", "%Y-%m-%d")
            to_date = dt.datetime.strptime("2023-06-30", "%Y-%m-%d")

            result = price_history_api(
                "AAPL", "test_api_key", from_date=from_date, to_date=to_date
            )

            # Verify the correct parameters were passed
            call_args = mock_get.call_args
            assert call_args[1]["params"]["from"] == from_date.strftime("%Y-%m-%d")
            assert call_args[1]["params"]["to"] == to_date.strftime("%Y-%m-%d")
            assert len(result) == 1

    def test_price_history_api_empty_symbol(self):
        """Test that empty symbol raises ValueError."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            price_history_api("", "test_api_key")

    def test_price_history_api_empty_api_key(self):
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            price_history_api("AAPL", "")

    def test_price_history_api_network_error(self):
        """Test handling of network errors."""
        with mock.patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

            with pytest.raises(FMPAPIError, match="Failed to fetch price history"):
                price_history_api("AAPL", "test_api_key")

    def test_price_history_api_http_error(self):
        """Test handling of HTTP errors."""
        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            mock_get.return_value.raise_for_status.side_effect = (
                requests.exceptions.HTTPError("404 Not Found")
            )

            with pytest.raises(FMPAPIError, match="Failed to fetch price history"):
                price_history_api("AAPL", "test_api_key")

    def test_price_history_api_invalid_json(self):
        """Test handling of invalid JSON response."""
        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()
            mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

            with pytest.raises(FMPAPIError, match="Failed to parse JSON response"):
                price_history_api("AAPL", "test_api_key")

    def test_price_history_api_error_message_in_response(self):
        """Test handling of error message in API response."""
        mock_response = {"Error Message": "Invalid API key"}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            with pytest.raises(FMPAPIError, match="FMP API error"):
                price_history_api("AAPL", "test_api_key")

    def test_price_history_api_list_response(self):
        """Test handling of API response that returns a list directly."""
        mock_response = [
            {"date": "2023-01-03", "close": 154.0},
            {"date": "2023-01-02", "close": 150.0},
        ]

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = price_history_api("AAPL", "test_api_key")

            assert len(result) == 2
            assert result[0]["date"] == "2023-01-03"

    def test_price_history_api_empty_response(self):
        """Test handling of empty or unexpected response format."""
        mock_response = {}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = price_history_api("AAPL", "test_api_key")

            assert result == []

    def test_price_history_api_timeout(self):
        """Test handling of request timeout."""
        with mock.patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

            with pytest.raises(FMPAPIError, match="Failed to fetch price history"):
                price_history_api("AAPL", "test_api_key")

    def test_price_history_api_url_construction(self):
        """Test that the correct URL and parameters are used."""
        mock_response = {"symbol": "AAPL", "historical": []}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            price_history_api("AAPL", "test_api_key")

            # Verify the correct URL was called
            call_args = mock_get.call_args
            assert "historical-price-eod/full" in call_args[0][0]
            assert "symbol=AAPL" in call_args[0][0]
            assert call_args[1]["params"]["apikey"] == "test_api_key"
            assert call_args[1]["timeout"] == 30


class TestAdjustedPriceHistoryAPI:
    """Tests for adjusted_price_history_api function."""

    def test_adjusted_price_history_api_success(self):
        """Test successful API call with dividend-adjusted historical data."""
        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-03",
                    "open": 150.0,
                    "high": 155.0,
                    "low": 149.0,
                    "close": 154.0,
                    "volume": 1000000,
                },
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = adjusted_price_history_api("AAPL", "test_api_key")

            assert len(result) == 2
            assert result[0]["date"] == "2023-01-03"
            assert result[0]["close"] == 154.0
            assert result[1]["date"] == "2023-01-02"

    def test_adjusted_price_history_api_with_date_range(self):
        """Test API call with from and to dates."""
        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-06-01",
                    "open": 160.0,
                    "close": 162.0,
                }
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            from_date = dt.datetime.strptime("2023-06-01", "%Y-%m-%d")
            to_date = dt.datetime.strptime("2023-06-30", "%Y-%m-%d")

            result = adjusted_price_history_api(
                "AAPL",
                "test_api_key",
                from_date=from_date,
                to_date=to_date,
            )

            # Verify the correct parameters were passed
            call_args = mock_get.call_args
            assert call_args[1]["params"]["from"] == from_date.strftime("%Y-%m-%d")
            assert call_args[1]["params"]["to"] == to_date.strftime("%Y-%m-%d")
            assert len(result) == 1

    def test_adjusted_price_history_api_empty_symbol(self):
        """Test that empty symbol raises ValueError."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            adjusted_price_history_api("", "test_api_key")

    def test_adjusted_price_history_api_empty_api_key(self):
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            adjusted_price_history_api("AAPL", "")

    def test_adjusted_price_history_api_network_error(self):
        """Test handling of network errors."""
        with mock.patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

            with pytest.raises(
                FMPAPIError, match="Failed to fetch dividend-adjusted price history"
            ):
                adjusted_price_history_api("AAPL", "test_api_key")

    def test_adjusted_price_history_api_http_error(self):
        """Test handling of HTTP errors."""
        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            mock_get.return_value.raise_for_status.side_effect = (
                requests.exceptions.HTTPError("404 Not Found")
            )

            with pytest.raises(
                FMPAPIError, match="Failed to fetch dividend-adjusted price history"
            ):
                adjusted_price_history_api("AAPL", "test_api_key")

    def test_adjusted_price_history_api_invalid_json(self):
        """Test handling of invalid JSON response."""
        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()
            mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

            with pytest.raises(FMPAPIError, match="Failed to parse JSON response"):
                adjusted_price_history_api("AAPL", "test_api_key")

    def test_adjusted_price_history_api_error_message_in_response(self):
        """Test handling of error message in API response."""
        mock_response = {"Error Message": "Invalid API key"}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            with pytest.raises(FMPAPIError, match="FMP API error"):
                adjusted_price_history_api("AAPL", "test_api_key")

    def test_adjusted_price_history_api_list_response(self):
        """Test handling of API response that returns a list directly."""
        mock_response = [
            {"date": "2023-01-03", "close": 154.0},
            {"date": "2023-01-02", "close": 150.0},
        ]

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = adjusted_price_history_api("AAPL", "test_api_key")

            assert len(result) == 2
            assert result[0]["date"] == "2023-01-03"

    def test_adjusted_price_history_api_empty_response(self):
        """Test handling of empty or unexpected response format."""
        mock_response = {}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = adjusted_price_history_api("AAPL", "test_api_key")

            assert result == []

    def test_adjusted_price_history_api_timeout(self):
        """Test handling of request timeout."""
        with mock.patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

            with pytest.raises(
                FMPAPIError, match="Failed to fetch dividend-adjusted price history"
            ):
                adjusted_price_history_api("AAPL", "test_api_key")

    def test_adjusted_price_history_api_url_construction(self):
        """Test that the correct URL and parameters are used."""
        mock_response = {"symbol": "AAPL", "historical": []}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            adjusted_price_history_api("AAPL", "test_api_key")

            # Verify the correct URL was called
            call_args = mock_get.call_args
            assert "dividend-adjusted" in call_args[0][0]
            assert "symbol=AAPL" in call_args[0][0]
            assert call_args[1]["params"]["apikey"] == "test_api_key"
            assert call_args[1]["timeout"] == 30


class TestTreasuryRatesAPI:
    """Tests for treasury_rates_api function."""

    def test_treasury_rates_api_success(self):
        """Test successful API call with treasury rates data."""
        mock_response = [
            {
                "date": "2023-01-03",
                "month1": 4.35,
                "month2": 4.42,
                "month3": 4.45,
                "year1": 4.68,
                "year5": 3.94,
                "year10": 3.79,
                "year30": 3.88,
            },
            {
                "date": "2023-01-02",
                "month1": 4.30,
                "month2": 4.40,
                "month3": 4.43,
                "year1": 4.65,
                "year5": 3.90,
                "year10": 3.75,
                "year30": 3.85,
            },
        ]

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = treasury_rates_api("test_api_key")

            assert len(result) == 2
            assert result[0]["date"] == "2023-01-03"
            assert result[0]["year10"] == 3.79
            assert result[1]["date"] == "2023-01-02"

    def test_treasury_rates_api_with_date_range(self):
        """Test API call with from and to dates."""
        from datetime import date

        mock_response = [
            {
                "date": "2023-06-01",
                "month1": 5.25,
                "year10": 3.70,
            }
        ]

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = treasury_rates_api(
                "test_api_key",
                start_date=date(2023, 6, 1),
                end_date=date(2023, 6, 30),
            )

            # Verify the correct parameters were passed
            call_args = mock_get.call_args
            assert call_args[1]["params"]["from"] == "2023-06-01"
            assert call_args[1]["params"]["to"] == "2023-06-30"
            assert len(result) == 1

    def test_treasury_rates_api_empty_api_key(self):
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            treasury_rates_api("")

    def test_treasury_rates_api_network_error(self):
        """Test handling of network errors."""
        with mock.patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

            with pytest.raises(FMPAPIError, match="Failed to fetch treasury rates"):
                treasury_rates_api("test_api_key")

    def test_treasury_rates_api_http_error(self):
        """Test handling of HTTP errors."""
        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            mock_get.return_value.raise_for_status.side_effect = (
                requests.exceptions.HTTPError("404 Not Found")
            )

            with pytest.raises(FMPAPIError, match="Failed to fetch treasury rates"):
                treasury_rates_api("test_api_key")

    def test_treasury_rates_api_invalid_json(self):
        """Test handling of invalid JSON response."""
        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()
            mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

            with pytest.raises(FMPAPIError, match="Failed to parse JSON response"):
                treasury_rates_api("test_api_key")

    def test_treasury_rates_api_error_message_in_response(self):
        """Test handling of error message in API response."""
        mock_response = {"Error Message": "Invalid API key"}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            with pytest.raises(FMPAPIError, match="FMP API error"):
                treasury_rates_api("test_api_key")

    def test_treasury_rates_api_empty_response(self):
        """Test handling of empty list response."""
        mock_response = []

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = treasury_rates_api("test_api_key")

            assert result == []

    def test_treasury_rates_api_unexpected_response(self):
        """Test handling of unexpected response format."""
        mock_response = {}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = treasury_rates_api("test_api_key")

            assert result == []

    def test_treasury_rates_api_timeout(self):
        """Test handling of request timeout."""
        with mock.patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

            with pytest.raises(FMPAPIError, match="Failed to fetch treasury rates"):
                treasury_rates_api("test_api_key")

    def test_treasury_rates_api_url_construction(self):
        """Test that the correct URL and parameters are used."""
        mock_response = []

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            treasury_rates_api("test_api_key")

            # Verify the correct URL was called
            call_args = mock_get.call_args
            assert "treasury-rates" in call_args[0][0]
            assert call_args[1]["params"]["apikey"] == "test_api_key"
            assert call_args[1]["timeout"] == 30


class TestGetPriceHistory:
    """Tests for get_price_history function."""

    def test_get_price_history_basic(self):
        """Test basic usage without date range or limit."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
                {
                    "date": "2023-01-03",
                    "open": 150.0,
                    "high": 155.0,
                    "low": 149.0,
                    "close": 154.0,
                    "volume": 1000000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history("test_api_key", "AAPL")

            assert len(result) == 2
            assert result.index.name == "date"
            # Check that data is sorted ascending
            assert result.index[0].strftime("%Y-%m-%d") == "2023-01-02"
            assert result.index[1].strftime("%Y-%m-%d") == "2023-01-03"
            assert result.iloc[0]["close"] == 150.0
            assert result.iloc[1]["close"] == 154.0

    def test_get_price_history_with_date_range(self):
        """Test with start_date and end_date."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {"date": "2023-06-01", "close": 160.0},
                {"date": "2023-06-02", "close": 162.0},
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history(
                "test_api_key",
                "AAPL",
                start_date="2023-06-01",
                end_date="2023-06-30",
            )

            assert len(result) == 2
            # Verify dates were passed to API
            call_args = mock_get.call_args
            assert "from" in call_args[1]["params"]
            assert "to" in call_args[1]["params"]

    def test_get_price_history_with_start_date_and_limit(self):
        """Test with start_date and limit - should keep first N records."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {"date": "2023-01-01", "close": 150.0},
                {"date": "2023-01-02", "close": 151.0},
                {"date": "2023-01-03", "close": 152.0},
                {"date": "2023-01-04", "close": 153.0},
                {"date": "2023-01-05", "close": 154.0},
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history(
                "test_api_key", "AAPL", start_date="2023-01-01", limit=3
            )

            # Should keep first 3 records
            assert len(result) == 3
            assert result.index[0].strftime("%Y-%m-%d") == "2023-01-01"
            assert result.index[-1].strftime("%Y-%m-%d") == "2023-01-03"

    def test_get_price_history_with_end_date_and_limit(self):
        """Test with end_date and limit - should keep last N records."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {"date": "2023-01-01", "close": 150.0},
                {"date": "2023-01-02", "close": 151.0},
                {"date": "2023-01-03", "close": 152.0},
                {"date": "2023-01-04", "close": 153.0},
                {"date": "2023-01-05", "close": 154.0},
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history(
                "test_api_key", "AAPL", end_date="2023-01-05", limit=3
            )

            # Should keep last 3 records
            assert len(result) == 3
            assert result.index[0].strftime("%Y-%m-%d") == "2023-01-03"
            assert result.index[-1].strftime("%Y-%m-%d") == "2023-01-05"

    def test_get_price_history_weekly_resampling(self):
        """Test resampling to weekly frequency."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 103.0,
                    "volume": 1000,
                },
                {
                    "date": "2023-01-03",
                    "open": 103.0,
                    "high": 107.0,
                    "low": 102.0,
                    "close": 106.0,
                    "volume": 1100,
                },
                {
                    "date": "2023-01-09",
                    "open": 106.0,
                    "high": 110.0,
                    "low": 105.0,
                    "close": 109.0,
                    "volume": 1200,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history(
                "test_api_key",
                "AAPL",
                start_date="2023-01-01",
                end_date="2023-01-31",
                frequency="week",
            )

            # Should have resampled data
            assert len(result) >= 1
            assert "close" in result.columns

    def test_get_price_history_monthly_resampling(self):
        """Test resampling to monthly frequency."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 103.0,
                    "volume": 1000,
                },
                {
                    "date": "2023-01-15",
                    "open": 103.0,
                    "high": 107.0,
                    "low": 102.0,
                    "close": 106.0,
                    "volume": 1100,
                },
                {
                    "date": "2023-02-05",
                    "open": 106.0,
                    "high": 110.0,
                    "low": 105.0,
                    "close": 109.0,
                    "volume": 1200,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history(
                "test_api_key",
                "AAPL",
                start_date="2023-01-01",
                end_date="2023-02-28",
                frequency="month",
            )

            # Should have resampled data with monthly frequency
            assert len(result) >= 1

    def test_get_price_history_empty_response(self):
        """Test handling of empty API response."""
        from duk.fmp_api import get_price_history

        mock_response = {"symbol": "AAPL", "historical": []}

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history("test_api_key", "AAPL")

            assert len(result) == 0
            assert isinstance(result, __import__("pandas").DataFrame)

    def test_get_price_history_invalid_date_format(self):
        """Test handling of invalid date format."""
        from duk.fmp_api import get_price_history

        with pytest.raises(ValueError):
            get_price_history("test_api_key", "AAPL", start_date="invalid-date")

    def test_get_price_history_quarterly_resampling(self):
        """Test resampling to quarterly frequency."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {"date": "2023-01-02", "open": 100.0, "close": 103.0, "volume": 1000},
                {"date": "2023-02-15", "open": 103.0, "close": 106.0, "volume": 1100},
                {"date": "2023-04-05", "open": 106.0, "close": 109.0, "volume": 1200},
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history(
                "test_api_key",
                "AAPL",
                start_date="2023-01-01",
                end_date="2023-06-30",
                frequency="quarter",
            )

            assert len(result) >= 1

    def test_get_price_history_annual_resampling(self):
        """Test resampling to annual frequency."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {"date": "2022-01-02", "open": 100.0, "close": 103.0, "volume": 1000},
                {"date": "2022-06-15", "open": 103.0, "close": 106.0, "volume": 1100},
                {"date": "2023-01-05", "open": 106.0, "close": 109.0, "volume": 1200},
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history(
                "test_api_key",
                "AAPL",
                start_date="2022-01-01",
                end_date="2023-12-31",
                frequency="annual",
            )

            assert len(result) >= 1

    def test_get_price_history_with_fields_parameter(self):
        """Test filtering columns with fields parameter."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
                {
                    "date": "2023-01-03",
                    "open": 150.0,
                    "high": 155.0,
                    "low": 149.0,
                    "close": 154.0,
                    "volume": 1000000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            # Test with only close field
            result = get_price_history("test_api_key", "AAPL", fields=["close"])

            assert len(result) == 2
            assert list(result.columns) == ["close"]
            assert "open" not in result.columns
            assert "high" not in result.columns

    def test_get_price_history_with_multiple_fields(self):
        """Test filtering with multiple fields."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            # Test with OHLC fields only (no volume)
            result = get_price_history(
                "test_api_key",
                "AAPL",
                fields=["open", "high", "low", "close"],
            )

            assert len(result) == 1
            assert set(result.columns) == {"open", "high", "low", "close"}
            assert "volume" not in result.columns

    def test_get_price_history_with_invalid_fields(self):
        """Test that invalid fields are filtered out."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            # Invalid fields should be filtered out, keeping only valid ones
            result = get_price_history(
                "test_api_key",
                "AAPL",
                fields=["close", "invalid_field"],
            )

            # Should only have 'close' column (invalid_field filtered out)
            assert len(result) == 1
            assert list(result.columns) == ["close"]

    def test_get_price_history_with_all_valid_fields(self):
        """Test with all valid fields specified."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            # Test with all valid fields
            result = get_price_history(
                "test_api_key",
                "AAPL",
                fields=["open", "high", "low", "close", "volume"],
            )

            assert len(result) == 1
            assert set(result.columns) == {"open", "high", "low", "close", "volume"}

    def test_get_price_history_fields_none_returns_all(self):
        """Test that fields=None returns all columns."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            # Test with fields=None (default)
            result = get_price_history("test_api_key", "AAPL")

            assert len(result) == 1
            # Should have all columns
            assert "open" in result.columns
            assert "high" in result.columns
            assert "low" in result.columns
            assert "close" in result.columns
            assert "volume" in result.columns

    def test_get_price_history_fields_not_in_response(self):
        """Test that requesting fields not in response returns empty DataFrame."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "close": 150.0,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            # Request fields that don't exist in response
            result = get_price_history(
                "test_api_key", "AAPL", fields=["open", "high", "low"]
            )

            # Should return DataFrame with index but no columns
            assert len(result) == 1
            assert len(result.columns) == 0
            assert result.index.name == "date"

    def test_get_price_history_limit_applied_after_resampling(self):
        """Test that limit is applied after resampling."""
        from duk.fmp_api import get_price_history

        # Create 14 days of daily data (2 full weeks)
        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": f"2023-01-{i:02d}",
                    "open": 100.0 + i,
                    "high": 105.0 + i,
                    "low": 99.0 + i,
                    "close": 103.0 + i,
                    "volume": 1000 + i * 10,
                }
                for i in range(1, 15)
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            # Request weekly data with limit=2 and start_date (no end_date)
            # Should fetch data from start_date, resample to weekly, then limit to 2
            result = get_price_history(
                "test_api_key",
                "AAPL",
                start_date="2023-01-01",
                frequency="week",
                limit=2,
            )

            # Should have exactly 2 weekly records (limit applied after resampling)
            assert len(result) == 2
            # Verify it's resampled (should have aggregated data)
            assert "close" in result.columns
            assert "volume" in result.columns

    def test_get_price_history_with_adjusted_true(self):
        """Test that adjusted=True uses adjusted_price_history_api."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "adjOpen": 149.0,
                    "adjHigh": 151.0,
                    "adjLow": 148.0,
                    "adjClose": 150.0,
                    "adjVolume": 900000,
                },
                {
                    "date": "2023-01-03",
                    "adjOpen": 150.0,
                    "adjHigh": 155.0,
                    "adjLow": 149.0,
                    "adjClose": 154.0,
                    "adjVolume": 1000000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history("test_api_key", "AAPL", adjusted=True)

            # Verify the correct API endpoint was called (dividend-adjusted)
            call_args = mock_get.call_args
            assert "dividend-adjusted" in call_args[0][0]

            # Verify column names have "adj" prefix stripped
            assert len(result) == 2
            assert "open" in result.columns
            assert "high" in result.columns
            assert "low" in result.columns
            assert "close" in result.columns
            assert "volume" in result.columns
            # Verify no "adj" prefix remains
            assert "adjopen" not in result.columns
            assert "adjclose" not in result.columns

    def test_get_price_history_with_adjusted_false(self):
        """Test that adjusted=False uses regular price_history_api."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history("test_api_key", "AAPL", adjusted=False)

            # Verify the correct API endpoint was called (regular price history)
            call_args = mock_get.call_args
            assert "historical-price-eod/full" in call_args[0][0]
            assert "dividend-adjusted" not in call_args[0][0]

            # Verify regular column names
            assert len(result) == 1
            assert "open" in result.columns
            assert "close" in result.columns

    def test_get_price_history_adjusted_strips_whitespace(self):
        """Test that adjusted=True strips 'adj' prefix and any whitespace."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "adj Open": 149.0,
                    "adj High": 151.0,
                    "adj Low": 148.0,
                    "adj Close": 150.0,
                    "adj Volume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history("test_api_key", "AAPL", adjusted=True)

            # Verify column names have "adj" prefix and whitespace stripped
            assert len(result) == 1
            # Check for properly cleaned column names (no "adj " prefix or extra spaces)
            assert "open" in result.columns
            assert "high" in result.columns
            assert "low" in result.columns
            assert "close" in result.columns
            assert "volume" in result.columns
            # Verify no whitespace or prefix remains
            for col in result.columns:
                assert not col.startswith("adj")
                assert col == col.strip()  # No leading or trailing whitespace

    def test_get_price_history_adjusted_only_strips_prefix(self):
        """Test that stripping 'adj' only removes prefix, not from other parts."""
        from duk.fmp_api import get_price_history

        mock_response = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2023-01-02",
                    "adjClose": 150.0,
                    "adjOpen": 149.0,
                    "adjHigh": 151.0,
                    "adjLow": 148.0,
                    "adjVolume": 900000,
                },
            ],
        }

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            mock_get.return_value.raise_for_status = mock.Mock()

            result = get_price_history("test_api_key", "AAPL", adjusted=True)

            # Verify the prefix was stripped correctly using slicing
            assert len(result) == 1
            assert "close" in result.columns
            assert "open" in result.columns
            assert "high" in result.columns
            assert "low" in result.columns
            assert "volume" in result.columns
            # Verify values are correct after column rename
            assert result.iloc[0]["close"] == 150.0
            assert result.iloc[0]["open"] == 149.0
