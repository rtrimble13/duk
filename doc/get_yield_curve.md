# get_yield_curve Function

## Overview

The `get_yield_curve` function retrieves treasury yield curve data from the Financial Modeling Prep (FMP) API and returns it as a pandas DataFrame. It supports date range filtering, zero rate bootstrapping, tenor filtering, and interpolation.

## Function Signature

```python
def get_yield_curve(
    api_key: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = None,
    zero_rates: bool = False,
    tenors: Optional[Tuple[str, str]] = None,
    interval: Optional[str] = None,
) -> pd.DataFrame
```

## Parameters

- **api_key** (str): Your FMP API key for authentication
- **start_date** (Optional[str]): Start date in YYYY-MM-DD format (e.g., "2023-01-01")
- **end_date** (Optional[str]): End date in YYYY-MM-DD format (e.g., "2023-12-31")
- **limit** (Optional[int]): Maximum number of records to return
- **zero_rates** (bool): If True, transform par rates to zero rates using bootstrapping. Default is False.
- **tenors** (Optional[Tuple[str, str]]): Filter tenor range as (start_tenor, end_tenor). For example, `("year1", "year10")` returns only tenors between 1 year and 10 years inclusive.
- **interval** (Optional[str]): Interpolation interval. Valid values:
  - `"day"`: Daily intervals
  - `"week"`: Weekly intervals
  - `"month"`: Monthly intervals
  - `"quarter"`: Quarterly intervals
  - `"semi-annual"`: Semi-annual intervals
  - `"annual"`: Annual intervals

## Returns

The function returns a pandas DataFrame with different structures depending on the number of dates returned:

### Multiple Dates
When multiple dates are returned:
- DataFrame is indexed on `date` (ascending order)
- Columns are the tenor names (e.g., 'month1', 'year1', 'year10')

### Single Date
When only one date is returned:
- DataFrame is indexed on tenor names
- Contains columns:
  - `years`: Tenor value in years (float)
  - `date`: Estimated maturity date (record date + years)
  - `par_rate` or `zero_rate`: Rate values (depending on zero_rates parameter)

## Limit Behavior

The `limit` parameter behaves differently based on which dates are provided:

### Case 1: limit with start_date (no end_date)
Returns the **first N records** starting from start_date.

### Case 2: limit with end_date (no start_date)
Returns the **last N records** before end_date.

## Usage Examples

### Example 1: Get Yield Curve for a Specific Date

```python
from duk.fmp_api import get_yield_curve

# Get yield curve for a single date
df = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-06-01",
    end_date="2023-06-01"
)

print(df)
# Output:
#         years       date  par_rate
# tenor
# month1  0.083 2023-07-01      4.35
# month6  0.500 2023-12-01      4.50
# year1   1.000 2024-06-01      4.68
# year10 10.000 2033-06-01      3.79
```

### Example 2: Get Zero Rate Curve

```python
from duk.fmp_api import get_yield_curve

# Get zero rate curve (bootstrapped from par rates)
df = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-06-01",
    end_date="2023-06-01",
    zero_rates=True
)

print(df.columns)
# Output: Index(['years', 'date', 'zero_rate'], dtype='object')
```

### Example 3: Get Last 30 Days of Yield Curves

```python
from duk.fmp_api import get_yield_curve

# Get last 30 days of yield curves
df = get_yield_curve(
    api_key="your_api_key",
    limit=30
)

print(f"Retrieved {len(df)} yield curve records")
print(df.head())
# Output: DataFrame indexed by date with tenor columns
```

### Example 4: Get Yield Curve with Quarterly Interpolation

```python
from duk.fmp_api import get_yield_curve

# Get yield curve with quarterly interpolated points
df = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-06-01",
    end_date="2023-06-01",
    interval="quarter"
)

print(df.index.tolist())
# Output includes: 'year1', 'year1.25', 'year1.5', 'year1.75', 'year2', ...
```

### Example 5: Filter to Specific Tenor Range

```python
from duk.fmp_api import get_yield_curve

# Get only 1-year to 10-year tenors
df = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-06-01",
    end_date="2023-06-01",
    tenors=("year1", "year10")
)

print(df.index.tolist())
# Output: ['year1', 'year2', 'year5', 'year7', 'year10']
# (excludes month1, month3, month6, year20, year30)
```

