"""Round-trip smoke tests (P1.4): adapt claude -> import claude -> validate.

Asserts (a) the re-imported agent validates, and (b) the importer detects
the AgentDef-generated marker and reports the round-trip in
IMPORT_REPORT.md.
"""

from pathlib import Path

import pytest

from agentdef.adapters.claude.generate import AgentDef, generate
from agentdef.importers.claude.importer import import_claude_md
from agentdef.validation.validate import validate

REPO = Path(__file__).resolve().parent.parent
EXAMPLES = ["mission-writer", "twitter-digest"]


@pytest.mark.parametrize("example", EXAMPLES)
def test_claude_roundtrip(example, tmp_path):
    agent = AgentDef(str(REPO / "examples" / example))
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(generate(agent), encoding="utf-8")

    out = import_claude_md(str(claude_md), str(tmp_path / "imported"))

    result = validate(str(out))
    assert result.valid, f"re-imported {example} failed validation: {result.summary()}"

    report = (out / "IMPORT_REPORT.md").read_text(encoding="utf-8")
    assert "round-trip detected" in report, "AgentDef-generated marker not detected"


@pytest.mark.parametrize("example", EXAMPLES)
def test_roundtrip_marker_required(example, tmp_path):
    """Without the marker line the import must NOT report a round-trip."""
    agent = AgentDef(str(REPO / "examples" / example))
    content = generate(agent)
    stripped = "\n".join(
        line for line in content.splitlines() if "Generated from AgentDef" not in line
    )
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(stripped, encoding="utf-8")

    out = import_claude_md(str(claude_md), str(tmp_path / "imported"))
    report = (out / "IMPORT_REPORT.md").read_text(encoding="utf-8")
    assert "round-trip detected" not in report
