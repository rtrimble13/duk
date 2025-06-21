.PHONY: install test clean lint format build build-standalone dist conda-build publish doc help

# Default target
help:
	@echo "Available targets:"
	@echo "  install    - Install the package in development mode"
	@echo "  test       - Run unit tests"
	@echo "  clean      - Clean build artifacts"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code with black"
	@echo "  build      - Build distribution packages"
	@echo "  build-standalone - Build packages using fallback method"
	@echo "  dist       - Build distribution packages (alias for build)"
	@echo "  conda-build - Build conda package"
	@echo "  publish    - Publish to PyPI (requires credentials)"
	@echo "  doc        - Install man pages"

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