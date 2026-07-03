"""Tests for importers/copilotstudio/import.py."""

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


cs_import = importlib.import_module("agentdef.importers.copilotstudio.importer")

# Trimmed real-world shape from github/awesome-copilot-studio-agents:
# YAML frontmatter with Copilot-Studio-specific fields, an H1 title wrapping
# Description / Conversation Starters / Instructions (a fenced code block --
# the actual system prompt, itself with its own ## ROLE etc. structure) /
# Knowledge Sources / Deployment Notes / Changelog.
WITH_FRONTMATTER = """---
name: Risk Register Manager
description: Generate, score, categorise, and manage project risks using a 5x5 matrix.
domain: project-management
vertical: n/a
audience: Project Managers / Project Controls
knowledge_sources: None required
language: EN / EN-FR
char_count: ~6000
rai_reviewed: yes
tested: no
version: 1.0
last_updated: 2026-03-24
---

# Risk Register Manager

> **Description:** Build, score, and manage project risk registers using a 5x5 matrix

## Description

Generate, score, categorise, and manage project risks and issues using a standard 5x5 matrix.

## Conversation Starters

- `Generate a risk register for an offshore platform installation project`
- `Add these three new risks to our register and score them`

## Instructions

*(Paste the full block below into the Instructions field in Copilot Studio.)*

```
# Risk Register Manager

## ROLE
You help project teams identify, document, score, categorise, and manage risks using standard risk management practice.

## RISK SCORING MODEL
Probability x Impact. Bands: 1-4 Low | 5-9 Medium | 10-16 High | 17-25 Critical.

## EDGE CASES
User asks to assign a disproportionate score: score as requested but flag it.
```

## Knowledge Sources

None required. If a corporate risk policy is available in SharePoint, connect it as a knowledge source.

## Deployment Notes

- Customise the scoring band thresholds if your organisation uses a different scale.

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-24 | Initial version |
"""

# Real-world shape without any frontmatter (~6% of the real corpus has this).
NO_FRONTMATTER = """# Document Validation Agent

> **Description:** Check any document against a policy or standard

## Description

Validates submitted documents against a defined standard, policy, checklist, or regulatory requirement.

## Conversation Starters

- `Validate this procedure document against our ISO 9001 checklist`

## Instructions

*(Paste the full block below into the Instructions field in Copilot Studio.)*

```
# Document Validation Agent

## ROLE
You validate documents against a defined standard, policy, checklist, or regulatory requirement provided by the user.

## WHAT YOU DO NOT DO
Do not rewrite or suggest replacement text.
```

## Knowledge Sources

None required for ad-hoc validation.

## Deployment Notes

- Works best with a clearly stated standard to check against.
"""


class TestCopilotStudioImport:
    def test_with_frontmatter(self, tmp_path):
        src = tmp_path / "risk-register-manager.md"
        src.write_text(WITH_FRONTMATTER, encoding="utf-8")

        out_dir = tmp_path / "imported"
        result_path = cs_import.import_copilotstudio(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["name"] == "risk-register-manager"
        assert "5x5 matrix" in manifest["description"].lower()
        assert manifest["x-copilotstudio-domain"] == "project-management"
        assert manifest["x-copilotstudio-audience"] == "Project Managers / Project Controls"
        assert "x-copilotstudio-knowledge-sources-detail" in manifest

        # The Role must come from the *fenced Instructions block* (the real
        # system prompt), not the outer wrapper document.
        agent_md = (result_path / "agent.md").read_text()
        assert "identify, document, score, categorise" in agent_md.lower()

        core_md = (result_path / "instructions" / "core.md").read_text()
        assert "risk scoring model" in core_md.lower()
        assert "edge cases" in core_md.lower()

        assert (result_path / "knowledge" / "conversation-starters.md").exists()
        starters = (result_path / "knowledge" / "conversation-starters.md").read_text()
        assert "offshore platform" in starters

        assert (result_path / "instructions" / "deployment-notes.md").exists()
        deployment = (result_path / "instructions" / "deployment-notes.md").read_text()
        assert "scoring band thresholds" in deployment

        report = (result_path / "IMPORT_REPORT.md").read_text()
        assert "changelog" in report.lower()  # dropped, and recorded as such

    def test_without_frontmatter(self, tmp_path):
        """~6% of the real corpus has no YAML frontmatter at all -- name and
        description must fall back to the H1 title and description
        blockquote instead of crashing or producing an empty manifest."""
        src = tmp_path / "document-validation-agent.md"
        src.write_text(NO_FRONTMATTER, encoding="utf-8")

        out_dir = tmp_path / "imported2"
        result_path = cs_import.import_copilotstudio(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["name"] == "document-validation-agent"
        assert "check any document" in manifest["description"].lower()

        agent_md = (result_path / "agent.md").read_text()
        assert "(role not specified in source)" not in agent_md
        assert "validate documents against a defined standard" in agent_md.lower()

    def test_name_override(self, tmp_path):
        src = tmp_path / "risk-register-manager.md"
        src.write_text(WITH_FRONTMATTER, encoding="utf-8")

        out_dir = tmp_path / "imported3"
        result_path = cs_import.import_copilotstudio(str(src), str(out_dir), name="custom-risk-agent")

        import yaml

        manifest = yaml.safe_load((result_path / "manifest.yaml").read_text())
        assert manifest["name"] == "custom-risk-agent"
