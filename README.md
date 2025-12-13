# 🏛️ Thirty's Monolith

![Build Status](https://img.shields.io/badge/Build-Passing-success?style=for-the-badge&logo=github)
![Security](https://img.shields.io/badge/Security-Hardened-blue?style=for-the-badge&logo=github-actions)
![AI Agent](https://img.shields.io/badge/AI-Codex%20Deus%20Maximus-purple?style=for-the-badge)

**One Workflow to Rule Them All.**

Thirty's Monolith is a unified, self-contained CI/CD pipeline that replaces 15+ disparate workflow files. It orchestrates AI agents, security audits, polyglot testing, and cloud deployment in a single, synchronized stream.

---

## ⚡ System Architecture

The Monolith operates in **6 Synchronized Battalions**:

| Battalion | Function | Tools Used |
| :--- | :--- | :--- |
| **1. Codex Deus Maximus** | *AI Auto-Correction* | Custom Python Agent (`codex_deus_maximus.py`) wakes up to fix code logic and style before tests run. |
| **2. Security Gate** | *Vulnerability Scanning* | **CodeQL** (Logic), **Super-Linter** (Style), **Pip Audit** (Python Deps), **NPM Audit** (Node Deps). |
| **3. Polyglot Build** | *Build & Test* | Matrix strategy handling **Python** (Pytest/Cerberus), **Node.js** (Webpack), **Android** (Gradle), and **Docker**. |
| **4. Triage Agents** | *Community Management* | AI Issue Summarizer, Auto-Labeler, First-Interaction Greeter. |
| **5. Deployment** | *Release Management* | **Datadog Synthetics** (Pre-flight), **Google Cloud Run** (Production). |
| **6. Maintenance** | *Janitorial* | Nightly stale issue closure and dependency checks. |

---

## 🚀 Installation & Setup

### 1. The Monolith File
Ensure the master script is placed at:
`.github/workflows/thirtys-monolith.yml`

### 2. The AI Agent
The workflow relies on your custom agent to self-heal the repository. Ensure the source code is present at:
`src/app/agents/codex_deus_maximus.py`

### 3. Required Secrets
Go to **Settings > Secrets and variables > Actions** and add:

* `DD_API_KEY` (Datadog API)
* `DD_APP_KEY` (Datadog App Key)
* `GCP_WORKLOAD_IDENTITY_PROVIDER` (Google Cloud Auth)
* `CODACY_PROJECT_TOKEN` (Optional: If using Codacy)

### 4. Configuration
Open `thirtys-monolith.yml` and update the environment variables section with your project details:

```yaml
env:
  PROJECT_ID: 'your-gcp-project-id'
  REGION: 'us-central1'
  SERVICE: 'project-ai-service'
