# Treasury Rate Downloader (`duk tr`)

The `duk tr` subprogram downloads U.S. Treasury par yield curve rates using the Financial Modeling Prep (FMP) API.

Note: An FMP API key is required. You can provide the key in one of two ways:
1. Set the `FMP_API_KEY` environment variable (recommended for CI/automated environments)
2. Place your key in `etc/.fmp_api.key` file

## Overview

This command retrieves daily Treasury par yield curve rates via the FMP API, which represent the interest rates on Treasury securities of various maturities. The data includes rates for maturities from 1 month to 30 years.

Key features:
- Download par yield curve data for specific dates or date ranges
- Cubic spline interpolation for smooth yield curves at regular intervals
- Bootstrap spot rate calculation from par rates (zero-coupon rates)
- Multiple output formats (CSV, JSON) and flexible file naming

## Basic Usage

```bash
# Download the most recent available data to stdout (CSV format)
duk tr

# Download with verbose logging
duk -v tr

# Download with interpolation
duk tr --interpolate

# Download with bootstrap spot rates (includes interpolation)
duk tr --bootstrap-spot-rates
```

## Cubic Spline Interpolation

The `tr` command supports cubic spline interpolation of the yield curve data to provide rates at regular intervals along the maturity spectrum.

### Basic Interpolation
```bash
# Perform semiannual interpolation (default)
duk tr --interpolate
duk tr -i

# Specify different interpolation intervals
duk tr --interpolate --interpolate-interval quarter
duk tr --interpolate --interpolate-interval month
duk tr --interpolate --interpolate-interval day
```

### Interpolation Output Format

When interpolation is enabled, the output format changes to:
- `calendar_date`: Date in YYYY-MM-DD format
- `date_decimal_years`: Date expressed as decimal years (reference: year 2000)
- `maturity_years`: Maturity in decimal years
- `interpolated_rate`: Interpolated interest rate

### Interpolation Intervals

- **semiannual** (default): 0.5-year intervals (e.g., 0.5, 1.0, 1.5, 2.0...)
- **quarter**: 0.25-year intervals (e.g., 0.25, 0.5, 0.75, 1.0...)
- **month**: Monthly intervals (e.g., 0.083, 0.167, 0.25...)
- **day**: Mixed intervals from daily (short-term) to yearly (long-term)

### Interpolation Examples
```bash
# Latest data with default semiannual interpolation
duk tr --interpolate

# Historical data with quarterly interpolation
duk tr --date 2023-12-01 --interpolate --interpolate-interval quarter

# Save interpolated data to file
duk tr --days 5 --interpolate --output

# Multiple dates with monthly interpolation in JSON format
duk tr --start-date 2023-11-01 --end-date 2023-11-30 --interpolate --interpolate-interval month --format json --output
```

## Bootstrap Spot Rates

The `tr` command can calculate bootstrap spot rates (zero-coupon rates) from the par yield curve data. This feature automatically enables interpolation and provides both par rates and spot rates in the output.

### Basic Bootstrap Usage
```bash
# Calculate spot rates with default semiannual interpolation
duk tr --bootstrap-spot-rates

# Calculate spot rates with quarterly interpolation
duk tr --bootstrap-spot-rates --interpolate-interval quarter

# Calculate spot rates for specific date
duk tr --date 2023-12-01 --bootstrap-spot-rates
```

### Bootstrap Output Format

When bootstrap spot rates are enabled, the output format includes:
- `calendar_date`: Date in YYYY-MM-DD format
- `maturity_years`: Maturity in decimal years
- `interpolated_rate`: Interpolated par rate (original par yield curve)
- `interpolated_spot_rate`: Bootstrap-calculated spot rate (zero-coupon rate)

### Bootstrap Algorithm

The bootstrap method used follows these principles:
- For maturities < 0.5 year: spot rate equals par rate (minimal coupon effect)
- For longer maturities: iteratively solve for spot rates using previously calculated rates
- **Assumes semiannual coupon payments** for bond pricing calculations (standard for Treasury bonds)
- When interpolation interval is not semiannual, performs a two-step process:
  1. Bootstrap calculation using semiannual coupon frequency
  2. Interpolation from semiannual to the target interval

### Bootstrap Examples
```bash
# Latest data with bootstrap spot rates
duk tr --bootstrap-spot-rates

# Historical data with bootstrap spot rates and quarterly intervals
duk tr --date 2023-12-01 --bootstrap-spot-rates --interpolate-interval quarter

# Save bootstrap data to file with custom naming
duk tr --bootstrap-spot-rates --output --filename treasury_bootstrap_data

# Multiple dates with bootstrap spot rates in JSON format
duk tr --start-date 2023-11-01 --end-date 2023-11-30 --bootstrap-spot-rates --format json --output
```

### Bootstrap File Naming

When saving bootstrap data to files, the naming convention automatically includes "bootstrap":
- CSV: `treasury_par_yields_interpolated_bootstrap_semiannual_YYYYMMDD.csv`
- JSON: `treasury_par_yields_interpolated_bootstrap_semiannual_YYYYMMDD.json`

## Date Options

### Specific Date
```bash
# Download data for a specific date
duk tr --date 2023-12-01
duk tr -d 2023-12-01
```

