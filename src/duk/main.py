#!/usr/bin/env python3
"""
Main entry point for the duk CLI tool.
"""

import sys
import logging
from pathlib import Path

import click

from duk.commands.tr import tr_command
from duk.commands.ph import ph_command


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO

    # Create var directory if it doesn't exist
    var_dir = Path("var")
    var_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(var_dir / "duk.log"),
            (logging.StreamHandler(sys.stderr) if verbose else logging.NullHandler()),
        ],
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging to stderr")
@click.pass_context
def main(ctx, verbose):
    """duk - TurningBull Data Utility Knife

    A CLI tool for downloading financial market data and performing data
    preprocessing.

    Use 'duk <subprogram> --help' for subprogram-specific help.
    """
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# Add subcommands
main.add_command(tr_command, name="tr")
main.add_command(ph_command, name="ph")


if __name__ == "__main__":
    main()
