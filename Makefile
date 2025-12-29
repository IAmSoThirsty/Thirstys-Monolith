.PHONY: help setup install test lint format clean docker-build docker-run docker-test

help:
	@echo "Thirsty's Monolith - Available commands:"
	@echo "  make setup         - Create virtual environment and install dependencies"
	@echo "  make install       - Install package in development mode"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run linters (flake8, pylint)"
	@echo "  make format        - Format code with black"
	@echo "  make clean         - Remove build artifacts and cache files"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Schematic Guardian in Docker"
	@echo "  make docker-test   - Run tests in Docker"

setup:
	@echo "🏗️  Setting up environment..."
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip setuptools wheel
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && pip install -r requirements-dev.txt
	@echo "✅ Setup complete! Activate with: source .venv/bin/activate"

install:
	@echo "📦 Installing package..."
	pip install -e .
	@echo "✅ Package installed"

test:
	@echo "🧪 Running tests..."
	pytest --cov=src --cov-report=html --cov-report=term-missing -v

lint:
	@echo "🔍 Running linters..."
	flake8 src/ tests/
	pylint src/

format:
	@echo "✨ Formatting code..."
	black src/ tests/

clean:
	@echo "🧹 Cleaning up..."
	rm -rf .venv
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.bak" -delete
	@echo "✅ Cleanup complete"

docker-build:
	@echo "🐳 Building Docker image..."
	docker-compose build
	@echo "✅ Docker image built"

docker-run:
	@echo "🐳 Running Schematic Guardian in Docker..."
	docker-compose up schematic-guardian

docker-test:
	@echo "🐳 Running tests in Docker..."
	docker-compose up test