### Example 6: Get Historical Yield Curves for Analysis

```python
from duk.fmp_api import get_yield_curve
import matplotlib.pyplot as plt

# Get 2023 Q1 yield curves
df = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-01-01",
    end_date="2023-03-31"
)

# Plot 10-year yield over time
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['year10'])
plt.title('10-Year Treasury Yield - Q1 2023')
plt.xlabel('Date')
plt.ylabel('Yield (%)')
plt.grid(True)
plt.show()
```

### Example 7: Compare Par Rates vs Zero Rates

```python
from duk.fmp_api import get_yield_curve
import pandas as pd

# Get par rate curve
par_curve = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-06-01",
    end_date="2023-06-01",
    zero_rates=False
)

# Get zero rate curve
zero_curve = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-06-01",
    end_date="2023-06-01",
    zero_rates=True
)

# Compare the curves
comparison = pd.DataFrame({
    'years': par_curve['years'],
    'par_rate': par_curve['par_rate'],
    'zero_rate': zero_curve['zero_rate']
})

print(comparison)
```

### Example 8: Get Yield Curve Date Range with Limit

```python
from duk.fmp_api import get_yield_curve

# Get first 5 records starting from a specific date
df = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-01-01",
    limit=5
)

print(f"First date: {df.index[0]}")
print(f"Last date: {df.index[-1]}")
print(f"Records: {len(df)}")
```

### Example 9: Using with Environment Variable for API Key

```python
import os
from duk.fmp_api import get_yield_curve

# Set API key in environment
# export FMP_API_KEY="your_api_key"

api_key = os.environ.get("FMP_API_KEY")

df = get_yield_curve(
    api_key=api_key,
    start_date="2023-06-01",
    end_date="2023-06-01"
)

print(df.head())
```

### Example 10: Calculate Yield Curve Spread

```python
from duk.fmp_api import get_yield_curve

# Get yield curve
df = get_yield_curve(
    api_key="your_api_key",
    start_date="2023-06-01",
    end_date="2023-06-01"
)

# Calculate 10Y-2Y spread (common recession indicator)
spread_10y_2y = df.loc['year10', 'par_rate'] - df.loc['year2', 'par_rate']
print(f"10Y-2Y Spread: {spread_10y_2y:.2f} bps")
```

## Zero Rate Bootstrapping

When `zero_rates=True`, the function:
1. First interpolates the par yield curve to semi-annual intervals
2. Then applies bootstrapping to convert par yields to zero (spot) rates

For tenors ≤ 1 year, the zero rate equals the par rate. For tenors > 1 year, the zero rate is calculated using the bootstrap method assuming semi-annual coupon payments.

## Interpolation

When `interval` is specified, the function uses cubic spline interpolation to add additional tenor points. This is useful for:
- Creating smoother yield curves
- Getting rates at specific tenors not provided by the API
- Preparing data for pricing calculations that require fine-grained rate data

## Error Handling

The function raises the following exceptions:

- **ValueError**: For invalid date formats, invalid tenors, or invalid intervals
- **FMPAPIError**: When the API request fails (network errors, invalid API key, etc.)

Example error handling:

```python
from duk.fmp_api import get_yield_curve, FMPAPIError

try:
    df = get_yield_curve(
        api_key="your_api_key",
        start_date="2023-06-01",
        end_date="2023-06-01"
    )
except FMPAPIError as e:
    print(f"API error: {e}")
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

## Notes

- When multiple dates are returned, the DataFrame is always sorted by date in ascending order
- The `date` column in single-date output is an estimated maturity date calculated as: record_date + (years * 365 days)
- The `tenors` filter is inclusive on both ends
- Interpolation is applied before tenor filtering

## Related Functions

- `treasury_rates_api()`: Lower-level function for raw API access
- `treasury_rates2df()`: Convert API response to DataFrame
- `interpolate_rates()`: Cubic spline interpolation of rate curves
- `bootstrap_zero_rates()`: Convert par yields to zero rates
- `get_api_date_range()`: Helper function for date range calculations

## Configuration

For setting up API keys and other configuration, see the main README.md file.
