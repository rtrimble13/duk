.PHONY: build install test fmt dist doc clean

# Default target
help:
	@echo "Available targets:"
	@echo "  build    - Build the project using miniconda with 'duk' environment"
	@echo "  install  - Build and install duk as a standalone application to ~/.local"
	@echo "  test     - Run unit tests using pytest framework"
	@echo "  dist     - Build conda distribution package"
	@echo "  doc	  - Install man pages"
	@echo "  clean    - Clean build artifacts and remove local installation"

# Build the project using miniconda framework with 'duk' environment
build:
	@echo "Creating/using conda env 'duk' and installing dependencies"
	@if command -v conda >/dev/null 2>&1; then \
		if ! conda env list | awk '{print $$1}' | grep -qx duk; then \
			echo "Creating conda env 'duk'..."; \
			conda create -n duk python=3.13 -y; \
		else \
			echo "Conda env 'duk' already exists."; \
		fi; \
		echo "Installing package info 'duk'..."; \
		conda activate duk; \
		python -m pip install -e .[dev]; \
	else \
		echo "conda not found, falling back to system pip"; \
		python -m pip install -e .[dev]; \
	fi

# Build standalone application and install to ~/.local
install:
	python -m pip install .

# Run the test suite
test:
	@echo "Running tests in 'duk' conda environment"
	@if command -v conda >/dev/null 2>&1; then \
		conda run -n duk python -m pytest test/ -v; \
	else \
		echo "conda not found, using system python"; \
		python -m pytest test/ -v; \
	fi

fmt:
	python -m black src/ test/
	python -m isort src/ test/
	python -m flake8 src/ test/ --max-line-length=80

# Build conda distribution
dist:
	python -m pip install --upgrade build
	python -m build

# Install man pages
doc:
	@echo "Installing man pages..."
	@mkdir -p ~/.local/share/man/man1
	@cp doc/duk.1 ~/.local/share/man/man1/duk.1
	@if command -v mandb >/dev/null 2>&1; then \
		mandb -q ~/.local/share/man 2>/dev/null || true; \
	fi
	@echo "Man page installed to ~/.local/share/man/man1/duk.1"
	@echo "You can now use 'man duk' to view the documentation"

# Clean build artifacts and remove local installation
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
