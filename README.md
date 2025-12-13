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

## 🛠️ Enforcement Rules
The **Schematic Guardian** automatically applies the following rules on every push:
1.  **Python:** Converts tabs to 4 spaces; strips trailing whitespace; ensures valid syntax.
2.  **Docs/Config:** Ensures UNIX line endings (`\n`) for `.md`, `.json`, and `.yml` files.
3.  **General:** Ensures every file ends with a single newline character.

---

## 📄 License
MIT License © 2025 Thirstys-Hub
