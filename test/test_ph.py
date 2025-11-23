"""
Unit tests for ph (price history) module.
"""

import json
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from duk.ph import format_output, get_price_history


class TestGetPriceHistory:
    """Test cases for get_price_history function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.symbol = "IBM"

        # Sample API response
        self.mock_response_data = {
            "symbol": "IBM",
            "historical": [
                {
                    "date": "2024-01-05",
                    "open": 150.0,
                    "high": 152.0,
                    "low": 149.0,
                    "close": 151.5,
                    "volume": 1000000,
                },
                {
                    "date": "2024-01-04",
                    "open": 149.0,
                    "high": 150.5,
                    "low": 148.0,
                    "close": 150.0,
                    "volume": 900000,
                },
                {
                    "date": "2024-01-03",
                    "open": 148.0,
                    "high": 149.5,
                    "low": 147.5,
                    "close": 149.0,
                    "volume": 850000,
                },
            ],
        }

    def test_get_price_history_success(self):
        """Test successful price history retrieval."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.mock_response_data
            mock_get.return_value = mock_response

            df = get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                limit=3,
            )

            assert len(df) == 3
            assert list(df.columns) == [
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
            # Check data is sorted by date ascending
            assert df["date"].is_monotonic_increasing

    def test_get_price_history_case_insensitive(self):
        """Test that symbol is case-insensitive."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.mock_response_data
            mock_get.return_value = mock_response

            # Test with lowercase
            get_price_history(
                symbol="ibm",
                api_key=self.api_key,
                limit=3,
            )

            # Check that API was called with uppercase symbol
            call_args = mock_get.call_args
            assert "IBM" in call_args[0][0]

    def test_get_price_history_with_date_range(self):
        """Test price history with date range."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.mock_response_data
            mock_get.return_value = mock_response

            get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                start_date="2024-01-01",
                end_date="2024-01-31",
                limit=3,
            )

            # Check that date parameters were passed
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["from"] == "2024-01-01"
            assert params["to"] == "2024-01-31"

    def test_get_price_history_with_custom_fields(self):
        """Test price history with custom fields."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.mock_response_data
            mock_get.return_value = mock_response

            df = get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                fields=["date", "close", "volume"],
                limit=3,
            )

            assert list(df.columns) == ["date", "close", "volume"]

    def test_get_price_history_limit_applied(self):
        """Test that limit is properly applied."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            # Create more data points
            extended_data = self.mock_response_data.copy()
            extended_data["historical"] = [
                {
                    "date": f"2024-01-{i:02d}",
                    "open": 150.0,
                    "high": 152.0,
                    "low": 149.0,
                    "close": 151.5,
                    "volume": 1000000,
                }
                for i in range(1, 11)
            ]
            mock_response.json.return_value = extended_data
            mock_get.return_value = mock_response

            # Request only 5 records
            df = get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                limit=5,
            )

            assert len(df) == 5

    def test_get_price_history_no_api_key(self):
        """Test error handling when API key is missing."""
        with pytest.raises(ValueError, match="FMP API key is required"):
            get_price_history(
                symbol=self.symbol,
                api_key="",
                limit=5,
            )

    def test_get_price_history_invalid_frequency(self):
        """Test error handling for invalid frequency."""
        with pytest.raises(ValueError, match="Invalid frequency"):
            get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                frequency="invalid",
                limit=5,
            )

    def test_get_price_history_quarterly_frequency(self):
        """Test price history with quarterly frequency."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.mock_response_data
            mock_get.return_value = mock_response

            get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                frequency="quarterly",
                limit=5,
            )

            # Check that API was called with line series for quarterly
            call_args = mock_get.call_args
            assert "serietype=line" in call_args[0][0]

    def test_get_price_history_semi_annual_frequency(self):
        """Test price history with semi-annual frequency."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.mock_response_data
            mock_get.return_value = mock_response

            get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                frequency="semi-annual",
                limit=5,
            )

            # Check that API was called with line series for semi-annual
            call_args = mock_get.call_args
            assert "serietype=line" in call_args[0][0]

    def test_get_price_history_annual_frequency(self):
        """Test price history with annual frequency."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.mock_response_data
            mock_get.return_value = mock_response

            get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                frequency="annual",
                limit=5,
            )

            # Check that API was called with line series for annual
            call_args = mock_get.call_args
            assert "serietype=line" in call_args[0][0]

    def test_get_price_history_api_error(self):
        """Test handling of API error response."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Error Message": "Invalid API key"}
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match="API error"):
                get_price_history(
                    symbol=self.symbol,
                    api_key=self.api_key,
                    limit=5,
                )

    def test_get_price_history_no_historical_data(self):
        """Test handling when no historical data is returned."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"symbol": "INVALID"}
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match="No historical data found"):
                get_price_history(
                    symbol="INVALID",
                    api_key=self.api_key,
                    limit=5,
                )

    def test_get_price_history_request_timeout(self):
        """Test handling of request timeout."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()

            with pytest.raises(requests.exceptions.Timeout):
                get_price_history(
                    symbol=self.symbol,
                    api_key=self.api_key,
                    limit=5,
                )

    def test_get_price_history_request_failure(self):
        """Test handling of request failure."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException(
                "Connection error"
            )

            with pytest.raises(requests.exceptions.RequestException):
                get_price_history(
                    symbol=self.symbol,
                    api_key=self.api_key,
                    limit=5,
                )

    def test_get_price_history_http_error(self):
        """Test handling of HTTP error status."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
            mock_get.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                get_price_history(
                    symbol=self.symbol,
                    api_key=self.api_key,
                    limit=5,
                )

    def test_get_price_history_empty_data(self):
        """Test handling of empty historical data."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "symbol": "IBM",
                "historical": [],
            }
            mock_get.return_value = mock_response

            df = get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                limit=5,
            )

            assert df.empty

    def test_get_price_history_date_sorting(self):
        """Test that results are sorted by date in ascending order."""
        with patch("duk.ph.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            # Data in random order
            mock_response.json.return_value = {
                "symbol": "IBM",
                "historical": [
                    {"date": "2024-01-03", "close": 149.0, "volume": 100},
                    {"date": "2024-01-01", "close": 147.0, "volume": 100},
                    {"date": "2024-01-05", "close": 151.0, "volume": 100},
                    {"date": "2024-01-02", "close": 148.0, "volume": 100},
                    {"date": "2024-01-04", "close": 150.0, "volume": 100},
                ],
            }
            mock_get.return_value = mock_response

            df = get_price_history(
                symbol=self.symbol,
                api_key=self.api_key,
                limit=5,
            )

            # Check dates are in ascending order
            dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
            assert dates == [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ]


class TestFormatOutput:
    """Test cases for format_output function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                "close": [150.0, 151.0],
                "volume": [1000000, 1100000],
            }
        )

    def test_format_output_csv(self):
        """Test CSV output format."""
        output = format_output(self.df, "csv")

        assert "date,close,volume" in output
        assert "150.0" in output
        assert "1000000" in output

    def test_format_output_json(self):
        """Test JSON output format."""
        output = format_output(self.df, "json")

        # Parse JSON to verify it's valid
        data = json.loads(output)
        assert len(data) == 2
        assert data[0]["close"] == 150.0
        assert data[0]["volume"] == 1000000

    def test_format_output_default_csv(self):
        """Test default output format is CSV."""
        output_csv = format_output(self.df)
        output_default = format_output(self.df, "csv")

        assert output_csv == output_default
