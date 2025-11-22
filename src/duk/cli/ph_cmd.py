"""
CLI handler for price history (ph) command
"""

import sys

from duk.api.ph import get_price_history
from duk.config import get_config
from duk.logger import get_logger

logger = get_logger("cli.ph")


def add_ph_parser(subparsers):
    """
    Add ph subcommand parser

    Args:
        subparsers: argparse subparsers object
    """
    parser = subparsers.add_parser(
        "ph",
        help="Download security price history from FMP",
        description=(
            "Download security price history from " "Financial Modeling Prep API"
        ),
    )

    # Positional argument
    parser.add_argument("symbol", help="Security symbol (e.g., IBM, AAPL)")

    # Optional arguments
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=5,
        help="Number of most recent data points to return (default: 5)",
    )

    parser.add_argument(
        "-f",
        "--from-date",
        dest="from_date",
        help="Start date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "-t",
        "--to-date",
        dest="to_date",
        help="End date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: stdout)",
    )

    parser.add_argument(
        "--fields",
        help=(
            "Comma-separated list of fields to display " "(default: date,close,volume)"
        ),
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json", "table"],
        default="table",
        help="Output format (default: table)",
    )

    parser.set_defaults(func=handle_ph_command)


def handle_ph_command(args):
    """
    Handle ph command execution

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Executing ph command for symbol: {args.symbol}")

    # Get configuration
    config = get_config()

    # Get API key
    api_key = config.get_fmp_api_key()
    if not api_key or api_key == "YOUR_FMP_API_KEY_HERE":
        logger.error("FMP API key not configured")
        print("Error: FMP API key not configured", file=sys.stderr)
        print(
            "Please set your API key in ~/.dukrc or provide it "
            "via environment variable",
            file=sys.stderr,
        )
        return 1

    try:
        # Get price history
        df = get_price_history(
            symbol=args.symbol,
            api_key=api_key,
            limit=args.limit,
            from_date=args.from_date,
            to_date=args.to_date,
        )

        if df.empty:
            logger.warning(f"No data found for symbol: {args.symbol}")
            print(f"No data found for symbol: {args.symbol}", file=sys.stderr)
            return 1

        # Select fields to display
        if args.fields:
            fields = [f.strip() for f in args.fields.split(",")]
            # Filter to only include fields that exist in the dataframe
            available_fields = [f for f in fields if f in df.columns]
            if not available_fields:
                logger.error("None of the specified fields exist in the data")
                print(
                    "Error: None of the specified fields exist in the data",
                    file=sys.stderr,
                )
                return 1
            df = df[available_fields]
        else:
            # Default fields
            default_fields = ["date", "close", "volume"]
            available_fields = [f for f in default_fields if f in df.columns]
            if available_fields:
                df = df[available_fields]

        # Format and output
        if args.output:
            # Write to file
            logger.info(f"Writing output to file: {args.output}")
            if args.format == "csv":
                df.to_csv(args.output, index=False)
            elif args.format == "json":
                df.to_json(args.output, orient="records", indent=2)
            else:
                with open(args.output, "w") as f:
                    f.write(df.to_string(index=False))
            logger.info(f"Output written to {args.output}")
        else:
            # Write to stdout
            if args.format == "csv":
                print(df.to_csv(index=False), end="")
            elif args.format == "json":
                print(df.to_json(orient="records", indent=2))
            else:
                print(df.to_string(index=False))

        logger.info("ph command completed successfully")
        return 0

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
