"""Tests for importers/claude/import.py, including a round-trip check
against the forward adapter (adapters/claude/generate.py).

The round-trip test shells out to both CLI scripts as subprocesses rather
than importing them directly: adapters/_common.py and importers/_common.py
are both plain modules named ``_common`` loaded via sys.path tricks, so
importing both forward and reverse scripts in the *same* Python process
would collide in sys.modules. Subprocesses sidestep that entirely and also
exercise the actual documented CLI usage.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
from agentdef.validation.validate import validate  # noqa: E402


def _load(path: Path, name: str):
    """Load a single script module by file path (works around 'import.py'
    not being a valid module name)."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestRoundTrip:
    def test_mission_writer_round_trip(self, tmp_path):
        claude_md = tmp_path / "CLAUDE.md"
        env = {**os.environ, "PYTHONPATH": str(ROOT / "pysrc")}
        subprocess.run(
            [
                sys.executable,
                "-m",
                "agentdef.adapters.claude.generate",
                str(ROOT / "examples" / "mission-writer"),
                "--output",
                str(claude_md),
            ],
            check=True,
            cwd=str(ROOT),
            env=env,
        )
        assert claude_md.exists()

        out_dir = tmp_path / "imported"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "agentdef.importers.claude.importer",
                str(claude_md),
                "--output",
                str(out_dir),
            ],
            check=True,
            cwd=str(ROOT),
            env=env,
        )

        result = validate(str(out_dir))
        assert result.valid, result.summary()

        agent_md = (out_dir / "agent.md").read_text()
        assert "structured documentation agent" in agent_md.lower()

        report = (out_dir / "IMPORT_REPORT.md").read_text()
        assert "round-trip detected" in report

        # Skill/workflow directory names come from the H1 title inside each
        # SKILL.md/workflow file (re-slugified), not from the original
        # examples/mission-writer/{skills,workflows}/<dir-name> on disk —
        # the real files are titled "Mission Authoring Skill" and "Mission
        # Writing Workflow" respectively.
        assert (out_dir / "skills" / "mission-authoring-skill" / "SKILL.md").exists()
        assert (out_dir / "workflows" / "mission-writing-workflow.md").exists()


class TestGenericClaudeMd:
    """These only touch importers/_common.py, so they're safe to load directly."""

    @classmethod
    def setup_class(cls):
        cls.claude_import = importlib.import_module("agentdef.importers.claude.importer")

    def test_freeform_claude_md(self, tmp_path):
        text = (
            "# Release Notes Bot\n\n"
            "You are an assistant that writes release notes from commit logs.\n\n"
            "## Objectives\n- summarize commits\n- group by type\n\n"
            "## Tools\n\n### GitHub API\nFetches commit history.\n"
        )
        src = tmp_path / "CLAUDE.md"
        src.write_text(text, encoding="utf-8")

        out_dir = tmp_path / "imported2"
        result_path = self.claude_import.import_claude_md(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()
        assert (result_path / "tools" / "github-api.md").exists()

    def test_name_override(self, tmp_path):
        src = tmp_path / "CLAUDE.md"
        src.write_text("# Whatever\n\nYou are a bot.\n", encoding="utf-8")
        out_dir = tmp_path / "imported3"
        result_path = self.claude_import.import_claude_md(str(src), str(out_dir), name="custom-name")

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["name"] == "custom-name"


class TestClaudeCodeSubagent:
    """Third source shape: a .claude/agents/<name>.md-style file with YAML
    frontmatter (name/description/tools), as published in community
    collections like github/awesome-claude-agents and
    github/awesome-claude-code-subagents. Added after batch-testing 187
    real files from those two repos."""

    @classmethod
    def setup_class(cls):
        cls.claude_import = importlib.import_module("agentdef.importers.claude.importer")

    def test_frontmatter_is_parsed_not_left_as_noise(self, tmp_path):
        text = (
            "---\n"
            "name: rails-api-developer\n"
            "description: Expert Rails API developer specializing in RESTful APIs "
            "and GraphQL. MUST BE USED for Rails API development.\n"
            "---\n\n"
            "# Rails API Developer\n\n"
            "You are an expert Rails API developer.\n\n"
            "## Objectives\n- build RESTful endpoints\n- write serializers\n"
        )
        src = tmp_path / "rails-api-developer.md"
        src.write_text(text, encoding="utf-8")

        out_dir = tmp_path / "imported"
        result_path = self.claude_import.import_claude_md(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["name"] == "rails-api-developer"
        assert "Rails API developer" in manifest["description"]

        report = (result_path / "IMPORT_REPORT.md").read_text()
        assert "YAML frontmatter" in report

        core = (result_path / "instructions" / "core.md").read_text()
        assert "name: rails-api-developer" not in core

    def test_tools_field_preserved_as_manifest_extra(self, tmp_path):
        text = (
            "---\n"
            "name: web-scraper\n"
            "description: Scrapes websites.\n"
            "tools: Read, Grep, Bash, WebFetch\n"
            "---\n\n"
            "You are a web scraping expert.\n"
        )
        src = tmp_path / "web-scraper.md"
        src.write_text(text, encoding="utf-8")

        out_dir = tmp_path / "imported"
        result_path = self.claude_import.import_claude_md(str(src), str(out_dir))

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["x-claude-tools"] == "Read, Grep, Bash, WebFetch"

    def test_unquoted_colon_in_description_does_not_corrupt_output(self, tmp_path):
        # Regression test mirroring the real gdpr-ccpa-compliance.md bug:
        # a description containing its own unescaped ": " used to make
        # yaml.safe_load throw and the whole frontmatter block would leak
        # into core.md as duplicated raw text.
        text = (
            "---\n"
            "name: gdpr-ccpa-compliance\n"
            "description: Use when the user needs to understand GDPR or CCPA "
            "compliance. Triggers on: 'GDPR', 'CCPA', privacy law questions.\n"
            "---\n\n"
            "You are a privacy compliance expert.\n"
        )
        src = tmp_path / "gdpr-ccpa-compliance.md"
        src.write_text(text, encoding="utf-8")

        out_dir = tmp_path / "imported"
        result_path = self.claude_import.import_claude_md(str(src), str(out_dir))

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["name"] == "gdpr-ccpa-compliance"
        assert "Triggers on" in manifest["description"]

        core = (result_path / "instructions" / "core.md").read_text()
        assert core.count("You are a privacy compliance expert") == 1
        assert "name: gdpr-ccpa-compliance" not in core

    def test_extended_dash_closing_fence(self, tmp_path):
        # Regression test mirroring the real frontend-developer.md bug: a
        # closing frontmatter fence made of a long run of dashes instead of
        # exactly "---" used to leave the whole block unparsed.
        text = (
            "---\n"
            "name: frontend-developer\n"
            "description: Builds UIs.\n"
            "--------------------------------------------------------\n\n"
            "# Frontend Developer\n\n"
            "You build user interfaces.\n"
        )
        src = tmp_path / "frontend-developer.md"
        src.write_text(text, encoding="utf-8")

        out_dir = tmp_path / "imported"
        result_path = self.claude_import.import_claude_md(str(src), str(out_dir))

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["name"] == "frontend-developer"

        core = (result_path / "instructions" / "core.md").read_text()
        assert "name: frontend-developer" not in core
