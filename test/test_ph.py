"""Tests for price history (ph) module."""

import os

import pandas as pd
import pytest
import requests

from duk.ph import get_price_history


class TestGetPriceHistory:
    """Tests for get_price_history function."""

    def test_symbol_normalization(self, mocker):
        """Test that symbol is normalized to uppercase."""
        mock_response = mocker.Mock()
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

        mocker.patch("requests.get", return_value=mock_response)

        # Test lowercase symbol
        df = get_price_history("ibm", api_key="test_key")
        assert not df.empty

        # Test uppercase symbol
        df = get_price_history("IBM", api_key="test_key")
        assert not df.empty

        # Test mixed case
        df = get_price_history("IbM", api_key="test_key")
        assert not df.empty

    def test_invalid_symbol(self, mocker):
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

    def test_missing_api_key(self, mocker):
        """Test error when API key is missing."""
        # Ensure no API key in environment
        mocker.patch.dict(os.environ, {}, clear=True)

        with pytest.raises(ValueError, match="FMP API key not found"):
            get_price_history("IBM")

    def test_api_request_failure(self, mocker):
        """Test handling of API request failures."""
        mocker.patch(
            "requests.get",
            side_effect=requests.RequestException("Connection error"),
        )
        with pytest.raises(requests.RequestException):
            get_price_history("IBM", api_key="test_key")

    def test_no_historical_data(self, mocker):
        """Test handling when no historical data is returned."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"symbol": "INVALID"}

        mocker.patch("requests.get", return_value=mock_response)
        with pytest.raises(ValueError, match="No historical data found"):
            get_price_history("INVALID", api_key="test_key")

    def test_data_sorting_ascending(self, mocker):
        """Test that data is sorted by date in ascending order."""
        mock_response = mocker.Mock()
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

        mocker.patch("requests.get", return_value=mock_response)
        df = get_price_history("IBM", api_key="test_key", limit=None)

        # Check that dates are in ascending order
        dates = df["date"].tolist()
        assert dates == sorted(dates)

        # Check first and last dates
        assert df.iloc[0]["date"] == pd.Timestamp("2024-01-01")
        assert df.iloc[-1]["date"] == pd.Timestamp("2024-01-03")

    def test_limit_parameter(self, mocker):
        """Test that limit parameter returns correct number of records."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "IBM",
            "historical": [
                {"date": f"2024-01-{i:02d}", "close": 100.0 + i} for i in range(1, 11)
            ],
        }

        mocker.patch("requests.get", return_value=mock_response)
        # Test with limit=5
        df = get_price_history("IBM", api_key="test_key", limit=5)
        assert len(df) == 5

        # Should get the 5 most recent (last 5 after sorting)
        assert df.iloc[-1]["date"] == pd.Timestamp("2024-01-10")

    def test_default_fields(self, mocker):
        """Test that default fields are returned."""
        mock_response = mocker.Mock()
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

        mocker.patch("requests.get", return_value=mock_response)
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

    def test_custom_fields(self, mocker):
        """Test that custom fields parameter works."""
        mock_response = mocker.Mock()
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

        mocker.patch("requests.get", return_value=mock_response)
        df = get_price_history("IBM", api_key="test_key", fields=["close", "volume"])

        # Date should always be included
        assert "date" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns

        # Other fields should not be included
        assert "open" not in df.columns
        assert "high" not in df.columns
        assert "low" not in df.columns

    def test_date_range_parameters(self, mocker):
        """Test that date range parameters are passed correctly."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "IBM",
            "historical": [{"date": "2024-01-15", "close": 103.0}],
        }

        mock_get = mocker.patch("requests.get", return_value=mock_response)
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


@pytest.mark.integration
class TestFMPAPIIntegration:
    """Integration tests that make real API calls to FMP."""

    def test_real_api_call(self):
        """
        Test real API call to FMP.

        This test requires a valid FMP API key to be set in the
        FMP_API_KEY environment variable or ~/.dukrc config file.

        Skip this test if no API key is available.
        """
        # Try to get API key from environment or config
        api_key = os.getenv("FMP_API_KEY")

        if not api_key:
            pytest.skip("FMP_API_KEY not set - skipping integration test")

        # Make a real API call with a well-known symbol
        try:
            df = get_price_history(
                "AAPL",  # Apple stock - very stable, always has data
                api_key=api_key,
                limit=5,  # Just get 5 records to keep it quick
            )

            # Verify we got data back
            assert not df.empty, "API returned empty data"
            assert len(df) <= 5, "Limit parameter not respected"

            # Verify expected columns are present
            expected_columns = ["date", "open", "high", "low", "close", "volume"]
            for col in expected_columns:
                assert col in df.columns, f"Missing column: {col}"

            # Verify data types
            assert df["date"].dtype == "datetime64[ns]", "Date column not datetime"
            assert df["close"].dtype in [
                "float64",
                "float32",
            ], "Close price not float"

            # Verify dates are in ascending order
            dates = df["date"].tolist()
            assert dates == sorted(dates), "Dates not in ascending order"

            # Verify price values are reasonable (positive)
            assert (df["close"] > 0).all(), "Found non-positive price values"

            print(f"\n✓ Successfully retrieved {len(df)} records from FMP API")
            print(f"  Latest date: {df.iloc[-1]['date']}")
            print(f"  Latest close: ${df.iloc[-1]['close']:.2f}")

        except requests.RequestException as e:
            pytest.fail(f"API request failed: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error during API call: {e}")
