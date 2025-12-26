# duk ls Command

## Overview

The `ls` command retrieves company and market information from the Financial Modeling Prep (FMP) API and outputs it to stdout or a file. It supports both listing (sectors, industries, actively trading securities) and screening (filtering securities by various criteria).

## Command Signature

```bash
duk ls [options]
```

## Options

### List Type Options

These options control what type of list is returned or enable screening mode.

- `--sectors[=VALUE]`: List all market sectors (without value) or screen by sectors (with comma-separated values)
- `--industries[=VALUE]`: List all industries (without value) or screen by industries (with comma-separated values)

If no list type option is specified, the command returns actively trading securities.

**Important**: When values are provided to `--sectors` or `--industries`, the command switches to screening mode. In screening mode, you can combine these with other screening parameters.

### Screening Filter Options

These options are used to filter securities when screening. Each numeric filter supports comparison operators:
- Use `>` for "greater than" (e.g., `--price=>50`)
- Use `<` for "less than" (e.g., `--price=<200`)

**Numeric Filters:**
- `--market-cap`: Filter by market capitalization (e.g., `--market-cap=>1000000000`)
- `--price`: Filter by stock price (e.g., `--price=>50` or `--price=<200`)
- `--volume`: Filter by trading volume (e.g., `--volume=>1000000`)
- `--beta`: Filter by beta value (e.g., `--beta=>1.0` or `--beta=<0.5`)
- `--dividend`: Filter by dividend (e.g., `--dividend=>2.0`)

**Other Filters:**
- `--exchange`: Filter by exchange (e.g., `--exchange=NASDAQ`)
- `--country`: Filter by country code (e.g., `--country=US`)
- `--is-etf`: Filter for ETFs only (flag)
- `--is-fund`: Filter for funds only (flag)
- `--is-actively-trading`: Filter for actively trading securities only (flag)

### Output Options

- `--csv`: Output data as CSV format (default)
- `--json`: Output data as JSON format
- `-o, --output PATH`: Write data to file instead of stdout
- `-q, --quiet`: Suppress printing list data to stdout
- `-v, --verbose`: Print all logging to stdout (debug level)

### General Options

- `-n, --limit INTEGER`: Maximum number of records to return

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

### Listing Examples

#### Example 1: Get Actively Trading Securities

```bash
duk ls
```

Retrieves all actively trading securities with symbol and name fields.

#### Example 2: Get Limited Number of Securities

```bash
duk ls -n 10
```

Retrieves the first 10 actively trading securities.

#### Example 3: Get All Market Sectors

```bash
duk ls --sectors
```

Retrieves a list of all market sectors.

#### Example 4: Get All Industries

```bash
duk ls --industries
```

Retrieves a list of all industries.

#### Example 5: Write Securities to a File

```bash
duk ls -o securities.csv
```

Retrieves actively trading securities and writes them to `securities.csv`.

#### Example 6: Get Sectors in JSON Format

```bash
duk ls --sectors --json
```

Retrieves market sectors and outputs them in JSON format.

### Screening Examples

#### Example 7: Screen by Single Sector

```bash
duk ls --sectors=Technology
```

Retrieves all securities in the Technology sector.

#### Example 8: Screen by Multiple Sectors

```bash
duk ls --sectors="Technology,Healthcare"
```

Retrieves all securities in either Technology or Healthcare sectors.

#### Example 9: Screen by Industry

```bash
duk ls --industries=Software
```

Retrieves all securities in the Software industry.

#### Example 10: Screen by Multiple Industries

```bash
duk ls --industries="Software,Pharmaceuticals,Banking"
```

Retrieves all securities in Software, Pharmaceuticals, or Banking industries.

#### Example 11: Screen by Price Range

```bash
duk ls --price=>50 --price=<200
```

**Note**: You cannot specify both greater than and less than for the same parameter in a single call. To get a range, you would need to filter the results separately.

