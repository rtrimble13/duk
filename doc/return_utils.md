# Return Calculation Utilities

The `return_utils` module provides comprehensive functions for calculating various types of financial returns from price data. This module is designed for investment performance measurement and analysis.

## Overview

The module includes functions for:
- Simple returns
- Log returns
- Price differences
- Cumulative returns
- Multi-period returns
- Dividend-adjusted returns
- Excess returns
- Annualized returns

## Functions

### `simple_return(prices, periods=1)`

Calculate simple returns from a price series.

**Formula**: `(P_t - P_{t-1}) / P_{t-1}`

**Parameters**:
- `prices` (pd.Series | pd.DataFrame): Price series or DataFrame
- `periods` (int): Number of periods to look back (default: 1)

**Returns**: Series or DataFrame of simple returns

**Example**:
```python
import pandas as pd
from duk.return_utils import simple_return

prices = pd.Series([100, 105, 103, 108])
returns = simple_return(prices)
print(returns)
# Output:
# 0         NaN
# 1    0.050000
# 2   -0.019048
# 3    0.048544
```

**Use Cases**:
- Daily, weekly, or monthly return calculations
- Portfolio performance tracking
- Comparing asset performance

---

### `log_return(prices, periods=1)`

Calculate log returns (continuously compounded returns) from a price series.

**Formula**: `ln(P_t) - ln(P_{t-1}) = ln(P_t / P_{t-1})`

**Parameters**:
- `prices` (pd.Series | pd.DataFrame): Price series or DataFrame
- `periods` (int): Number of periods to look back (default: 1)

**Returns**: Series or DataFrame of log returns

**Example**:
```python
import pandas as pd
from duk.return_utils import log_return

prices = pd.Series([100, 105, 103, 108])
log_returns = log_return(prices)
print(log_returns)
# Output:
# 0         NaN
# 1    0.048790
# 2   -0.019231
# 3    0.047402
```

**Use Cases**:
- Time-additive return calculations
- Statistical analysis (log returns are more normally distributed)
- Continuous compounding models

**Note**: Log returns have the useful property that they are additive across time: `sum(r_t) = ln(P_T / P_0)`

---

### `price_difference(prices, periods=1)`

Calculate price differences from a price series.

**Formula**: `P_t - P_{t-1}`

**Parameters**:
- `prices` (pd.Series | pd.DataFrame): Price series or DataFrame
- `periods` (int): Number of periods to look back (default: 1)

**Returns**: Series or DataFrame of price differences

**Example**:
```python
import pandas as pd
from duk.return_utils import price_difference

prices = pd.Series([100, 105, 103, 108])
diffs = price_difference(prices)
print(diffs)
# Output:
# 0    NaN
# 1    5.0
# 2   -2.0
# 3    5.0
```

**Use Cases**:
- Absolute price change analysis
- Dollar profit/loss calculations
- Volatility measurement in price units

---

### `cumulative_simple_return(returns)`

Calculate cumulative simple return from a series of simple returns.

**Formula**: `R_T = ∏(1 + r_t) - 1`

**Parameters**:
- `returns` (pd.Series | pd.DataFrame): Series or DataFrame of simple returns

**Returns**: Float (for Series) or Series (for DataFrame) representing total cumulative return

**Example**:
```python
import pandas as pd
from duk.return_utils import cumulative_simple_return

returns = pd.Series([0.05, -0.02, 0.03, 0.01])
cumulative = cumulative_simple_return(returns)
print(f"Total return: {cumulative:.4f}")
# Output: Total return: 0.0705
```

**Use Cases**:
- Total return over a period
- Portfolio value growth calculation
- Comparing investment alternatives

---

### `cumulative_log_return(returns)`

Calculate cumulative log return from a series of log returns.

**Formula**: `R_T = ∑r_t`

**Parameters**:
- `returns` (pd.Series | pd.DataFrame): Series or DataFrame of log returns

**Returns**: Float (for Series) or Series (for DataFrame) representing total cumulative log return

**Example**:
```python
import pandas as pd
from duk.return_utils import cumulative_log_return

log_returns = pd.Series([0.0488, -0.0192, 0.0296, 0.0099])
cumulative = cumulative_log_return(log_returns)
print(f"Total log return: {cumulative:.4f}")
# Output: Total log return: 0.0691
```

**Use Cases**:
- Continuously compounded returns
- Statistical modeling
- Time-series analysis

