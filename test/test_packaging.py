"""
Test packaging configuration and distribution building.

These tests verify that the packaging configuration is correct and that
distribution packages can be built for both PyPI and conda.
"""

import os
import subprocess
from pathlib import Path

import pytest


class TestPackagingConfiguration:
    """Test packaging configuration files."""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists and has required fields."""
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        assert pyproject_path.exists(), "pyproject.toml not found"

        # Read and verify basic content
        with open(pyproject_path, "r") as f:
            content = f.read()

        assert "[build-system]" in content, "build-system section not found"
        assert "[project]" in content, "project section not found"
        assert 'name = "duk"' in content, "project name not found"
        assert 'version = "0.1.0"' in content, "project version not found"
        assert "[project.scripts]" in content, "entry points not found"
        assert 'duk = "duk.main:main"' in content, "CLI entry point not configured"

    def test_conda_recipe_exists(self):
        """Test that conda recipe exists and has required fields."""
        project_root = Path(__file__).parent.parent
        meta_yaml_path = project_root / "conda-recipe" / "meta.yaml"

        assert meta_yaml_path.exists(), "conda-recipe/meta.yaml not found"

        # Read and verify basic content
        with open(meta_yaml_path, "r") as f:
            content = f.read()

        assert "name: {{ name|lower }}" in content, "package name template not found"
        assert "version: {{ version }}" in content, "version template not found"
        assert "source:" in content, "source section not found"
        assert "build:" in content, "build section not found"
        assert "requirements:" in content, "requirements section not found"
        assert "test:" in content, "test section not found"
        assert "about:" in content, "about section not found"

    def test_makefile_has_dist_targets(self):
        """Test that Makefile has the required targets."""
        project_root = Path(__file__).parent.parent
        makefile_path = project_root / "Makefile"

        assert makefile_path.exists(), "Makefile not found"

        # Read and verify targets exist
        with open(makefile_path, "r") as f:
            content = f.read()

        # Check for the 7 required targets
        assert "build:" in content, "build target not found"
        assert "install:" in content, "install target not found"
        assert "test:" in content, "test target not found"
        assert "dist:" in content, "dist target not found"
        assert "doc:" in content, "doc target not found"
        assert "format:" in content, "format target not found"
        assert "clean:" in content, "clean target not found"

    def test_install_target_functionality(self):
        """Test that install target exists and has correct functionality."""
        project_root = Path(__file__).parent.parent
        makefile_path = project_root / "Makefile"

        assert makefile_path.exists(), "Makefile not found"

        # Read and verify install target content
        with open(makefile_path, "r") as f:
            content = f.read()

        # Check that install target is defined
        assert "install:" in content, "install target not found"

        # Check that it mentions ~/.local installation
        assert "~/.local" in content, "install doesn't reference ~/.local"

        # Check that it installs man page
        assert (
            "~/.local/share/man/man1" in content
        ), "install doesn't install man page to correct location"

        # Check that it uses pip install --user
        assert (
            "pip install --user" in content
        ), "install doesn't use pip install --user"

        # Check that it copies configuration file
        assert "~/.duk/duk.rc" in content, "install should copy config file"


class TestDistributionBuilding:
    """Test actual distribution building."""

    def test_make_install_creates_distribution_files(self):
        """Test that make install creates and uses wheel packages."""
        project_root = Path(__file__).parent.parent

        # Test the install target which should build packages (dry run)
        result = subprocess.run(
            ["make", "-n", "install"], cwd=project_root, capture_output=True, text=True
        )

        # Check that the dry run succeeds and shows expected commands
        assert result.returncode == 0, f"make -n install failed: {result.stderr}"
        
        # Check that it references building packages and installing
        build_command_present = ("python -m build" in result.stdout or 
                               "python scripts/build.py" in result.stdout)
        assert build_command_present, "install should build packages"
        assert "pip install --user" in result.stdout, "install should use pip install --user"

    def test_make_dist_builds_conda_package(self):
        """Test that make dist builds conda package successfully when conda-build is available."""
        project_root = Path(__file__).parent.parent

        # Run make dist (should build conda package)
        result = subprocess.run(
            ["make", "dist"], cwd=project_root, capture_output=True, text=True
        )

        # The dist command should succeed since conda-build is available in the test environment
        assert result.returncode == 0, f"make dist should succeed when conda-build is available: {result.stderr}"
        assert "conda-build" in result.stdout, "dist should use conda-build"

    def test_conda_recipe_is_valid(self):
        """Test that conda recipe can be parsed (syntax check)."""
        project_root = Path(__file__).parent.parent
        meta_yaml_path = project_root / "conda-recipe" / "meta.yaml"

        # Try to parse the YAML file
        try:
            import yaml
            import re

            with open(meta_yaml_path, "r") as f:
                content = f.read()

            # Replace Jinja2 template variables with dummy values for parsing
            # Handle {% set %} statements
            content = re.sub(r"{% set .* %}", "", content)

            # Replace template variables
            content = content.replace("{{ name|lower }}", "duk")
            content = content.replace("{{ version }}", "0.1.0")
            content = content.replace("{{ PYTHON }}", "python")

            # Parse YAML
            data = yaml.safe_load(content)

            # Verify required sections exist
            assert "package" in data, "package section missing"
            assert "source" in data, "source section missing"
            assert "build" in data, "build section missing"
            assert "requirements" in data, "requirements section missing"
            assert "test" in data, "test section missing"
            assert "about" in data, "about section missing"

        except ImportError:
            pytest.skip("PyYAML not available for conda recipe validation")
        except yaml.YAMLError as e:
            pytest.fail(f"conda recipe YAML is invalid: {e}")

    def test_setup_py_fallback_exists(self):
        """Test that setup.py fallback exists for standalone builds."""
        project_root = Path(__file__).parent.parent
        setup_py_path = project_root / "setup.py"

        assert setup_py_path.exists(), "setup.py not found"

        # Verify it's executable
        assert os.access(setup_py_path, os.X_OK), "setup.py is not executable"

        # Read and verify basic content
        with open(setup_py_path, "r") as f:
            content = f.read()

        assert "from setuptools import setup" in content, "setuptools import not found"
        assert 'name="duk"' in content, "package name not found"
        assert "entry_points" in content, "entry points not found"
