# Makefile for the Swarm Agent project

# Python interpreter
PYTHON = python3

# Virtual environment
VENV = venv
VENV_ACTIVATE = . $(VENV)/bin/activate

# Install dependencies
install:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "Activating virtual environment and installing dependencies..."
	$(VENV_ACTIVATE) && pip install -r requirements.txt

# Run the FastAPI server
serve:
	$(VENV_ACTIVATE) && uvicorn app.main:app --reload

# Clean up pyc files and the virtual environment
clean:
	find . -type f -name "*.pyc" -delete
	rm -rf __pycache__
	rm -rf $(VENV)

# Run tests (assuming you'll add tests in the future)
test:
	$(VENV_ACTIVATE) && pytest

# Format code using black (you might want to add this to your requirements.txt)
format:
	$(VENV_ACTIVATE) && black .

# Lint code using flake8 (you might want to add this to your requirements.txt)
lint:
	$(VENV_ACTIVATE) && flake8 .

.PHONY: install serve clean test format lint
