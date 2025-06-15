#!/usr/bin/env python3
"""
Standalone build script for the duk package.

This script creates distribution packages without relying on the `build` module,
making it more resilient to network issues during CI/CD.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0

def build_package():
    """Build the package using setuptools directly."""
    repo_dir = Path(__file__).parent.parent
    
    print(f"Building package in: {repo_dir}")
    
    # Clean previous builds
    print("Cleaning previous builds...")
    for dir_name in ["build", "dist", "*.egg-info"]:
        for path in repo_dir.glob(dir_name):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
    
    # Build source distribution
    print("\nBuilding source distribution...")
    if not run_command("python setup.py sdist", cwd=repo_dir):
        print("Failed to build source distribution")
        return False
    
    # Build wheel distribution
    print("\nBuilding wheel distribution...")
    if not run_command("python setup.py bdist_wheel", cwd=repo_dir):
        print("Failed to build wheel distribution")
        return False
    
    # List created files
    dist_dir = repo_dir / "dist"
    if dist_dir.exists():
        print(f"\nBuilt packages in {dist_dir}:")
        for file in dist_dir.iterdir():
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    print("\n✅ Package build completed successfully!")
    return True

def create_setup_py():
    """Create a simple setup.py for fallback building."""
    setup_py_content = '''#!/usr/bin/env python3
"""
Fallback setup.py for building the duk package.
"""

from setuptools import setup, find_packages
import os

# Read version from pyproject.toml or __init__.py
def get_version():
    try:
        import tomllib
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except:
        # Fallback to reading from __init__.py
        init_file = os.path.join("src", "duk", "__init__.py")
        with open(init_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="duk",
    version=get_version(),
    description="TurningBull Data Utility Knife - CLI tool for downloading financial data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="TurningBull",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.3.0",
        "click>=8.0.0",
        "python-dateutil>=2.8.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "build>=0.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "duk=duk.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
'''
    
    repo_dir = Path(__file__).parent.parent
    setup_py_path = repo_dir / "setup.py"
    
    if not setup_py_path.exists():
        print("Creating fallback setup.py...")
        with open(setup_py_path, "w") as f:
            f.write(setup_py_content)
        print(f"Created {setup_py_path}")
    
    return setup_py_path.exists()

if __name__ == "__main__":
    # Ensure we have a setup.py for fallback
    create_setup_py()
    
    # Build the package
    success = build_package()
    sys.exit(0 if success else 1)