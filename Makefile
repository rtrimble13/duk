.PHONY: install test clean lint format build publish doc help

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