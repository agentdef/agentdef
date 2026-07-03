"""Tests for importers/copilot/import.py."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
from agentdef.validation.validate import validate  # noqa: E402


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


copilot_import = importlib.import_module("agentdef.importers.copilot.importer")

MAIN_INSTRUCTIONS = """# Repo Helper

You are a coding assistant for this repository.

## Objectives
- keep PRs small
- write tests for new code

## Avoid
- introducing new dependencies without discussion
"""

SCOPED_INSTRUCTIONS = """---
applyTo: "**/*.py"
---

Use type hints on all new functions. Prefer f-strings over .format().
"""

# Real-world shape: a github/awesome-copilot custom agent (*.agent.md), with
# a YAML frontmatter block (name/description/tools) ahead of a single H1
# title that wraps everything else. Trimmed down from
# https://github.com/github/awesome-copilot/blob/main/agents/devops-expert.agent.md
CUSTOM_AGENT_MD = """---
name: 'DevOps Expert'
description: 'DevOps specialist following the infinity loop principle'
tools: ['codebase', 'edit/editFiles', 'terminalCommand']
---

# DevOps Expert

You are a DevOps expert who follows the DevOps Infinity Loop principle.

## Your Mission

Guide teams through the complete DevOps lifecycle.

## Phase 1: Plan

Define work, prioritize, and prepare for implementation.
"""


class TestCopilotImport:
    def test_main_file_only(self, tmp_path):
        gh_dir = tmp_path / ".github"
        gh_dir.mkdir()
        src = gh_dir / "copilot-instructions.md"
        src.write_text(MAIN_INSTRUCTIONS, encoding="utf-8")

        out_dir = tmp_path / "imported"
        result_path = copilot_import.import_copilot(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()
        agent_md = (result_path / "agent.md").read_text()
        assert "coding assistant" in agent_md.lower()

    def test_with_scoped_instructions_autodetected(self, tmp_path):
        gh_dir = tmp_path / ".github"
        gh_dir.mkdir()
        src = gh_dir / "copilot-instructions.md"
        src.write_text(MAIN_INSTRUCTIONS, encoding="utf-8")

        instructions_dir = gh_dir / "instructions"
        instructions_dir.mkdir()
        (instructions_dir / "python.instructions.md").write_text(SCOPED_INSTRUCTIONS, encoding="utf-8")

        out_dir = tmp_path / "imported2"
        result_path = copilot_import.import_copilot(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()

        python_instr = (result_path / "instructions" / "python.md").read_text()
        assert "type hints" in python_instr
        assert "**/*.py" in python_instr  # applyTo scope preserved as a comment

    def test_explicit_instructions_dir(self, tmp_path):
        src = tmp_path / "copilot-instructions.md"
        src.write_text(MAIN_INSTRUCTIONS, encoding="utf-8")

        instructions_dir = tmp_path / "scoped"
        instructions_dir.mkdir()
        (instructions_dir / "python.instructions.md").write_text(SCOPED_INSTRUCTIONS, encoding="utf-8")

        out_dir = tmp_path / "imported3"
        result_path = copilot_import.import_copilot(
            str(src), str(out_dir), instructions_dir=str(instructions_dir)
        )

        assert (result_path / "instructions" / "python.md").exists()
        result = validate(str(result_path))
        assert result.valid, result.summary()

    def test_custom_agent_with_yaml_frontmatter(self, tmp_path):
        """github/awesome-copilot-style *.agent.md: name/description/tools
        frontmatter must be parsed properly, not silently dropped or dumped
        as raw text into core.md."""
        src = tmp_path / "devops-expert.agent.md"
        src.write_text(CUSTOM_AGENT_MD, encoding="utf-8")

        out_dir = tmp_path / "imported4"
        result_path = copilot_import.import_copilot(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["name"] == "devops-expert"
        assert "infinity loop" in manifest["description"].lower()
        assert manifest["x-copilot-tools"] == ["codebase", "edit/editFiles", "terminalCommand"]

        agent_md = (result_path / "agent.md").read_text()
        assert "devops expert" in agent_md.lower()

        report = (result_path / "IMPORT_REPORT.md").read_text()
        assert "frontmatter" in report.lower()
        assert "x-copilot-tools" in report
