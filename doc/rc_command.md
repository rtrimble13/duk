# duk rc Command

## Overview

The `rc` command computes various types of returns from price data. It reads price data from CSV or JSON files and calculates simple returns, log returns, price differences, cumulative returns, and annualized returns. The command is designed to work with time series price data that includes a date column and one or more numeric price columns.

## Command Signature

```bash
duk rc -i <input_file> [return_options] [output_options]
```

## Required Options

- `-i, --input PATH`: Input file containing price data (CSV or JSON format). **Required**.
  - Must contain a `date` column (case-insensitive: `date`, `Date`, or `DATE`)
  - Must contain at least one numeric price column (e.g., `close`, `open`, `high`, `low`)

## Return Calculation Options

At least one return calculation option must be specified. Multiple options can be used together to compute different return types simultaneously.

### Basic Return Calculations

- `--simple`: Compute arithmetic (simple) returns
  - Formula: `(P_t - P_{t-1}) / P_{t-1}`
  - Output column suffix: `_simple_ret`

- `--log`: Compute log returns
  - Formula: `ln(P_t / P_{t-1})`
  - Output column suffix: `_log_ret`

- `--diff`: Compute price differences
  - Formula: `P_t - P_{t-1}`
  - Output column suffix: `_diff`

### Cumulative Return Calculations

- `--cum-simple`: Compute cumulative simple returns
  - Formula: `prod(1 + r_i) - 1` for i=1 to t
  - Output column suffix: `_cum_simple`

- `--cum-log`: Compute cumulative log returns
  - Formula: `sum(r_i)` for i=1 to t
  - Output column suffix: `_cum_log`

### Annualized Return Calculations

- `--annual-simple`: Compute annualized simple returns
  - Automatically infers the frequency from the date index
  - Formula: `(1 + R_cumulative)^(periods_per_year / N) - 1`
  - Output column suffix: `_annual_simple`

- `--annual-log`: Compute annualized log returns
  - Automatically infers the frequency from the date index
  - Formula: `R_cumulative * (periods_per_year / N)`
  - Output column suffix: `_annual_log`

## Additional Options

### Lookback Period

- `-l, --lookback INTEGER`: Number of periods to lookback for computing multi-period returns (default: 1)
  - Applies to all return calculations (simple, log, diff, cumulative, annualized)
  - When lookback > 1, output columns are suffixed with `_l{lookback}` (e.g., `_simple_ret_l2`)

### Data Options

- `-a, --append`: Include input price data in the output
  - Original price columns are included alongside computed return columns

### Output Options

- `--csv`: Output data as CSV format (default)
- `--json`: Output data as JSON format
- `-o, --output PATH`: Write data to file instead of stdout
- `-q, --quiet`: Suppress printing return data to stdout
- `-v, --verbose`: Print all logging to stdout (debug level)

**Note**: Only one of `--csv` or `--json` can be specified at a time.

## Frequency Inference for Annualized Returns

When using `--annual-simple` or `--annual-log`, the command automatically infers the data frequency by analyzing the average time difference between dates in the input:

| Average Days Between Observations | Inferred Frequency | Periods Per Year |
|-----------------------------------|-------------------|------------------|
| ≤ 1.5 days                        | Daily             | 252              |
| ≤ 5 days                          | Weekly            | 52               |
| ≤ 20 days                         | Monthly           | 12               |
| ≤ 70 days                         | Quarterly         | 4                |
| ≤ 150 days                        | Semi-annual       | 2                |
| > 150 days                        | Annual            | 1                |

## Usage Examples

### Example 1: Compute Simple Returns

```bash
duk rc -i prices.csv --simple
```

Computes simple returns from price data in `prices.csv`.

**Input (prices.csv):**
```csv
date,close
2023-01-02,100.0
2023-01-03,105.0
2023-01-04,103.0
```

**Output:**
```csv
date,close_simple_ret
2023-01-02,
2023-01-03,0.05
2023-01-04,-0.019048
```

### Example 2: Compute Multiple Return Types

```bash
duk rc -i prices.csv --simple --log --diff
```

Computes simple returns, log returns, and price differences simultaneously.

**Output:**
```csv
date,close_simple_ret,close_log_ret,close_diff
2023-01-02,,,
2023-01-03,0.05,0.04879,5.0
2023-01-04,-0.019048,-0.019231,-2.0
```

### Example 3: Include Original Prices in Output

```bash
duk rc -i prices.csv --simple --append
```

Includes the original price data alongside the computed returns.

**Output:**
```csv
date,close,close_simple_ret
2023-01-02,100.0,
2023-01-03,105.0,0.05
2023-01-04,103.0,-0.019048
```

### Example 4: Compute Multi-Period Returns

```bash
duk rc -i prices.csv --simple --lookback 2
```

Computes 2-period simple returns (comparing each price to the price 2 periods ago).

**Output:**
```csv
date,close_simple_ret_l2
2023-01-02,
2023-01-03,
2023-01-04,0.03
2023-01-05,0.028571
```

### Example 5: Compute Cumulative Returns

```bash
duk rc -i prices.csv --cum-simple
```

Computes cumulative simple returns from the beginning of the series.

**Output:**
```csv
date,close_cum_simple
2023-01-02,
2023-01-03,0.05
2023-01-04,0.029
2023-01-05,0.059870
```

### Example 6: Compute Annualized Returns

