.PHONY: build install test dist doc format clean

# Build the project using miniconda framework with 'duk' environment
build:
	@echo "Building duk project using miniconda framework..."
	@if ! command -v conda >/dev/null 2>&1; then \
		echo "Error: conda not found. Please install miniconda3 or anaconda first."; \
		exit 1; \
	fi
	@if conda env list | grep -q "^duk "; then \
		echo "Environment 'duk' exists. Updating..."; \
		conda env update -f environment.yml; \
	else \
		echo "Creating new environment 'duk'..."; \
		conda env create -f environment.yml; \
	fi
	@echo ""
	@echo "Build complete! To use duk:"
	@echo "  conda activate duk"
	@echo "  pip install -e ."

# Build standalone application and install to ~/.local
install:
	@echo "Building and installing duk as a standalone application..."
	@# Build the package if not already built
	@if [ ! -f dist/duk-0.1.0-py3-none-any.whl ]; then \
		echo "Building package first..."; \
		python -m build 2>/dev/null || python scripts/build.py; \
	fi
	@# Install to ~/.local
	pip install --user dist/duk-0.1.0-py3-none-any.whl
	@# Copy configuration file
	@mkdir -p ~/.duk
	@cp etc/duk.rc ~/.duk/duk.rc
	@echo "Installation complete!"
	@echo "- duk CLI installed to ~/.local/bin/duk"
	@echo "- Configuration copied to ~/.duk/duk.rc"
	@echo ""
	@echo "Make sure ~/.local/bin is in your PATH to use the duk command."

# Run the test suite
test:
	python -m pytest test/ -v

# Build conda distribution
dist:
	@echo "Building conda distribution package..."
	@if ! command -v conda-build >/dev/null 2>&1; then \
		echo "Error: conda-build not found. Install with: conda install conda-build"; \
		exit 1; \
	fi
	conda-build conda-recipe/

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

# Run black and flake8 checks
format:
	black src/ test/
	flake8 src/ test/

# Clean build artifacts and remove local installation
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Removing local installation..."
	@if command -v pip >/dev/null 2>&1; then \
		pip uninstall -y duk 2>/dev/null || true; \
	fi
	@if [ -f ~/.local/bin/duk ]; then \
		rm -f ~/.local/bin/duk; \
		echo "Removed ~/.local/bin/duk"; \
	fi
	@if [ -f ~/.local/share/man/man1/duk.1 ]; then \
		rm -f ~/.local/share/man/man1/duk.1; \
		echo "Removed ~/.local/share/man/man1/duk.1"; \
	fi
	@echo "Clean complete!"