Use `--price=>50` to get securities priced above $50:
```bash
duk ls --price=>50
```

Or use `--price=<200` to get securities priced below $200:
```bash
duk ls --price=<200
```

#### Example 12: Screen by Market Capitalization

```bash
duk ls --market-cap=>1000000000
```

Retrieves securities with market cap greater than $1 billion.

#### Example 13: Combined Screening

```bash
duk ls --sectors=Technology --price=>100 --market-cap=>10000000000
```

Retrieves Technology sector securities priced above $100 with market cap above $10 billion.

#### Example 14: Screen with Exchange Filter

```bash
duk ls --sectors=Technology --exchange=NASDAQ
```

Retrieves Technology sector securities listed on NASDAQ.

#### Example 15: Screen for High Beta Stocks

```bash
duk ls --beta=>1.5 --sectors=Technology
```

Retrieves Technology sector securities with beta greater than 1.5.

#### Example 16: Screen for Dividend Stocks

```bash
duk ls --dividend=>3.0 --sectors="Utilities,Real Estate"
```

Retrieves Utilities and Real Estate securities with dividend greater than 3.0.

#### Example 17: Screen with Volume Filter

```bash
duk ls --volume=>5000000 --price=>50
```

Retrieves securities with trading volume above 5 million and price above $50.

#### Example 18: Screen and Save Results

```bash
duk ls --sectors=Technology --price=>100 -o tech_stocks.csv
```

Screens for Technology stocks priced above $100 and saves to file.

#### Example 19: Quiet Mode Screening

```bash
duk ls --sectors=Healthcare --price=>50 -o healthcare.csv -q
```

Screens Healthcare stocks and saves to file without printing to stdout.

#### Example 20: JSON Output with Screening

```bash
duk ls --sectors=Technology --market-cap=>1000000000 --json
```

Screens Technology stocks with large market cap and outputs in JSON format.

## Output Format

The command can output data in two formats: CSV (default) or JSON.

### CSV Output Format

CSV output has the following characteristics:

- Column names are based on the list type or screening results
- Screening results are sorted alphabetically by company name
- Numeric values are not quoted

#### Actively Trading Securities (Default)

```csv
symbol,name
AAPL,Apple Inc.
MSFT,Microsoft Corporation
GOOGL,Alphabet Inc.
```

#### Sectors (--sectors flag)

```csv
sector_id,sector_hash,sector_name
1,8f5e9,Financial Services
2,84bf8,Healthcare
3,4b3b7,Technology
```

#### Industries (--industries flag)

```csv
industry_id,industry_hash,industry_name
1,3b4a2,Banking
2,9c1e5,Pharmaceuticals
3,2f0d7,Software
```

#### Screening Results

```csv
symbol,companyName,sector,industry,price,marketCap,...
AAPL,Apple Inc.,Technology,Consumer Electronics,150.0,2500000000000,...
MSFT,Microsoft Corporation,Technology,Software,300.0,2200000000000,...
```

### JSON Output Format

JSON output has the following characteristics:

- Array of objects, one per record
- Column names are based on the list type or screening results
- Screening results are sorted alphabetically by company name

#### Actively Trading Securities (Default)

```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc."
  },
  {
    "symbol": "MSFT",
    "name": "Microsoft Corporation"
  }
]
```

#### Sectors (--sectors flag)

```json
[
  {
    "sector_id": 1,
    "sector_hash": "8f5e9",
    "sector_name": "Financial Services"
  },
  {
    "sector_id": 2,
    "sector_hash": "84bf8",
    "sector_name": "Healthcare"
  }
]
```

#### Industries (--industries flag)

```json
[
  {
    "industry_id": 1,
    "industry_hash": "3b4a2",
    "industry_name": "Banking"
  },
  {
    "industry_id": 2,
    "industry_hash": "9c1e5",
    "industry_name": "Pharmaceuticals"
  }
]
```

