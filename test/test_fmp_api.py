"""
Tests for FMP API module.
"""

from unittest import mock

import pytest
import requests

from duk.fmp_api import FMPAPIError, price_history_api


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

            result = price_history_api(
                "AAPL",
                "test_api_key",
                from_date="2023-06-01",
                to_date="2023-06-30",
            )

            # Verify the correct parameters were passed
            call_args = mock_get.call_args
            assert call_args[1]["params"]["from"] == "2023-06-01"
            assert call_args[1]["params"]["to"] == "2023-06-30"
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
            assert "historical-price-full/AAPL" in call_args[0][0]
            assert call_args[1]["params"]["apikey"] == "test_api_key"
            assert call_args[1]["timeout"] == 30
