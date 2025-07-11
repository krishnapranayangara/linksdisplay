# Makefile for Link Organizer Backend

.PHONY: help install test test-coverage lint format clean run dev setup-db

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean up cache and temporary files"
	@echo "  run          - Run the application in production mode"
	@echo "  dev          - Run the application in development mode"
	@echo "  setup-db     - Initialize database and create tables"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Run tests
test:
	@echo "Running tests..."
	pytest

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	pytest --cov=. --cov-report=html --cov-report=term-missing

# Run linting
lint:
	@echo "Running linting checks..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Format code
format:
	@echo "Formatting code..."
	black .
	isort .

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Run in production mode
run:
	@echo "Starting production server..."
	gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run in development mode
dev:
	@echo "Starting development server..."
	FLASK_ENV=development python app.py

# Setup database
setup-db:
	@echo "Setting up database..."
	python -c "from app import init_db; init_db()"

# Create test database
setup-test-db:
	@echo "Setting up test database..."
	createdb -U admin link_organizer_test || true
	FLASK_ENV=testing python -c "from app import create_app, db; app = create_app('testing'); app.app_context().push(); db.create_all()"

# Run all checks
check: lint test
	@echo "All checks passed!"

# Development setup
dev-setup: install setup-db
	@echo "Development environment setup complete!" 