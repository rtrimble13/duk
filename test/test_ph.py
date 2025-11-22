"""Tests for price history (ph) module."""

import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from duk.ph import get_price_history


class TestGetPriceHistory:
    """Tests for get_price_history function."""

    def test_symbol_normalization(self):
        """Test that symbol is normalized to uppercase."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "IBM",
            "historical": [
                {
                    "date": "2024-01-01",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 103.0,
                    "adjClose": 103.0,
                    "volume": 1000000,
                }
            ],
        }

        with patch("requests.get", return_value=mock_response):
            # Test lowercase symbol
            df = get_price_history("ibm", api_key="test_key")
            assert not df.empty

            # Test uppercase symbol
            df = get_price_history("IBM", api_key="test_key")
            assert not df.empty

            # Test mixed case
            df = get_price_history("IbM", api_key="test_key")
            assert not df.empty

    def test_invalid_symbol(self):
        """Test error handling for invalid symbols."""
        # Empty symbol
        with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
            get_price_history("", api_key="test_key")

        # None symbol
        with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
            get_price_history(None, api_key="test_key")

        # Non-string symbol
        with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
            get_price_history(123, api_key="test_key")

    def test_missing_api_key(self):
        """Test error when API key is missing."""
        # Ensure no API key in environment
        old_key = os.environ.get("FMP_API_KEY")
        if "FMP_API_KEY" in os.environ:
            del os.environ["FMP_API_KEY"]

        try:
            with pytest.raises(ValueError, match="FMP API key not found"):
                get_price_history("IBM")
        finally:
            # Restore environment
            if old_key:
                os.environ["FMP_API_KEY"] = old_key

    def test_api_request_failure(self):
        """Test handling of API request failures."""
        with patch(
            "requests.get",
            side_effect=requests.RequestException("Connection error"),
        ):
            with pytest.raises(requests.RequestException):
                get_price_history("IBM", api_key="test_key")

    def test_no_historical_data(self):
        """Test handling when no historical data is returned."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"symbol": "INVALID"}

        with patch("requests.get", return_value=mock_response):
            with pytest.raises(ValueError, match="No historical data found"):
                get_price_history("INVALID", api_key="test_key")

    def test_data_sorting_ascending(self):
        """Test that data is sorted by date in ascending order."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "IBM",
            "historical": [
                {
                    "date": "2024-01-03",
                    "open": 102.0,
                    "high": 106.0,
                    "low": 101.0,
                    "close": 105.0,
                    "adjClose": 105.0,
                    "volume": 1200000,
                },
                {
                    "date": "2024-01-01",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 103.0,
                    "adjClose": 103.0,
                    "volume": 1000000,
                },
                {
                    "date": "2024-01-02",
                    "open": 101.0,
                    "high": 104.0,
                    "low": 100.0,
                    "close": 102.0,
                    "adjClose": 102.0,
                    "volume": 1100000,
                },
            ],
        }

        with patch("requests.get", return_value=mock_response):
            df = get_price_history("IBM", api_key="test_key", limit=None)

            # Check that dates are in ascending order
            dates = df["date"].tolist()
            assert dates == sorted(dates)

            # Check first and last dates
            assert df.iloc[0]["date"] == pd.Timestamp("2024-01-01")
            assert df.iloc[-1]["date"] == pd.Timestamp("2024-01-03")

    def test_limit_parameter(self):
        """Test that limit parameter returns correct number of records."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "IBM",
            "historical": [
                {"date": f"2024-01-{i:02d}", "close": 100.0 + i} for i in range(1, 11)
            ],
        }

        with patch("requests.get", return_value=mock_response):
            # Test with limit=5
            df = get_price_history("IBM", api_key="test_key", limit=5)
            assert len(df) == 5

            # Should get the 5 most recent (last 5 after sorting)
            assert df.iloc[-1]["date"] == pd.Timestamp("2024-01-10")

    def test_default_fields(self):
        """Test that default fields are returned."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "IBM",
            "historical": [
                {
                    "date": "2024-01-01",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 103.0,
                    "adjClose": 103.0,
                    "volume": 1000000,
                    "change": 3.0,
                    "changePercent": 3.0,
                }
            ],
        }

        with patch("requests.get", return_value=mock_response):
            df = get_price_history("IBM", api_key="test_key")

            # Check default fields are present
            expected_fields = [
                "date",
                "open",
                "high",
                "low",
                "close",
                "adjClose",
                "volume",
            ]
            for field in expected_fields:
                assert field in df.columns

            # Check that extra fields are not included
            assert "change" not in df.columns
            assert "changePercent" not in df.columns

    def test_custom_fields(self):
        """Test that custom fields parameter works."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "IBM",
            "historical": [
                {
                    "date": "2024-01-01",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 103.0,
                    "adjClose": 103.0,
                    "volume": 1000000,
                }
            ],
        }

        with patch("requests.get", return_value=mock_response):
            df = get_price_history(
                "IBM", api_key="test_key", fields=["close", "volume"]
            )

            # Date should always be included
            assert "date" in df.columns
            assert "close" in df.columns
            assert "volume" in df.columns

            # Other fields should not be included
            assert "open" not in df.columns
            assert "high" not in df.columns
            assert "low" not in df.columns

    def test_date_range_parameters(self):
        """Test that date range parameters are passed correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "IBM",
            "historical": [{"date": "2024-01-15", "close": 103.0}],
        }

        with patch("requests.get", return_value=mock_response) as mock_get:
            get_price_history(
                "IBM",
                api_key="test_key",
                from_date="2024-01-01",
                to_date="2024-01-31",
            )

            # Check that the parameters were passed
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["from"] == "2024-01-01"
            assert params["to"] == "2024-01-31"
