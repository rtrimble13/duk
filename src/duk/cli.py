"""
Command-line interface for duk.

This module provides the main CLI entry point and command handlers.
"""

import argparse
import sys

from duk import __version__
from duk.config import get_config
from duk.logger import get_logger, setup_logging


def cmd_ph(args):
    """
    Handle the 'ph' (price history) command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger = get_logger("cli.ph")
    logger.info(f"Executing ph command for symbol: {args.symbol}")

    try:
        from duk.ph import get_price_history

        # Get price history
        df = get_price_history(
            symbol=args.symbol,
            limit=args.limit,
            from_date=args.from_date,
            to_date=args.to_date,
            fields=args.fields,
        )

        if df.empty:
            print(f"No data found for symbol: {args.symbol}", file=sys.stderr)
            logger.warning(f"No data found for symbol: {args.symbol}")
            return 1

        # Output format
        if args.output_format == "csv":
            print(df.to_csv(index=False))
        elif args.output_format == "json":
            print(df.to_json(orient="records", date_format="iso", indent=2))
        elif args.output_format == "table":
            print(df.to_string(index=False))
        else:  # default
            print(df.to_string(index=False))

        logger.info(f"Successfully output {len(df)} records")
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"ValueError: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        logger.exception("Unexpected error in ph command")
        return 1


def create_parser():
    """
    Create and configure the argument parser.

    Returns:
        ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="duk",
        description="CLI tool for downloading market and financial data",
        epilog="For more information, see: https://github.com/rtrimble13/duk",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--config",
        help="Path to config file (default: ~/.dukrc)",
        metavar="FILE",
    )

    # Subparsers for commands
    subparsers = parser.add_subparsers(
        title="commands",
        description="Available commands",
        dest="command",
        required=True,
    )

    # Price History (ph) command
    ph_parser = subparsers.add_parser(
        "ph",
        help="Download security price history",
        description="Download security price history from FMP API",
    )

    ph_parser.add_argument(
        "symbol",
        help="Stock symbol (case-insensitive, e.g., IBM or ibm)",
    )

    ph_parser.add_argument(
        "-l",
        "--limit",
        type=int,
        help="Number of most recent data points to return (default: 5)",
        metavar="N",
    )

    ph_parser.add_argument(
        "-f",
        "--from-date",
        help="Start date for historical data (YYYY-MM-DD)",
        metavar="DATE",
    )

    ph_parser.add_argument(
        "-t",
        "--to-date",
        help="End date for historical data (YYYY-MM-DD)",
        metavar="DATE",
    )

    ph_parser.add_argument(
        "--fields",
        nargs="+",
        help="Fields to include in output (e.g., date open high low close volume)",
        metavar="FIELD",
    )

    ph_parser.add_argument(
        "-o",
        "--output-format",
        choices=["table", "csv", "json"],
        default="table",
        help="Output format (default: table)",
    )

    ph_parser.set_defaults(func=cmd_ph)

    return parser


def main():
    """
    Main entry point for the CLI.

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()

    # Initialize config
    if hasattr(args, "config") and args.config:
        config = get_config(args.config)
    else:
        config = get_config()

    # Setup logging
    setup_logging(config)
    logger = get_logger("cli")
    logger.info(f"duk v{__version__} started")
    logger.debug(f"Command: {args.command}")

    # Execute command
    if hasattr(args, "func"):
        exit_code = args.func(args)
        logger.info(f"Command completed with exit code: {exit_code}")
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
