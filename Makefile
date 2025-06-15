.PHONY: install test clean lint format build publish help

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
	@echo "  publish    - Publish to PyPI (requires credentials)"

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

publish:
	python -m twine upload dist/*