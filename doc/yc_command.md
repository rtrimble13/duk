# duk yc Command

## Overview

The `yc` command retrieves treasury yield curve data from the Financial Modeling Prep (FMP) API and outputs it to stdout or a file.

## Command Signature

```bash
duk yc [options]
```

## Options

### Date and Limit Options

- `-s, --start-date TEXT`: Start date in YYYY-MM-DD format (e.g., "2023-06-01")
- `-e, --end-date TEXT`: End date in YYYY-MM-DD format (e.g., "2023-06-30")
- `-n, --limit INTEGER`: Maximum number of records to return

### Yield Curve Options

- `-z, --zero-rates`: Return zero rate yield curve (bootstrapped from par rates). By default, par rates are returned.
- `--tenors TEXT`: Filter tenor range. Specify as 'start_tenor, end_tenor'. Example: `'month6, year10'` returns tenors from 6 months to 10 years.
- `--key-rates`: Return only key rate tenors: year1, year5, year10, year20, year30
- `-i, --interval`: Interpolation interval between tenors. Valid values:
  - `day`: Daily intervals
  - `week`: Weekly intervals
  - `month`: Monthly intervals
  - `quarter`: Quarterly intervals
  - `semi-annual`: Semi-annual intervals
  - `annual`: Annual intervals

**Note**: `--tenors` and `--key-rates` cannot be used together.

### Output Options

- `--csv`: Output data as CSV format (default)
- `--json`: Output data as JSON format
- `-o, --output PATH`: Write data to file instead of stdout
  - If PATH is a file, data is written to that file with appropriate extension
  - If PATH is a directory, filename is formatted as `yc_<start>_<end>.<ext>` where ext is csv or json
- `-q, --quiet`: Suppress printing yield curve data to stdout
- `-v, --verbose`: Print all logging to stdout (debug level)

**Note**: Only one of `--csv` or `--json` can be specified at a time. If neither is specified, CSV format is used by default.

## Configuration

The command requires an FMP API key, which can be provided in two ways:

1. Environment variable: `FMP_API_KEY`
2. Configuration file (`~/.dukrc`):
   ```toml
   [api]
   fmp_key = "your_api_key_here"
   ```

The environment variable takes precedence over the configuration file.

## Usage Examples

### Example 1: Get Current Yield Curve

```bash
duk yc -n 1
```

Retrieves the most recent yield curve data.

### Example 2: Get Yield Curve for a Specific Date

```bash
duk yc -s 2023-06-01 -e 2023-06-01
```

Retrieves yield curve data for June 1, 2023.

### Example 3: Get Last 30 Days of Yield Curves

```bash
duk yc -n 30
```

Retrieves the last 30 days of yield curve data.

### Example 4: Get Zero Rate Curve

```bash
duk yc -n 1 -z
```

Retrieves the most recent yield curve and converts par rates to zero (spot) rates using bootstrapping.

### Example 5: Get Yield Curve with Tenor Filter

```bash
duk yc -n 1 --tenors "month6, year10"
```

Retrieves only the tenors between 6 months and 10 years.

### Example 6: Get Key Rate Tenors Only

```bash
duk yc -n 1 --key-rates
```

Retrieves only year1, year5, year10, year20, and year30 tenors. This is useful for key rate duration analysis.

### Example 7: Get Yield Curve with Quarterly Interpolation

```bash
duk yc -n 1 -i quarter
```

Retrieves yield curve data with interpolated points at quarterly intervals.

### Example 8: Get Zero Rate Curve with Monthly Interpolation

```bash
duk yc -s 2023-06-01 -e 2023-06-01 -z -i month
```

Retrieves zero rate curve for a specific date with monthly interpolated points.

### Example 9: Write Yield Curve to File

```bash
duk yc -n 1 -o yc_latest.csv
```

Retrieves yield curve data and writes it to `yc_latest.csv`.

### Example 10: Write JSON Output to File

```bash
duk yc -n 1 --json -o yc_latest.json
```

Retrieves yield curve data and writes it in JSON format to `yc_latest.json`.

### Example 11: Write Data to Directory

```bash
duk yc -s 2023-06-01 -e 2023-06-30 -o ./data/
```

Retrieves yield curve data for June 2023 and writes it to `./data/yc_2023-06-01_2023-06-30.csv`.

### Example 12: Quiet Mode with File Output

```bash
duk yc -n 30 -o output.csv -q
```

Retrieves data and writes to file without printing data to stdout. Only the confirmation message is printed.

### Example 13: Verbose Mode for Debugging

```bash
duk yc -n 1 -v
```

Retrieves data with debug logging enabled, showing detailed information about the API request and processing.

### Example 14: Combine Multiple Options

```bash
duk yc -s 2023-01-01 -e 2023-12-31 -z --tenors "year1, year10" -i quarter --json -o analysis.json
```

Retrieves 2023 yield curves, converts to zero rates, filters to 1-10 year range, interpolates quarterly, and saves as JSON.

## Output Format

The command can output data in two formats: CSV (default) or JSON.

### Single Date Output Format

When the result contains a single date (e.g., when using `-n 1`), the output is tenor-indexed with the following columns:

**CSV Example:**
```csv
tenor,years,date,par_rate
month1,0.083,2023-07-01,4.35
month3,0.25,2023-09-01,4.45
month6,0.5,2023-12-01,4.50
year1,1.0,2024-06-01,4.68
year2,2.0,2025-06-01,4.20
year10,10.0,2033-06-01,3.79
year30,30.0,2053-06-01,3.90
```

When using `--zero-rates`, the `par_rate` column is replaced with `zero_rate`.

### Multiple Dates Output Format