#### Screening Results

```json
[
  {
    "symbol": "AAPL",
    "companyName": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "price": 150.0,
    "marketCap": 2500000000000
  },
  {
    "symbol": "MSFT",
    "companyName": "Microsoft Corporation",
    "sector": "Technology",
    "industry": "Software",
    "price": 300.0,
    "marketCap": 2200000000000
  }
]
```

## Error Handling

The command will exit with an error (exit code 1) in the following cases:

1. **Missing API Key**: FMP API key not configured
   ```
   Error: FMP API key not configured. Set FMP_API_KEY environment variable
   or add fmp_key to [api] section in ~/.dukrc
   ```

2. **Multiple List Types**: Both --sectors and --industries flags used together
   ```
   Error: Only one of --sectors or --industries can be specified
   ```

3. **Multiple Output Formats**: Both --csv and --json specified
   ```
   Error: Only one of --csv or --json can be specified
   ```

4. **Invalid Filter Format**: Filter value without > or < operator
   ```
   Error: Filter value must start with > or < operator: 100
   ```

5. **Invalid Numeric Value**: Non-numeric value in filter
   ```
   Error: Invalid numeric value: abc
   ```

6. **API Error**: Failed to fetch data from the API
   ```
   Error: Failed to fetch list data: <error message>
   ```

When no data is available, the command exits successfully (exit code 0) with a message:
```
No data found
```

## Tips and Best Practices

1. **Use Environment Variables**: Set `FMP_API_KEY` as an environment variable to avoid storing sensitive data in config files:
   ```bash
   export FMP_API_KEY="your_api_key_here"
   duk ls
   ```

2. **Combine with Unix Tools**: The CSV output can be easily processed with standard Unix tools:
   ```bash
   # Count securities
   duk ls | wc -l
   
   # Filter with grep
   duk ls | grep "Apple"
   
   # Search for specific symbols
   duk ls | grep "^AAPL,"
   ```

3. **Use JSON with jq**: JSON output works well with jq for advanced data processing:
   ```bash
   # Extract all symbols
   duk ls --json | jq '.[].symbol'
   
   # Filter by name
   duk ls --json | jq '.[] | select(.name | contains("Apple"))'
   
   # Count records
   duk ls --json | jq 'length'
   
   # Screen and extract specific fields
   duk ls --sectors=Technology --price=>100 --json | jq '.[] | {symbol, price}'
   ```

4. **Quiet Mode for Scripts**: Use `-q` flag in scripts to suppress data output while still getting status messages:
   ```bash
   duk ls --sectors=Technology --price=>50 -o tech.csv -q && echo "Screening complete"
   ```

5. **Verbose Mode for Troubleshooting**: Use `-v` flag to see detailed logging when debugging issues:
   ```bash
   duk ls --sectors=Technology --price=>100 -v
   ```

6. **Use Limit for Testing**: Use `--limit` to get a small sample when testing screening queries:
   ```bash
   duk ls --sectors=Technology --price=>100 -n 10
   ```

7. **Screening Multiple Sectors or Industries**: When you want to screen across multiple sectors or industries, use comma-separated values:
   ```bash
   duk ls --sectors="Technology,Healthcare,Financial Services" --market-cap=>5000000000
   ```

8. **Understanding Comparison Operators**: Always use `>` or `<` prefix for numeric filters:
   - `--price=>100` means "price greater than 100"
   - `--price=<100` means "price less than 100"
   - `--price=100` will produce an error

## Related Functions

- `actively_trading_list_api()`: API function for actively trading securities
- `sector_list_api()`: API function for sectors
- `industry_list_api()`: API function for industries
- `screen_securities()`: Function for screening securities with multiple filters
- `_screen_securities()`: Internal API screening function

## See Also

- Main duk documentation: `man duk`
- [ph Command Documentation](ph_command.md)
- [yc Command Documentation](yc_command.md)
