"""Tests for importers/m365copilot/import.py."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
from agentdef.validation.validate import validate  # noqa: E402


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m365_import = importlib.import_module("agentdef.importers.m365copilot.importer")

MINIMAL_MANIFEST = {
    "version": "v1.7",
    "name": "Repairs agent",
    "description": "This declarative agent is meant to help track any tickets and repairs",
    "instructions": "This declarative agent needs to look at my Service Now and Jira tickets/instances to help me keep track of open items",
}

FULL_MANIFEST = {
    "version": "v1.7",
    "name": "Teams Toolkit declarative agent",
    "description": "Declarative agent created with Teams Toolkit",
    "instructions": (
        "You are a repairs expert agent. With the response from the listRepairs function, "
        "you must create a poem out of the repairs listed."
    ),
    "conversation_starters": [
        {"title": "Getting Started", "text": "How can I get started with Teams Toolkit?"},
    ],
    "actions": [{"id": "repairsPlugin", "file": "repairs-hub-api-plugin.json"}],
    "behavior_overrides": {
        "suggestions": {"disabled": True},
        "special_instructions": {"discourage_model_knowledge": True},
        "default_response_mode": "Auto",
    },
    "disclaimer": {"text": "This declarative agent is a fictional example."},
    "capabilities": [
        {"name": "WebSearch", "sites": [{"url": "https://contoso.com/projects/mark-8"}]},
        {"name": "CodeInterpreter"},
    ],
    "sensitivity_label": {"id": "00000000-0000-0000-0000-000000000000"},
}


class TestM365CopilotImport:
    def test_minimal_manifest(self, tmp_path):
        src = tmp_path / "declarativeAgent.json"
        src.write_text(json.dumps(MINIMAL_MANIFEST), encoding="utf-8")

        out_dir = tmp_path / "imported"
        result_path = m365_import.import_m365copilot(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()

        manifest_text = (result_path / "manifest.yaml").read_text()
        assert "repairs-agent" in manifest_text

        core_md = (result_path / "instructions" / "core.md").read_text()
        assert "Service Now and Jira" in core_md

    def test_full_manifest(self, tmp_path):
        src = tmp_path / "declarativeAgent.json"
        src.write_text(json.dumps(FULL_MANIFEST), encoding="utf-8")

        out_dir = tmp_path / "imported2"
        result_path = m365_import.import_m365copilot(str(src), str(out_dir))

        result = validate(str(result_path))
        assert result.valid, result.summary()

        agent_md = (result_path / "agent.md").read_text()
        assert "you are a repairs expert agent" in agent_md.lower()

        assert (result_path / "tools" / "websearch.md").exists()
        assert (result_path / "tools" / "codeinterpreter.md").exists()
        assert (result_path / "tools" / "action-repairsplugin.md").exists()
        assert (result_path / "knowledge" / "conversation-starters.md").exists()

        safety = (result_path / "instructions" / "safety.md").read_text()
        assert "disclaimer" in safety.lower()
        assert "model knowledge" in safety.lower() or "discourage" in safety.lower()

        runtime_config = (result_path / "runtime" / "config.yaml").read_text()
        assert "x-m365-sensitivity_label" in runtime_config

        report = (result_path / "IMPORT_REPORT.md").read_text()
        assert "sensitivity_label" in report
