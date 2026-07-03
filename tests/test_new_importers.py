"""P3.1/P3.2/P3.3: unit tests for the cursor, openai, and generic importers."""

from pathlib import Path

import pytest
import yaml

from agentdef.importers.cursor.importer import import_cursor
from agentdef.importers.generic.importer import import_generic
from agentdef.importers.openai.importer import import_openai
from agentdef.validation.validate import validate

REPO = Path(__file__).resolve().parent.parent
DOWNLOADS = REPO.parent / "downloads"

MDC = """---
description: Enforce API conventions in the services layer
globs: ["src/services/**/*.ts"]
alwaysApply: false
---

# Service rules

You are a strict reviewer of service-layer code.

## Objectives
- Keep handlers thin
- Validate inputs at the boundary
"""

AGENTS_MD = """# Release Bot

You are a release automation agent for a Python monorepo.

## Objectives
- Cut releases safely
- Keep changelogs honest

## Style
- terse
- imperative
"""

WEIRD = """Just some prose with no headers at all.

- a stray bullet
- another one

```yaml
not: agent content
---
tricky: fences
```
"""


def test_cursor_mdc_frontmatter(tmp_path):
    src = tmp_path / "service.mdc"
    src.write_text(MDC, encoding="utf-8")
    out = import_cursor(str(src), str(tmp_path / "agent"))
    assert validate(str(out)).valid
    manifest = yaml.safe_load((out / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["x-cursor"]["globs"] == ["src/services/**/*.ts"]
    assert manifest["x-cursor"]["alwaysApply"] is False
    assert manifest["description"] == "Enforce API conventions in the services layer"
    report = (out / "IMPORT_REPORT.md").read_text(encoding="utf-8")
    assert "x-cursor.globs" in report


def test_openai_agents_md(tmp_path):
    src = tmp_path / "AGENTS.md"
    src.write_text(AGENTS_MD, encoding="utf-8")
    out = import_openai(str(src), str(tmp_path / "agent"))
    assert validate(str(out)).valid
    agent_md = (out / "agent.md").read_text(encoding="utf-8")
    assert "release automation agent" in agent_md
    assert "Cut releases safely" in agent_md


def test_generic_weird_input_never_dropped(tmp_path):
    src = tmp_path / "prompt.md"
    src.write_text(WEIRD, encoding="utf-8")
    out = import_generic(str(src), str(tmp_path / "agent"))
    assert validate(str(out)).valid
    everything = "".join(
        p.read_text(encoding="utf-8") for p in out.rglob("*.md")
    ) + (out / "manifest.yaml").read_text(encoding="utf-8")
    for needle in ("stray bullet", "tricky: fences", "no headers at all"):
        assert needle in everything, f"content dropped silently: {needle!r}"


def _readme_corpus():
    if not DOWNLOADS.is_dir():
        return []
    return sorted(DOWNLOADS.rglob("README.md"))[:60]


READMES = _readme_corpus()


@pytest.mark.skipif(not READMES, reason="downloads/ corpus not present")
@pytest.mark.parametrize("src", READMES, ids=lambda p: str(p.parent.name))
def test_generic_fuzz_never_crashes_always_valid(src, tmp_path):
    """P3.3 fuzz property: arbitrary non-agent markdown -> no crash, valid
    AgentDef output, report present."""
    out = import_generic(str(src), str(tmp_path / "agent"))
    result = validate(str(out))
    assert result.valid, f"{src}: {result.errors}"
    assert (out / "IMPORT_REPORT.md").exists()
