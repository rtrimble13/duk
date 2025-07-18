.PHONY: install test clean lint format build build-standalone dist conda-build publish doc help dev env-create env-update env-export env-remove

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install the package in development mode"
	@echo "  test          - Run unit tests"
	@echo "  clean         - Clean build artifacts"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code with black"
	@echo "  build         - Build distribution packages"
	@echo "  build-standalone - Build packages using fallback method"
	@echo "  dist          - Build distribution packages (alias for build)"
	@echo "  conda-build   - Build conda package"
	@echo "  publish       - Publish to PyPI (requires credentials)"
	@echo "  doc           - Install man pages"
	@echo ""
	@echo "Conda environment targets:"
	@echo "  dev           - Create/update conda development environment"
	@echo "  env-create    - Create conda environment from environment.yml"
	@echo "  env-update    - Update existing conda environment"
	@echo "  env-export    - Export current environment to environment.yml"
	@echo "  env-remove    - Remove the conda development environment"

install:
	pip install -e .[dev]

test:
	python -m pytest test/ -v

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 src/ test/
	black --check src/ test/

format:
	black src/ test/

build:
	python -m build

build-standalone:
	python scripts/build.py

dist:
	@echo "Building distribution packages..."
	@if python -m build --version >/dev/null 2>&1; then \
		echo "Using standard build method..."; \
		if ! python -m build; then \
			echo "Standard build failed, falling back to standalone method..."; \
			python scripts/build.py; \
		fi; \
	else \
		echo "Using standalone build method..."; \
		python scripts/build.py; \
	fi

conda-build:
	@echo "Building conda package..."
	@if ! command -v conda-build >/dev/null 2>&1; then \
		echo "Error: conda-build not found. Install with: conda install conda-build"; \
		exit 1; \
	fi
	conda-build conda-recipe/

publish:
	python -m twine upload dist/*

doc:
	@echo "Installing man pages..."
	@if [ -d /usr/local/share/man/man1 ]; then \
		sudo cp doc/duk.1 /usr/local/share/man/man1/; \
		sudo mandb -q; \
		echo "Man page installed to /usr/local/share/man/man1/duk.1"; \
	elif [ -d /usr/share/man/man1 ]; then \
		sudo cp doc/duk.1 /usr/share/man/man1/; \
		sudo mandb -q; \
		echo "Man page installed to /usr/share/man/man1/duk.1"; \
	else \
		echo "Error: Could not find system man page directory"; \
		echo "Try creating /usr/local/share/man/man1 or install manually"; \
		exit 1; \
	fi
	@echo "You can now use 'man duk' to view the documentation"

# Conda environment management targets
dev:
	@echo "Setting up conda development environment..."
	@if ! command -v conda >/dev/null 2>&1; then \
		echo "Error: conda not found. Please install miniconda3 or anaconda first."; \
		exit 1; \
	fi
	@if conda env list | grep -q "^duk-dev "; then \
		echo "Environment 'duk-dev' already exists. Updating..."; \
		conda env update -f environment.yml; \
	else \
		echo "Creating new environment 'duk-dev'..."; \
		conda env create -f environment.yml; \
	fi
	@echo ""
	@echo "Development environment ready!"
	@echo "To activate: conda activate duk-dev"
	@echo "To install duk in development mode: conda activate duk-dev && pip install -e ."
	@echo "To run tests: conda activate duk-dev && make test"

env-create:
	@echo "Creating conda environment from environment.yml..."
	@if ! command -v conda >/dev/null 2>&1; then \
		echo "Error: conda not found. Please install miniconda3 or anaconda first."; \
		exit 1; \
	fi
	conda env create -f environment.yml
	@echo "Environment created. Activate with: conda activate duk-dev"

env-update:
	@echo "Updating conda environment from environment.yml..."
	@if ! command -v conda >/dev/null 2>&1; then \
		echo "Error: conda not found. Please install miniconda3 or anaconda first."; \
		exit 1; \
	fi
	conda env update -f environment.yml
	@echo "Environment updated."

env-export:
	@echo "Exporting current conda environment to environment.yml..."
	@if ! command -v conda >/dev/null 2>&1; then \
		echo "Error: conda not found. Please install miniconda3 or anaconda first."; \
		exit 1; \
	fi
	@if [ "$$CONDA_DEFAULT_ENV" = "duk-dev" ]; then \
		conda env export > environment.yml; \
		echo "Environment exported to environment.yml"; \
	else \
		echo "Please activate the duk-dev environment first: conda activate duk-dev"; \
		exit 1; \
	fi

env-remove:
	@echo "Removing conda development environment..."
	@if ! command -v conda >/dev/null 2>&1; then \
		echo "Error: conda not found. Please install miniconda3 or anaconda first."; \
		exit 1; \
	fi
	@if conda env list | grep -q "^duk-dev "; then \
		conda env remove -n duk-dev; \
		echo "Environment 'duk-dev' removed."; \
	else \
		echo "Environment 'duk-dev' does not exist."; \
	fi