```bash
duk rc -i daily_prices.csv --annual-simple
```

Computes annualized simple returns, automatically detecting that the data is daily (252 trading days per year).

### Example 7: Work with Multiple Price Columns

```bash
duk rc -i prices.csv --simple
```

When the input has multiple price columns, returns are computed for each column.

**Input (prices.csv):**
```csv
date,open,close
2023-01-02,99.0,100.0
2023-01-03,104.0,105.0
2023-01-04,102.0,103.0
```

**Output:**
```csv
date,open_simple_ret,close_simple_ret
2023-01-02,,
2023-01-03,0.050505,0.05
2023-01-04,-0.019231,-0.019048
```

### Example 8: JSON Input and Output

```bash
duk rc -i prices.json --simple --json -o returns.json
```

Reads from JSON input file, computes simple returns, and writes JSON output to a file.

### Example 9: Complex Analysis with Multiple Options

```bash
duk rc -i prices.csv --simple --cum-simple --annual-simple --append --lookback 5 -o analysis.csv
```

Performs comprehensive return analysis:
- Computes 5-period simple returns
- Computes cumulative simple returns
- Computes annualized simple returns
- Includes original price data
- Saves results to `analysis.csv`

### Example 10: Quiet Mode for Scripting

```bash
duk rc -i prices.csv --simple -o returns.csv --quiet
```

Computes returns and saves to file without printing output to console. Useful for scripts and automated workflows.

## Input File Requirements

### Required Structure

1. **Date Column**: The input must have a column named `date` (case-insensitive)
   - Supported formats: Any format parseable by pandas (e.g., "2023-01-02", "2023-01-02 10:30:00")
   - The date column is automatically sorted in ascending order

2. **Price Columns**: At least one numeric column containing price data
   - Column names can be anything (e.g., `close`, `open`, `high`, `low`, `price`, `adj_close`)
   - All numeric columns are treated as price data

### Supported Input Formats

- **CSV**: Standard comma-separated values file
- **JSON**: JSON file with records format (list of dictionaries)

### Example Input Files

**CSV Format:**
```csv
date,close,volume
2023-01-02,100.0,1000000
2023-01-03,105.0,1200000
2023-01-04,103.0,950000
```

**JSON Format:**
```json
[
  {"date": "2023-01-02", "close": 100.0, "volume": 1000000},
  {"date": "2023-01-03", "close": 105.0, "volume": 1200000},
  {"date": "2023-01-04", "close": 103.0, "volume": 950000}
]
```

## Return Type Descriptions

### Simple Returns
- Most commonly used return metric
- Intuitive interpretation: a return of 0.05 means a 5% gain
- Not time-additive: R(t1→t3) ≠ R(t1→t2) + R(t2→t3)
- Use case: Single-period performance analysis

### Log Returns
- Also called continuous compounding returns
- Time-additive: R(t1→t3) = R(t1→t2) + R(t2→t3)
- More suitable for statistical analysis
- Use case: Multi-period return aggregation, portfolio theory

### Price Differences
- Absolute change in price
- Not normalized by price level
- Use case: Analyzing price movements in absolute terms

### Cumulative Returns
- Total return from the beginning of the series to each point
- Shows the running total performance
- Use case: Visualizing overall performance over time

### Annualized Returns
- Scales returns to a per-year basis for comparison
- Useful for comparing returns across different time periods
- Use case: Comparing performance of different assets or strategies

## Notes and Best Practices

1. **Data Quality**: Ensure your input data is clean and properly formatted. Missing dates in time series data may affect return calculations.

2. **Lookback Periods**: When using lookback > 1, the first `lookback` observations will have NaN (empty) values for returns.

3. **Annualized Returns**: For annualized return calculations, ensure you have at least 2 observations so the frequency can be inferred.

4. **Multiple Calculations**: You can compute multiple return types in a single command for efficiency.

5. **Volume Columns**: Non-price numeric columns (like volume) will also have returns computed. If you only want returns for specific columns, filter your input data beforehand.

6. **Large Files**: For large datasets, consider using the `--quiet` flag and `-o` option to write directly to a file rather than printing to stdout.

## Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Input data must contain a 'date' column" | No date column found | Ensure your input has a column named 'date' (case-insensitive) |
| "Input data must contain at least one numeric price column" | No numeric columns found | Add price data columns to your input |
| "At least one return calculation option must be specified" | No return option provided | Add at least one option like --simple, --log, etc. |
| "Input file contains no data" | Empty input file | Provide a file with data |
| "Only one of --csv or --json can be specified" | Both output formats specified | Choose either --csv or --json, not both |
| "Need at least 2 observations to infer periods_per_year" | Less than 2 data points for annualized returns | Provide more data points or don't use annualized returns |

## See Also

- [return_utils.md](return_utils.md) - Detailed documentation of the underlying return calculation functions
- [ph_command.md](ph_command.md) - Fetching price history data to use with rc command
- [get_price_history.md](get_price_history.md) - API for downloading price data

## Integration Example

Combine `duk ph` and `duk rc` for a complete workflow:

```bash
# Step 1: Download price data
duk ph AAPL -s 2023-01-01 -e 2023-12-31 -o aapl_prices.csv

# Step 2: Compute returns
duk rc -i aapl_prices.csv --simple --cum-simple --annual-simple --append -o aapl_analysis.csv
```

This workflow downloads Apple stock prices for 2023 and then computes various return metrics.
