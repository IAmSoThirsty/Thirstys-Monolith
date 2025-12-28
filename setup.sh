#!/bin/bash
# Setup script for Thirsty's Monolith

set -e

echo "🏗️  Setting up Thirsty's Monolith..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $REQUIRED_VERSION or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies (optional)
if [ "$1" == "--dev" ]; then
    echo "📥 Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Install package in editable mode
echo "🔧 Installing package in editable mode..."
pip install -e .

# Create required directories
echo "📂 Creating required directories..."
mkdir -p .github/workflows
mkdir -p src/app/agents
mkdir -p data
mkdir -p tests

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "    source .venv/bin/activate"
echo ""
echo "To run the Schematic Guardian:"
echo "    python -c 'from src.app.agents.codex_deus_maximus import create_codex; agent = create_codex(); print(agent.run_schematic_enforcement())'"
echo ""
echo "To run tests:"
echo "    pytest --cov=src"
echo ""
echo "To use Docker:"
echo "    docker-compose up schematic-guardian"
echo ""
