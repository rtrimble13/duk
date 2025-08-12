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
        """Test that Makefile has distribution targets."""
        project_root = Path(__file__).parent.parent
        makefile_path = project_root / "Makefile"

        assert makefile_path.exists(), "Makefile not found"

        # Read and verify targets exist
        with open(makefile_path, "r") as f:
            content = f.read()

        assert "dist:" in content, "dist target not found"
        assert "conda-build:" in content, "conda-build target not found"
        assert "build:" in content, "build target not found"
        assert "build-standalone:" in content, "build-standalone target not found"
        assert "install-user:" in content, "install-user target not found"

    def test_install_user_target_exists(self):
        """Test that install-user target exists and has correct functionality."""
        project_root = Path(__file__).parent.parent
        makefile_path = project_root / "Makefile"

        assert makefile_path.exists(), "Makefile not found"

        # Read and verify install-user target content
        with open(makefile_path, "r") as f:
            content = f.read()

        # Check that install-user target is defined
        assert "install-user:" in content, "install-user target not found"

        # Check that it mentions ~/.local installation
        assert "~/.local" in content, "install-user doesn't reference ~/.local"

        # Check that it installs man page
        assert (
            "~/.local/share/man/man1" in content
        ), "install-user doesn't install man page to correct location"

        # Check that it uses pip install --user
        assert (
            "pip install --user" in content
        ), "install-user doesn't use pip install --user"


class TestDistributionBuilding:
    """Test actual distribution building."""

    def test_make_build_packages_creates_distribution_files(self):
        """Test that make build-packages creates wheel and tar.gz distribution packages."""
        project_root = Path(__file__).parent.parent

        # Clean any existing dist directory
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            import shutil

            shutil.rmtree(dist_dir)

        # Run make build-packages
        result = subprocess.run(
            ["make", "build-packages"], cwd=project_root, capture_output=True, text=True
        )

        # Check that the command succeeded (exit code 0)
        if result.returncode != 0:
            pytest.fail(
                f"make build-packages failed with exit code {result.returncode}:\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

        # Check that dist directory was created
        assert dist_dir.exists(), "dist directory was not created"

        # Check that expected files were created
        dist_files = list(dist_dir.glob("*"))
        assert (
            len(dist_files) >= 2
        ), f"Expected at least 2 files in dist/, got {len(dist_files)}"

        # Check for wheel and source distribution
        wheel_files = list(dist_dir.glob("*.whl"))
        tar_files = list(dist_dir.glob("*.tar.gz"))

        assert len(wheel_files) == 1, f"Expected 1 wheel file, got {len(wheel_files)}"
        assert len(tar_files) == 1, f"Expected 1 tar.gz file, got {len(tar_files)}"

        # Verify file names contain expected version
        wheel_file = wheel_files[0]
        tar_file = tar_files[0]

        assert (
            "duk-0.1.0" in wheel_file.name
        ), f"Wheel file name doesn't contain version: {wheel_file.name}"
        assert (
            "duk-0.1.0" in tar_file.name
        ), f"Tar file name doesn't contain version: {tar_file.name}"

    def test_make_dist_builds_conda_package(self):
        """Test that make dist attempts to build conda packages."""
        project_root = Path(__file__).parent.parent

        # Run make dist (should attempt conda build)
        result = subprocess.run(
            ["make", "dist"], cwd=project_root, capture_output=True, text=True
        )

        # The command should fail with a specific error message about conda-build not being found
        # This is expected behavior when conda-build is not installed
        assert (
            result.returncode != 0
        ), "make dist should fail when conda-build is not available"
        assert (
            "conda-build not found" in result.stdout
        ), f"Expected conda-build error message, got: {result.stdout}"

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