### Date Range
```bash
# Download data for a date range
duk tr --start-date 2023-11-01 --end-date 2023-11-30
duk tr -s 2023-11-01 -e 2023-11-30
```

### Number of Days
```bash
# Download last 5 days of data
duk tr --days 5
duk tr -n 5

# Download 10 days starting from a specific date
duk tr --start-date 2023-12-01 --days 10
```

## Output Options

### Output to File
```bash
# Output to file with default naming (treasury_par_yields_YYYYMMDD.csv)
duk tr --output
duk tr -o

# Output to file with custom filename
duk tr --filename my_treasury_data
duk tr -f my_treasury_data

# Specify output directory
duk tr --output --directory /path/to/output
duk tr -o -D /path/to/output
```

### Output Formats

#### CSV Format (Default)
```bash
# CSV output to stdout
duk tr

# CSV output to file
duk tr --output --format csv
```

#### JSON Format
```bash
# JSON output to stdout
duk tr --format json

# JSON output to file
duk tr --output --format json
```

## Data Structure

The treasury data includes the following fields:

- `record_date`: The date of the yield curve data (YYYY-MM-DD)
- `month1`, `month2`, `month3`, `month4`, `month6`: Short-term rates (months)
- `year1`, `year2`, `year3`, `year5`, `year7`: Medium-term rates (years)
- `year10`, `year20`, `year30`: Long-term rates (years)

Rate values are expressed as percentages (e.g., 4.25 represents 4.25%).

## Examples

### Basic Usage Examples
```bash
# Get latest data
duk tr

# Get data for last trading week (5 days)
duk tr --days 5

# Get specific date
duk tr --date 2023-12-01
```

### File Output Examples
```bash
# Save last 30 days to default file
duk tr --days 30 --output

# Save to custom filename in JSON format
duk tr --days 10 --filename rates_december --format json --output

# Save to specific directory
duk tr --output --directory ./data/treasury
```

### Advanced Examples
```bash
# Download Q4 2023 data to CSV file
duk tr --start-date 2023-10-01 --end-date 2023-12-31 --output

# Get year-end data for multiple years (would require multiple commands)
duk tr --date 2022-12-30 --filename rates_2022 --output
duk tr --date 2023-12-29 --filename rates_2023 --output

# Bootstrap spot rates with quarterly interpolation and file output
duk tr --bootstrap-spot-rates --interpolate-interval quarter --output

# Bootstrap spot rates for historical analysis
duk tr --start-date 2023-01-01 --end-date 2023-12-31 --bootstrap-spot-rates --format json --output
```

## Integration with Data Analysis

The output format is designed to be easily loaded into pandas DataFrames:

### Python Integration
```python
import pandas as pd

# Load CSV output
df = pd.read_csv('treasury_par_yields_20231201.csv')

# Convert date column to datetime
df['record_date'] = pd.to_datetime(df['record_date'])

# Set date as index for time series analysis
df.set_index('record_date', inplace=True)
```

### JSON Integration
```python
import json
import pandas as pd

# Load JSON output
with open('treasury_par_yields_20231201.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df['record_date'] = pd.to_datetime(df['record_date'])
```

### Bootstrap Data Integration
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load bootstrap spot rates data
df = pd.read_csv('treasury_par_yields_interpolated_bootstrap_semiannual_20231201.csv')

# Convert date column to datetime
df['calendar_date'] = pd.to_datetime(df['calendar_date'])

# Compare par rates vs spot rates
plt.figure(figsize=(10, 6))
plt.plot(df['maturity_years'], df['interpolated_rate'], label='Par Rates', marker='o')
plt.plot(df['maturity_years'], df['interpolated_spot_rate'], label='Spot Rates', marker='s')
plt.xlabel('Maturity (Years)')
plt.ylabel('Interest Rate (%)')
plt.title('Par Rates vs Bootstrap Spot Rates')
plt.legend()
plt.grid(True)
plt.show()

# Calculate rate differences
df['rate_difference'] = df['interpolated_spot_rate'] - df['interpolated_rate']
print("Maximum difference between spot and par rates:", df['rate_difference'].abs().max())
```

## Error Handling

The command provides clear error messages for common issues:

- **Network connectivity issues**: "Failed to download treasury data"
- **Invalid date formats**: Use YYYY-MM-DD format
- **No data available**: "No data found for the specified criteria"
- **Invalid date combinations**: Cannot specify --date with --start-date or --end-date

## Logging

When run with the `-v` flag, detailed logging information is written to `var/duk.log` and displayed on stderr, including:

- API request details
- Number of records downloaded
- File save locations
- Error details for troubleshooting

## Data Source

Data is retrieved from the U.S. Treasury's Fiscal Data API:
- **API Endpoint**: `https://api.fiscaldata.treasury.gov/services/api/v1/accounting/od/daily_treasury_par_yield_curve_rates`
- **Data Source**: U.S. Department of the Treasury, Bureau of the Fiscal Service
- **Update Frequency**: Daily (business days)
- **Historical Coverage**: Data available from 1990 to present

## Notes

- Treasury markets are closed on weekends and federal holidays, so no data is available for these dates
- The most recent data may be delayed by 1-2 business days
- All rates are expressed as annual percentages
- The par yield curve represents the yields of the most recently auctioned Treasury securities