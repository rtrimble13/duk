#!/usr/bin/env python3
"""
Fallback setup.py for building the duk package.
"""

from setuptools import setup, find_packages
import os

# Read version from pyproject.toml or __init__.py
def get_version():
    try:
        # Try tomllib first (Python 3.11+)
        import tomllib
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except ImportError:
        # Python < 3.11, try tomli
        try:
            import tomli
            with open("pyproject.toml", "rb") as f:
                data = tomli.load(f)
                return data["project"]["version"]
        except ImportError:
            # Fallback to manual parsing
            pass
    except:
        pass
    
    # Manual parsing fallback for maximum compatibility
    try:
        with open("pyproject.toml", "r") as f:
            for line in f:
                if line.startswith('version = '):
                    return line.split('=')[1].strip().strip('"').strip("'")
    except:
        pass
    
    # Final fallback to reading from __init__.py
    try:
        init_file = os.path.join("src", "duk", "__init__.py")
        with open(init_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except:
        pass
    
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
        "configistate>=1.0.0",
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
