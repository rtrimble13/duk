"""
Main CLI entry point for duk
"""

import sys

import click

from duk import __version__
from duk.cli.ph_cmd import ph
from duk.config import get_config
from duk.logger import setup_logging


@click.group()
@click.version_option(version=__version__)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(),
    help="Path to configuration file (default: ~/.dukrc)",
)
@click.pass_context
def cli(ctx, config_path):
    """
    A CLI tool for downloading financial market data and performing data
    preprocessing.

    For more information, see: https://github.com/rtrimble13/duk
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)

    # Initialize configuration
    config = get_config(config_path)
    ctx.obj["config"] = config

    # Setup logging
    setup_logging(config)


# Add subcommands
cli.add_command(ph)


def main():
    """
    Main entry point for duk CLI
    """
    return cli(obj={})


if __name__ == "__main__":
    sys.exit(main())
