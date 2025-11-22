"""
Main CLI entry point for duk
"""

import argparse
import sys

from duk import __version__
from duk.cli.ph_cmd import add_ph_parser
from duk.config import get_config
from duk.logger import setup_logging


def main():
    """
    Main entry point for duk CLI
    """
    # Create main parser
    parser = argparse.ArgumentParser(
        prog="duk",
        description=(
            "A CLI tool for downloading financial market data and "
            "performing data preprocessing"
        ),
        epilog="For more information, see: https://github.com/rtrimble13/duk",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        help="Path to configuration file (default: ~/.dukrc)",
    )

    # Create subparsers for subcommands
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Available subcommands",
        dest="subcommand",
        help="Subcommand help",
    )

    # Add ph subcommand
    add_ph_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Initialize configuration
    config_path = args.config_path if hasattr(args, "config_path") else None
    config = get_config(config_path)

    # Setup logging
    setup_logging(config)

    # Handle subcommand
    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
