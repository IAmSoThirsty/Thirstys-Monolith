# 🏛️ Thirty's Monolith: Schematic Guardian

![Build Status](https://img.shields.io/badge/Schematic-Enforced-success?style=for-the-badge&logo=github)
![Security](https://img.shields.io/badge/Integrity-Verified-blue?style=for-the-badge&logo=github-actions)
![Agent](https://img.shields.io/badge/Agent-Codex%20Deus%20Maximus-purple?style=for-the-badge)

**The Strict Enforcer for Repository Integrity.**

Thirty's Monolith is a specialized, self-correcting CI/CD pipeline designed to maintain absolute schematic control over your codebase. It uses a custom AI agent to strictly enforce folder structure, file formatting, and syntax standards before allowing any build to proceed.

---

## ⚡ System Architecture

The pipeline operates in **3 Strict Stages**:

| Stage | Job Name | Function |
| :--- | :--- | :--- |
| **1. Enforcement** | `🤖 Schematic Guardian` | The **Codex Deus Maximus** agent wakes up, scans the entire repository, and auto-corrects formatting (tabs, newlines) while validating Python syntax. If the required folder structure is broken, the build fails immediately. |
| **2. Integrity** | `🛡️ Verify Integrity` | Runs **CodeQL** (Logic Analysis) and **Pip Audit** (Dependency Security) to ensure the code is safe and robust. |
| **3. Validation** | `🏗️ Validate Functions` | A polyglot matrix that builds and tests the actual code artifacts (**Python/Pytest**, **Node/Webpack**, **Android/Gradle**). |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Git
- Docker (optional, for containerized deployment)

### Quick Start

#### Option 1: Using the Setup Script (Recommended)
```bash
git clone https://github.com/IAmSoThirsty/Thirstys-Monolith.git
cd Thirstys-Monolith
./setup.sh
source .venv/bin/activate
```

#### Option 2: Using Make
```bash
git clone https://github.com/IAmSoThirsty/Thirstys-Monolith.git
cd Thirstys-Monolith
make setup
source .venv/bin/activate
```

#### Option 3: Manual Setup
See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Verify Installation
```bash
# Run tests
pytest --cov=src -v

# Run Schematic Guardian
python -c "from src.app.agents.codex_deus_maximus import create_codex; agent = create_codex(); print(agent.run_schematic_enforcement())"
```

### 1. The Monolith Workflow
Ensure the master enforcement script is placed at:
`.github/workflows/thirtys-monolith.yml`

### 2. The Guardian Agent
The workflow relies on your custom agent to perform the audit. Ensure the source code is present at:
`src/app/agents/codex_deus_maximus.py`

### 3. Required Directory Schematic
The Guardian enforces the existence of these core directories. Your build **will fail** if they are missing:
* `.github/workflows/`
* `src/`

---

## 🛠️ Development

### Available Commands
The project includes a `Makefile` with common development commands:

```bash
make help          # Show all available commands
make setup         # Create virtual environment and install dependencies
make test          # Run tests with coverage
make lint          # Run linters (flake8, pylint)
make format        # Format code with black
make clean         # Remove build artifacts and cache files
make docker-build  # Build Docker image
make docker-run    # Run Schematic Guardian in Docker
```

### Running Tests
```bash
# All tests with coverage
pytest --cov=src -v

# Or using Make
make test
```

### Docker Support
Build and run with Docker:
```bash
# Build image
docker compose build

# Run Schematic Guardian
docker compose up schematic-guardian

# Run tests
docker compose up test
```

---

## 📦 Project Structure

```
Thirstys-Monolith/
├── .github/workflows/     # CI/CD workflows
├── src/app/agents/        # Schematic Guardian agent
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── setup.py               # Package configuration
├── Dockerfile            # Docker configuration
├── Makefile              # Development commands
└── INSTALL.md            # Detailed installation guide
```

---

## 🛠️ Enforcement Rules
The **Schematic Guardian** automatically applies the following rules on every push:
1.  **Python:** Converts tabs to 4 spaces; strips trailing whitespace; ensures valid syntax.
2.  **Docs/Config:** Ensures UNIX line endings (`\n`) for `.md`, `.json`, and `.yml` files.
3.  **General:** Ensures every file ends with a single newline character.

---

## 📄 License
MIT License © 2025 Thirstys-Hub
