"""Tests that invalid agent directories fail validation correctly."""

import os
import sys
import tempfile
from pathlib import Path


from agentdef.validation.validate import validate


def _make_agent(tmp: Path, files: dict[str, str]) -> Path:
    """Create a temporary agent directory with the given files."""
    agent_dir = tmp / "test-agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        full = agent_dir / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
    return agent_dir


class TestMissingFiles:
    """Agents missing required files should fail."""

    def test_missing_agent_md(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "manifest.yaml": "name: test\ninstructions:\n  - instructions/core.md\n",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("agent.md" in e for e in result.errors)

    def test_missing_manifest(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("manifest.yaml" in e for e in result.errors)

    def test_missing_core_instructions(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "manifest.yaml": "name: test\ninstructions:\n  - instructions/core.md\n",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("core.md" in e for e in result.errors)


class TestInvalidManifest:
    """Manifests with bad content should fail."""

    def test_invalid_yaml(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "manifest.yaml": "name: test\ninstructions:\n  - [broken",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("not valid YAML" in e for e in result.errors)

    def test_missing_name_field(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "manifest.yaml": "instructions:\n  - instructions/core.md\n",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("schema" in e.lower() or "name" in e.lower() for e in result.errors)

    def test_missing_instructions_field(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "manifest.yaml": "name: test\n",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("schema" in e.lower() or "instructions" in e.lower() for e in result.errors)

    def test_invalid_name_format(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "manifest.yaml": "name: 'My Agent With Spaces!'\ninstructions:\n  - instructions/core.md\n",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("schema" in e.lower() for e in result.errors)


class TestBrokenReferences:
    """Manifests referencing nonexistent files should fail."""

    def test_missing_instruction_file(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "manifest.yaml": "name: test\ninstructions:\n  - instructions/core.md\n  - instructions/safety.md\n",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("safety.md" in e for e in result.errors)

    def test_missing_workflow_file(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "manifest.yaml": "name: test\ninstructions:\n  - instructions/core.md\nworkflows:\n  - workflows/main.md\n",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("main.md" in e for e in result.errors)

    def test_missing_skill_directory(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Role\nTest role.",
            "manifest.yaml": "name: test\ninstructions:\n  - instructions/core.md\nskills:\n  - skills/nonexistent\n",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("nonexistent" in e for e in result.errors)


class TestMissingRole:
    """agent.md without a Role section should fail."""

    def test_no_role_section(self, tmp_path):
        agent_dir = _make_agent(tmp_path, {
            "agent.md": "# Test Agent\n\n## Objectives\n- Do things.",
            "manifest.yaml": "name: test\ninstructions:\n  - instructions/core.md\n",
            "instructions/core.md": "# Core\nDo things.",
        })
        result = validate(str(agent_dir))
        assert not result.valid
        assert any("Role" in e for e in result.errors)


class TestNotADirectory:
    """Passing a file instead of a directory should fail."""

    def test_file_instead_of_dir(self, tmp_path):
        f = tmp_path / "not-a-dir.txt"
        f.write_text("hello")
        result = validate(str(f))
        assert not result.valid
        assert any("Not a directory" in e for e in result.errors)
