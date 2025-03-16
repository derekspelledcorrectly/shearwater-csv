.PHONY: help lint clean dev-setup venv activate run

VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

venv:  ## Create virtual environment if it doesn't exist
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)

activate: venv  ## Copy virtual environment activation command to clipboard or display it
	@if command -v pbcopy >/dev/null 2>&1; then \
		echo "source $(VENV_DIR)/bin/activate" | pbcopy && \
		echo "Activation command copied to clipboard. Paste and run to activate."; \
	else \
		echo "Run this command to activate the virtual environment:"; \
		echo "source $(VENV_DIR)/bin/activate"; \
	fi

dev-setup: venv  ## Set up development environment
	$(PIP) install -r dev_requirements.txt

run: venv  ## Run the script (args are passed through)
	$(PYTHON) shearwater_csv.py $(ARGS)

lint: dev-setup  ## Run code style checks
	$(VENV_BIN)/pycodestyle --max-line-length=120 shearwater_csv.py

clean:  ## Remove Python and editor artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type f -name "*.swp" -delete

clean-venv: clean  ## Remove virtual environment and artifacts
	rm -rf $(VENV_DIR)
