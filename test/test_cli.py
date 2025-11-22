"""
Unit tests for CLI module.
"""

import os
import tempfile

from click.testing import CliRunner

from duk.cli import main


class TestCLI:
    """Test cases for CLI functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert (
            "duk - A CLI tool for downloading markets and financial data"
            in result.output
        )

    def test_cli_with_custom_config(self):
        """Test CLI with custom config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('default_output_dir = "/tmp/output"\n')
                f.write('default_output_type = "json"\n')
                f.write('log_level = "debug"\n')
                f.write('log_dir = "/tmp/logs"\n')

            runner = CliRunner()
            result = runner.invoke(main, ["--config", config_path, "--help"])

            # Should succeed with custom config
            assert result.exit_code == 0

    def test_cli_without_config(self):
        """Test CLI without config file (should use defaults)."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        # Should still work with defaults
        assert result.exit_code == 0