When the result contains multiple dates, the output is date-indexed with tenor columns:

**CSV Example:**
```csv
date,month1,month3,month6,year1,year2,year10,year30
2023-06-01,4.35,4.45,4.50,4.68,4.20,3.79,3.90
2023-06-02,4.38,4.47,4.52,4.70,4.22,3.81,3.92
2023-06-05,4.40,4.48,4.53,4.72,4.24,3.82,3.93
```

### JSON Output Format

JSON output contains an array of objects:

**Single Date Example:**
```json
[
  {"tenor": "month1", "years": 0.083, "date": "2023-07-01", "par_rate": 4.35},
  {"tenor": "year1", "years": 1.0, "date": "2024-06-01", "par_rate": 4.68},
  {"tenor": "year10", "years": 10.0, "date": "2033-06-01", "par_rate": 3.79}
]
```

**Multiple Dates Example:**
```json
[
  {"date": "2023-06-01", "month1": 4.35, "year1": 4.68, "year10": 3.79},
  {"date": "2023-06-02", "month1": 4.38, "year1": 4.70, "year10": 3.81}
]
```

## Tenor Names

Treasury yield curve data uses the following tenor naming convention:

- Short-term: `month1`, `month2`, `month3`, `month6`
- Medium-term: `year1`, `year2`, `year3`, `year5`, `year7`
- Long-term: `year10`, `year20`, `year30`

When using `--interval` for interpolation, additional tenors are created. For example, with quarterly interpolation (`-i quarter`):
- `year1`, `year1.25`, `year1.5`, `year1.75`, `year2`, ...

## Zero Rate Bootstrapping

When `--zero-rates` is specified:

1. The par yield curve is first interpolated to semi-annual intervals (required for bootstrapping)
2. Zero rates are calculated using the bootstrap method:
   - For tenors ≤ 1 year: zero rate = par rate
   - For tenors > 1 year: zero rates are bootstrapped assuming semi-annual coupon payments

Zero rates (also called spot rates) are useful for:
- Bond pricing
- Forward rate calculations
- Discount factor derivation
- Duration and convexity calculations

## Limit Behavior

The `--limit` parameter behaves differently based on which dates are provided:

### With start_date (no end_date)
Returns the **first N records** starting from start_date.

```bash
duk yc -s 2023-01-01 -n 10
# Returns: First 10 records starting from 2023-01-01
```

### With end_date (no start_date)
Returns the **last N records** before end_date.

```bash
duk yc -e 2023-12-31 -n 10
# Returns: Last 10 records before 2023-12-31
```

### With neither start_date nor end_date
Returns the **last N records** available.

```bash
duk yc -n 30
# Returns: Last 30 records available
```

## Error Handling

The command will exit with an error (exit code 1) in the following cases:

1. **Missing API Key**: FMP API key not configured
   ```
   Error: FMP API key not configured. Set FMP_API_KEY environment variable
   or add fmp_key to [api] section in ~/.dukrc
   ```

2. **Multiple Output Formats**: Both --csv and --json specified
   ```
   Error: Only one of --csv or --json can be specified
   ```

3. **Conflicting Tenor Options**: Both --tenors and --key-rates specified
   ```
   Error: Cannot use both --tenors and --key-rates. Choose one.
   ```

4. **Invalid Tenors Format**: Tenors not in correct format
   ```
   Error: Invalid tenors format. Use format: 'start_tenor, end_tenor'. Example: 'month6, year10'
   ```

5. **API Error**: Failed to fetch data from the API
   ```
   Error: Failed to fetch yield curve: <error message>
   ```

When no data is available, the command exits successfully (exit code 0) with a message:
```
No yield curve data found
```

## Tips and Best Practices

1. **Use Environment Variables**: Set `FMP_API_KEY` as an environment variable to avoid storing sensitive data in config files:
   ```bash
   export FMP_API_KEY="your_api_key_here"
   duk yc -n 1
   ```

2. **Use Key Rates for Analysis**: When doing key rate duration analysis, use `--key-rates` to get only the standard key rate tenors:
   ```bash
   duk yc -n 1 --key-rates
   ```

3. **Zero Rates for Pricing**: Use `--zero-rates` when you need discount factors for pricing:
   ```bash
   duk yc -n 1 -z
   ```

4. **Combine with Unix Tools**: The CSV output can be easily processed with standard Unix tools:
   ```bash
   # Get 10-year yield for last 30 days
   duk yc -n 30 | cut -d, -f1,7
   
   # Filter with grep
   duk yc -n 30 | grep "2023-06"
   ```

5. **Use JSON with jq**: JSON output works well with jq for advanced data processing:
   ```bash
   # Extract 10-year yields
   duk yc -n 30 --json | jq '.[].year10'
   
   # Calculate average 10-year yield
   duk yc -n 30 --json | jq '[.[].year10] | add/length'
   ```

6. **Quiet Mode for Scripts**: Use `-q` flag in scripts to suppress data output while still getting status messages:
   ```bash
   duk yc -n 30 -o data.csv -q && echo "Data downloaded successfully"
   ```

7. **Verbose Mode for Troubleshooting**: Use `-v` flag to see detailed logging when debugging issues:
   ```bash
   duk yc -n 1 -v
   ```

## Related Functions

- `get_yield_curve()`: Python function used internally by the command
- `treasury_rates_api()`: Lower-level API function for raw data access
- `bootstrap_zero_rates()`: Function for converting par rates to zero rates
- `interpolate_rates()`: Function for interpolating yield curve points

## See Also

- [get_yield_curve Function Documentation](get_yield_curve.md)
- [ph Command Documentation](ph_command.md)
- Main duk documentation: `man duk`
