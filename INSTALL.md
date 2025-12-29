# Installation Guide - Thirsty's Monolith

This guide will help you set up the Thirsty's Monolith development environment.

## Prerequisites

- Python 3.11 or higher
- Git
- Docker (optional, for containerized deployment)
- Make (optional, for using Makefile commands)

## Quick Setup

### Option 1: Using the Setup Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/IAmSoThirsty/Thirstys-Monolith.git
cd Thirstys-Monolith

# Run the setup script
./setup.sh

# For development setup with additional tools
./setup.sh --dev
```

### Option 2: Using Make

```bash
# Clone the repository
git clone https://github.com/IAmSoThirsty/Thirstys-Monolith.git
cd Thirstys-Monolith

# Setup environment and install dependencies
make setup

# Install package in development mode
make install
```

### Option 3: Manual Setup

```bash
# Clone the repository
git clone https://github.com/IAmSoThirsty/Thirstys-Monolith.git
cd Thirstys-Monolith

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

## Directory Structure

After setup, your directory structure should look like:

```
Thirstys-Monolith/
├── .github/
│   └── workflows/
│       ├── thirtys-monolith.yml
│       └── constructor.yml
├── src/
│   └── app/
│       └── agents/
│           └── codex_deus_maximus.py
├── tests/
│   ├── __init__.py
│   └── test_codex_deus_maximus.py
├── data/              # Created at runtime for audit logs
├── .venv/             # Virtual environment
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Docker Setup

### Building the Docker Image

```bash
# Using docker-compose
docker-compose build

# Or using Make
make docker-build
```

### Running with Docker

```bash
# Run Schematic Guardian
docker-compose up schematic-guardian

# Or using Make
make docker-run

# Run tests in Docker
docker-compose up test

# Or using Make
make docker-test
```

## Verification

### Verify Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
pytest --cov=src -v

# Or using Make
make test
```

### Run Schematic Guardian

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the guardian
python -c "from src.app.agents.codex_deus_maximus import create_codex; agent = create_codex(); print(agent.run_schematic_enforcement())"
```

## Development Workflow

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html -v

# Or using Make
make test
```

### Linting

```bash
# Run linters
flake8 src/ tests/
pylint src/

# Or using Make
make lint
```

### Formatting

```bash
# Format code
black src/ tests/

# Or using Make
make format
```

### Cleaning Up

```bash
# Remove build artifacts and cache files
make clean
```

## Troubleshooting

### Python Version Issues

Ensure you have Python 3.11 or higher:

```bash
python3 --version
```

### Virtual Environment Issues

If you have issues with the virtual environment:

```bash
# Remove existing venv
rm -rf .venv

# Recreate it
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Permission Issues on Linux/Mac

If setup.sh won't run:

```bash
chmod +x setup.sh
./setup.sh
```

### Docker Issues

If Docker commands fail:

```bash
# Ensure Docker is running
docker ps

# Rebuild without cache
docker-compose build --no-cache
```

## Next Steps

After installation:

1. Read the [README.md](README.md) for project overview
2. Check the [workflow files](.github/workflows/) to understand CI/CD setup
3. Review the [Codex Deus Maximus agent](src/app/agents/codex_deus_maximus.py)
4. Run tests to ensure everything works
5. Start developing!

## Support

For issues or questions:
- Check existing GitHub Issues
- Create a new issue with detailed information
- Include error messages and system information
