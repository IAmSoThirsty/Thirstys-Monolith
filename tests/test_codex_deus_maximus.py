"""Tests for Codex Deus Maximus - Schematic Guardian."""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app.agents.codex_deus_maximus import CodexDeusMaximus, create_codex


class TestCodexDeusMaximus:
    """Test suite for Schematic Guardian."""

    def test_initialization(self):
        """Test that the agent initializes correctly."""
        agent = create_codex()
        assert agent is not None
        assert isinstance(agent, CodexDeusMaximus)

    def test_structure_validation_pass(self):
        """Test structure validation with required directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create required directories
            os.makedirs(os.path.join(tmpdir, ".github", "workflows"))
            os.makedirs(os.path.join(tmpdir, "src"))
            
            agent = create_codex()
            result = agent._validate_structure(tmpdir)
            
            assert result["status"] == "HEALTHY"
            assert len(result["missing_directories"]) == 0

    def test_structure_validation_fail(self):
        """Test structure validation with missing directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = create_codex()
            result = agent._validate_structure(tmpdir)
            
            assert result["status"] == "BROKEN"
            assert len(result["missing_directories"]) > 0

    def test_auto_fix_python_file(self):
        """Test Python file auto-fixing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.py")
            
            # Write file with tabs and trailing whitespace
            with open(test_file, "w") as f:
                f.write("def test():\n\tpass  \n")
            
            agent = create_codex()
            result = agent.auto_fix_file(test_file)
            
            assert result["success"] is True
            assert result["action"] == "fixed"
            
            # Verify content was fixed
            with open(test_file, "r") as f:
                content = f.read()
            
            assert "\t" not in content
            assert "    pass" in content

    def test_auto_fix_markdown_file(self):
        """Test markdown file auto-fixing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.md")
            
            # Write file with Windows line endings
            with open(test_file, "wb") as f:
                f.write(b"# Title\r\nContent\r\n")
            
            agent = create_codex()
            result = agent.auto_fix_file(test_file)
            
            assert result["success"] is True
            
            # Verify content was fixed
            with open(test_file, "rb") as f:
                content = f.read()
            
            assert b"\r\n" not in content

    def test_run_schematic_enforcement(self):
        """Test full schematic enforcement run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create required structure
            os.makedirs(os.path.join(tmpdir, ".github", "workflows"))
            os.makedirs(os.path.join(tmpdir, "src"))
            
            # Create a test Python file
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, "w") as f:
                f.write("print('hello')")
            
            agent = create_codex()
            report = agent.run_schematic_enforcement(tmpdir)
            
            assert "structure_check" in report
            assert "fixes" in report
            assert "errors" in report
            assert report["structure_check"]["status"] == "HEALTHY"
