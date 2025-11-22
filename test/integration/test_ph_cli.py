"""
Integration tests for ph CLI command
"""

import subprocess
import sys
import tempfile


class TestPhCLI:
    """Integration tests for ph command"""

    def test_ph_command_help(self):
        """Test that ph command help works"""
        result = subprocess.run(
            [sys.executable, "-m", "duk.cli.main", "ph", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Download security price history" in result.stdout
        assert "symbol" in result.stdout

    def test_ph_command_without_api_key(self):
        """Test that ph command fails gracefully without API key"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as f:
            f.write("[api]\n")
            f.write('fmp_api_key = ""\n')
            config_path = f.name

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "duk.cli.main",
                "-c",
                config_path,
                "ph",
                "IBM",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "API key not configured" in result.stderr

    def test_main_command_version(self):
        """Test that version flag works"""
        result = subprocess.run(
            [sys.executable, "-m", "duk.cli.main", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout

    def test_main_command_help(self):
        """Test that main help works"""
        result = subprocess.run(
            [sys.executable, "-m", "duk.cli.main", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "duk" in result.stdout
        assert "ph" in result.stdout
