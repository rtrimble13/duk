# get_price_history Function

## Overview

The `get_price_history` function retrieves historical price data for securities from the Financial Modeling Prep (FMP) API and returns it as a pandas DataFrame. It combines date range calculation, API data fetching, and data transformation into a single convenient function.

## Function Signature

```python
def get_price_history(
    api_key: str,
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frequency: str = "day",
    limit: Optional[int] = None,
    fields: Optional[List[str]] = None,
) -> pd.DataFrame
```

## Parameters

- **api_key** (str): Your FMP API key for authentication
- **symbol** (str): The ticker symbol for the security (e.g., "AAPL", "MSFT", "GOOGL")
- **start_date** (Optional[str]): Start date in YYYY-MM-DD format (e.g., "2023-01-01")
- **end_date** (Optional[str]): End date in YYYY-MM-DD format (e.g., "2023-12-31")
- **frequency** (str): Data frequency. Valid values:
  - `"day"` (default): Daily data
  - `"week"`: Weekly data
  - `"month"`: Monthly data
  - `"quarter"`: Quarterly data
  - `"semi-annual"`: Semi-annual data
  - `"annual"`: Annual data
- **limit** (Optional[int]): Maximum number of records to return
- **fields** (Optional[List[str]]): List of columns to return. Valid fields are:
  - `"open"`: Opening price
  - `"high"`: Highest price
  - `"low"`: Lowest price
  - `"close"`: Closing price
  - `"volume"`: Trading volume
  - Default: All fields

## Returns

A pandas DataFrame with historical price data, indexed on Date (ascending order).

When `fields` is specified, only the requested columns are returned. Otherwise, all available columns are included.

## Limit Behavior

The `limit` parameter behaves differently based on which dates are provided:

### Case 1: limit with start_date (no end_date)
Returns the **first N records** starting from start_date.

```python
# Get first 10 daily records starting from 2023-01-01
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2023-01-01",
    limit=10
)
# Returns: 2023-01-01 through 2023-01-10 (approximately)
```

### Case 2: limit with end_date (no start_date)
Returns the **last N records** before end_date.

```python
# Get last 10 daily records before 2023-12-31
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    end_date="2023-12-31",
    limit=10
)
# Returns: 2023-12-21 through 2023-12-31 (approximately)
```

## Usage Examples

### Example 1: Get All Available Daily Data

```python
from duk import get_price_history

df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL"
)

print(f"Retrieved {len(df)} records")
print(df.head())
```

### Example 2: Get Data for a Specific Date Range

```python
from duk import get_price_history

df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

print(f"2023 AAPL data: {len(df)} records")
```

### Example 3: Get First N Records from a Date

```python
from duk import get_price_history

# Get first 20 daily records starting from 2023-01-01
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2023-01-01",
    limit=20
)

print(f"First 20 records from 2023-01-01:")
print(df)
```

### Example 4: Get Last N Records Before a Date

```python
from duk import get_price_history

# Get last 30 daily records before 2023-12-31
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    end_date="2023-12-31",
    limit=30
)

print(f"Last 30 records before 2023-12-31:")
print(df)
```

### Example 5: Get Weekly Data

```python
from duk import get_price_history

# Get weekly data for 2023
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31",
    frequency="week"
)

print(f"Weekly data: {len(df)} records")
print(df.head())
```

### Example 6: Get Monthly Data with Limit

```python
from duk import get_price_history

# Get last 12 months of data
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    frequency="month",
    limit=12
)

print(f"Last 12 months of data:")
print(df)
```

### Example 7: Get Quarterly Data

```python
from duk import get_price_history

# Get quarterly data for 2022-2023
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2022-01-01",
    end_date="2023-12-31",
    frequency="quarter"
)

print(f"Quarterly data: {len(df)} records")
print(df)
```

### Example 8: Get Annual Data

```python
from duk import get_price_history

# Get last 5 years of annual data
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    frequency="annual",
    limit=5
)

print(f"Last 5 years of annual data:")
print(df)
```

### Example 9: Using with Environment Variable for API Key

```python
import os
from duk import get_price_history

# Set API key in environment
# export FMP_API_KEY="your_api_key"

api_key = os.environ.get("FMP_API_KEY")

df = get_price_history(
    api_key=api_key,
    symbol="MSFT",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

print(df.head())
```

### Example 10: Data Analysis Example

```python
from duk import get_price_history
import matplotlib.pyplot as plt

# Get daily data
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Calculate daily returns
df['returns'] = df['close'].pct_change()

# Plot closing prices
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['close'])
plt.title('AAPL Closing Prices - 2023')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.grid(True)
plt.show()

# Calculate statistics
print(f"Average closing price: ${df['close'].mean():.2f}")
print(f"Max closing price: ${df['close'].max():.2f}")
print(f"Min closing price: ${df['close'].min():.2f}")
print(f"Average daily return: {df['returns'].mean():.4%}")
```

### Example 11: Get Only Closing Prices

```python
from duk import get_price_history

# Get only close prices for analysis
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31",
    fields=["close"]
)

print(df.head())
# DataFrame will only have the 'close' column
```

### Example 12: Get OHLC Data Without Volume

```python
from duk import get_price_history

# Get OHLC data excluding volume for charting
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31",
    fields=["open", "high", "low", "close"]
)

print(df.columns)  # ['open', 'high', 'low', 'close']
```

### Example 13: Compare Multiple Stocks - Close Prices Only

```python
from duk import get_price_history
import pandas as pd

# Get close prices for multiple stocks
symbols = ["AAPL", "MSFT", "GOOGL"]
data = {}

for symbol in symbols:
    df = get_price_history(
        api_key="your_api_key",
        symbol=symbol,
        start_date="2023-01-01",
        end_date="2023-12-31",
        fields=["close"]
    )
    data[symbol] = df["close"]

# Combine into single DataFrame
comparison = pd.DataFrame(data)
print(comparison.head())
```

## Data Resampling

When using frequencies other than "day", the function automatically resamples the data:

- **open**: First value in the period
- **high**: Maximum value in the period
- **low**: Minimum value in the period
- **close**: Last value in the period
- **volume**: Sum of volumes in the period

This ensures proper OHLC (Open-High-Low-Close) aggregation for financial data.

## Error Handling

The function raises the following exceptions:

- **ValueError**: For invalid date formats or parameters
- **FMPAPIError**: When the API request fails (network errors, invalid API key, etc.)

Example error handling:

```python
from duk import get_price_history, FMPAPIError

try:
    df = get_price_history(
        api_key="your_api_key",
        symbol="INVALID_SYMBOL",
        start_date="2023-01-01"
    )
except FMPAPIError as e:
    print(f"API error: {e}")
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

## Notes

- The DataFrame is always returned with dates in ascending order
- The index of the DataFrame is the date column (as a pandas DatetimeIndex)
- When no data is available, an empty DataFrame is returned
- The function uses the `get_api_date_range` helper function to calculate date ranges
- Date calculations respect the frequency parameter for limit-based ranges

## Related Functions

- `price_history_api()`: Lower-level function for raw API access
- `get_api_date_range()`: Helper function for date range calculations

## Configuration

For setting up API keys and other configuration, see the main README.md file.