---

### `multi_period_return(prices, periods)`

Calculate multi-period returns from a price series.

**Formula**: `R_{t,k} = P_t / P_{t-k} - 1`

**Parameters**:
- `prices` (pd.Series | pd.DataFrame): Price series or DataFrame
- `periods` (int): Number of periods to look back

**Returns**: Series or DataFrame of multi-period returns

**Example**:
```python
import pandas as pd
from duk.return_utils import multi_period_return

prices = pd.Series([100, 105, 103, 108, 110])
# Calculate 2-period returns
returns_2p = multi_period_return(prices, periods=2)
print(returns_2p)
# Output:
# 0         NaN
# 1         NaN
# 2    0.030000
# 3    0.028571
# 4    0.067961
```

**Use Cases**:
- Rolling window performance
- Overlapping period analysis
- Momentum indicators

---

### `dividend_adjusted_return(prices, dividends, periods=1)`

Calculate dividend-adjusted returns from price and dividend series.

**Formula**: `(P_t + D_t - P_{t-1}) / P_{t-1}`

**Parameters**:
- `prices` (pd.Series | pd.DataFrame): Price series or DataFrame
- `dividends` (pd.Series | pd.DataFrame): Dividend series matching price structure (0 if no dividend)
- `periods` (int): Number of periods to look back (default: 1)

**Returns**: Series or DataFrame of dividend-adjusted returns

**Example**:
```python
import pandas as pd
from duk.return_utils import dividend_adjusted_return

prices = pd.Series([100, 105, 103, 108])
dividends = pd.Series([0, 2, 0, 1])
returns = dividend_adjusted_return(prices, dividends)
print(returns)
# Output:
# 0         NaN
# 1    0.070000  # Includes $2 dividend
# 2   -0.019048
# 3    0.058252  # Includes $1 dividend
```

**Use Cases**:
- Total return calculation (price + income)
- Stock return analysis including dividends
- Reinvestment assumption modeling

**Note**: This assumes dividends are paid at the end of the period and immediately reinvested.

---

### `excess_return(returns_i, returns_j)`

Calculate excess returns between two return series.

**Formula**: `r_{t,i} - r_{t,j}`

**Parameters**:
- `returns_i` (pd.Series | pd.DataFrame): First return series (typically asset return)
- `returns_j` (pd.Series | pd.DataFrame): Second return series (typically benchmark return)

**Returns**: Series or DataFrame of excess returns

**Example**:
```python
import pandas as pd
from duk.return_utils import excess_return

asset_returns = pd.Series([0.05, 0.02, -0.01, 0.03])
benchmark_returns = pd.Series([0.03, 0.02, 0.01, 0.02])
excess = excess_return(asset_returns, benchmark_returns)
print(excess)
# Output:
# 0    0.02
# 1    0.00
# 2   -0.02
# 3    0.01
```

**Use Cases**:
- Performance attribution
- Alpha calculation
- Risk-adjusted return analysis
- Benchmark comparisons

---

### `annualized_return(returns, periods_per_year=252, return_type='simple')`

Calculate annualized return from a series of returns.

**Formulas**:
- Simple: `(1 + R_total)^(periods_per_year / N) - 1`
- Log: `R_total * (periods_per_year / N)`

**Parameters**:
- `returns` (pd.Series | pd.DataFrame): Series or DataFrame of returns
- `periods_per_year` (int): Number of periods in a year (default: 252 trading days)
- `return_type` (str): Either 'simple' or 'log' (default: 'simple')

**Returns**: Float (for Series) or Series (for DataFrame) representing annualized return

**Example**:
```python
import pandas as pd
from duk.return_utils import annualized_return

# Daily returns for 252 trading days
daily_returns = pd.Series([0.001] * 252)

# Annualize simple returns
ann_simple = annualized_return(daily_returns, periods_per_year=252, return_type='simple')
print(f"Annualized simple return: {ann_simple:.4f}")
# Output: Annualized simple return: 0.2864

# For monthly data, use periods_per_year=12
monthly_returns = pd.Series([0.01] * 12)
ann_monthly = annualized_return(monthly_returns, periods_per_year=12, return_type='simple')
print(f"Annualized return from monthly data: {ann_monthly:.4f}")
# Output: Annualized return from monthly data: 0.1268
```

**Use Cases**:
- Standardizing returns across different time periods
- Comparing strategies with different data frequencies
- Annual performance reporting

