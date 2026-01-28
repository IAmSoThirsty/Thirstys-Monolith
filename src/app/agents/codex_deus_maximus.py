"""Codex Deus Maximus - Schematic Guardian.
Repurposed to solely focus on repository integrity, structure validation, and auto-correction.
"""
from __future__ import annotations

import ast
import json
import logging
import os
import shutil
import types
from datetime import datetime, timezone
from typing import Any, List, Dict

# --- CONFIGURATION ---
logger = logging.getLogger("SchematicGuardian")
logging.basicConfig(level=logging.INFO)

# Define the "Schematic" (Required Structure)
REQUIRED_DIRS = [
    ".github/workflows",
    "src",
]

class CodexDeusMaximus:
    """Schematic Guardian AI that enforces repository structure and code standards."""

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self.audit_path = os.path.join(self.data_dir, "schematic_audit.json")
        # Ensure legacy method binding for compatibility
        try:
            self.auto_fix_file = types.MethodType(self.__class__.auto_fix_file, self)
        except Exception:
            pass

    def initialize(self) -> bool:
        logger.info("Schematic Guardian initialized. Mode: STRICT ENFORCEMENT.")
        return True

    def _audit(self, action: str, details: Dict[str, Any]) -> None:
        """Log actions to the audit trail."""
        try:
            os.makedirs(os.path.dirname(self.audit_path), exist_ok=True)
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "action": action,
                "details": details
            }
            with open(self.audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            logger.error("Failed to write audit entry.")

    def run_schematic_enforcement(self, root: str | None = None) -> Dict[str, Any]:
        """The Main Routine: Validates structure and fixes files."""
        root = root or os.getcwd()
        report = {
            "structure_check": self._validate_structure(root),
            "fixes": [],
            "errors": []
        }

        logger.info(f"Enforcing schematics on {root}...")

        # Walk the repo to fix code files
        for dirpath, _, filenames in os.walk(root):
            # Ignore hidden/system folders
            if any(part.startswith(".") or part in ("venv", "env", "__pycache__", "build", "dist") for part in dirpath.split(os.sep)):
                continue

            for fn in filenames:
                path = os.path.join(dirpath, fn)

                # Enforce formatting on specific types
                if fn.endswith(('.py', '.md', '.json', '.yml', '.yaml')):
                    res = self.auto_fix_file(path)
                    if res.get("success") and res.get("action") == "fixed":
                        report["fixes"].append({"path": path, "backup": res.get("backup")})
                    elif not res.get("success"):
                        report["errors"].append({"path": path, "error": res.get("error")})

        self._audit("enforcement_run", report)
        return report

    def _validate_structure(self, root: str) -> Dict[str, Any]:
        """Ensure the repository adheres to the required folder schematic."""
        missing = []
        for d in REQUIRED_DIRS:
            if not os.path.exists(os.path.join(root, d)):
                missing.append(d)

        status = "HEALTHY" if not missing else "BROKEN"
        if missing:
            logger.warning(f"Schematic Violation: Missing directories {missing}")

        return {"status": status, "missing_directories": missing}

    def auto_fix_file(self, path: str) -> Dict[str, Any]:
        """Strictly enforces formatting standards (Tabs->Spaces, EOF Newline, Syntax Check)."""
        if not os.path.exists(path):
            return {"success": False, "error": "missing"}

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            orig = content
            fixed = content

            # --- RULE 1: Python Specifics ---
            if path.endswith(".py"):
                fixed = fixed.replace("\t", "    ") # No tabs
                fixed = "\n".join(line.rstrip() for line in fixed.splitlines()) # No trailing whitespace

                # Safety: Check syntax before accepting
                try:
                    ast.parse(fixed)
                except SyntaxError as e:
                    return {"success": False, "error": f"syntax_error: {str(e)}"}

            # --- RULE 2: General Text Files (.md, .yml, .json) ---
            elif path.endswith((".md", ".yml", ".yaml", ".json")):
                fixed = fixed.replace("\r\n", "\n").replace("\r", "\n") # UNIX endings

            # --- RULE 3: End of File Newline ---
            if fixed and not fixed.endswith("\n"):
                fixed += "\n"

            # Apply Changes
            if fixed != orig:
                bak = path + ".bak"
                shutil.copyfile(path, bak)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(fixed)
                return {"success": True, "action": "fixed", "backup": bak}

            return {"success": True, "action": "noop"}

        except Exception as e:
            return {"success": False, "error": str(e)}

# Factory
def create_codex(data_dir: str = "data") -> CodexDeusMaximus:
    c = CodexDeusMaximus(data_dir=data_dir)
    c.initialize()
    return c