**Common `periods_per_year` values**:
- 252: Daily data (trading days)
- 52: Weekly data
- 12: Monthly data
- 4: Quarterly data

---

## Complete Example: Portfolio Analysis

Here's a complete example demonstrating multiple return calculations:

```python
import pandas as pd
import numpy as np
from duk.return_utils import (
    simple_return, log_return, cumulative_simple_return,
    annualized_return, excess_return
)

# Sample price data for a stock
dates = pd.date_range('2023-01-01', periods=252, freq='B')  # Business days
np.random.seed(42)
prices = pd.Series(
    100 * np.exp(np.random.randn(252).cumsum() * 0.01),
    index=dates
)

# Calculate simple returns
daily_returns = simple_return(prices)

# Calculate cumulative return
total_return = cumulative_simple_return(daily_returns)
print(f"Total return: {total_return:.2%}")

# Calculate annualized return
ann_return = annualized_return(daily_returns, periods_per_year=252, return_type='simple')
print(f"Annualized return: {ann_return:.2%}")

# Compare against benchmark (e.g., market index)
benchmark_returns = pd.Series(
    np.random.randn(252) * 0.01 + 0.0003,  # Slightly positive drift
    index=dates[1:]  # Align with returns (first return is NaN)
)

# Calculate excess returns (alpha)
alpha = excess_return(daily_returns.dropna(), benchmark_returns)
avg_alpha = alpha.mean()
print(f"Average daily excess return: {avg_alpha:.4%}")
print(f"Annualized excess return: {avg_alpha * 252:.2%}")

# Compare log returns vs simple returns
log_rets = log_return(prices)
print(f"\nLog return sum: {log_rets.sum():.4f}")
print(f"Simple return product: {np.log(1 + total_return):.4f}")
# These should be approximately equal
```

## Error Handling

All functions in this module raise `ReturnCalculationError` for invalid inputs:

```python
from duk.return_utils import simple_return, ReturnCalculationError

try:
    # This will raise an error
    simple_return(pd.Series([]))
except ReturnCalculationError as e:
    print(f"Error: {e}")
    # Output: Error: Price series is empty
```

## Performance Considerations

- All functions use vectorized pandas operations for efficiency
- Functions work with both Series and DataFrame inputs
- NaN values are handled gracefully (typically propagated in calculations)
- Large datasets (millions of rows) are processed efficiently

## Best Practices

1. **Use log returns for statistical analysis**: Log returns are more normally distributed and additive across time.

2. **Use simple returns for portfolio calculations**: Simple returns can be weighted by portfolio allocation.

3. **Include dividends for total return**: Use `dividend_adjusted_return()` when calculating total return for dividend-paying stocks.

4. **Standardize periods for comparison**: Use `annualized_return()` to compare strategies with different data frequencies.

5. **Check for missing data**: Handle NaN values appropriately before calculation:
   ```python
   # Fill forward or drop NaN values as appropriate
   prices_clean = prices.ffill()  # or prices.dropna()
   ```

## Integration with Other duk Modules

The return utilities work seamlessly with price data from other duk functions:

```python
from duk.fmp_api import price_history_api
from duk.return_utils import simple_return, annualized_return
import pandas as pd

# Get price data
api_key = "your_api_key"
price_data = price_history_api("AAPL", api_key)

# Convert to DataFrame
df = pd.DataFrame(price_data)
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date').sort_index()

# Calculate returns
daily_returns = simple_return(df['close'])
annual_return = annualized_return(daily_returns, periods_per_year=252)

print(f"Annualized return for AAPL: {annual_return:.2%}")
```

## Mathematical References

- **Simple Returns**: Ross, S. A., Westerfield, R. W., & Jaffe, J. (2013). *Corporate Finance*.
- **Log Returns**: Campbell, J. Y., Lo, A. W., & MacKinlay, A. C. (1997). *The Econometrics of Financial Markets*.
- **Annualized Returns**: Bodie, Z., Kane, A., & Marcus, A. J. (2018). *Investments*.

## See Also

- [get_price_history.md](get_price_history.md) - Retrieving price data
- [pandas Documentation](https://pandas.pydata.org/docs/) - DataFrame operations
- [NumPy Documentation](https://numpy.org/doc/) - Numerical computing

---

**Module**: `duk.return_utils`  
**Version**: 0.2.0  
**Last Updated**: December 2024
