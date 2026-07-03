"""P3.4 + P3.7: CrewAI pair and Letta bridge tests."""

import json
from pathlib import Path

import yaml

from agentdef.adapters.crewai.generate import AgentDef, generate as gen_crewai
from agentdef.importers.crewai.importer import import_crewai
from agentdef.importers.letta.importer import import_letta
from agentdef.validation.validate import validate

REPO = Path(__file__).resolve().parent.parent

LETTA_AF = {
    "name": "support-agent",
    "description": "Handles support tickets",
    "system": "You are a support agent for Acme. Always be factual.",
    "memory_blocks": [
        {"label": "persona", "value": "You are a patient, precise support specialist."},
        {"label": "human", "value": "The user is an Acme customer."},
    ],
    "tools": [{"name": "search_kb"}, {"name": "escalate"}],
    "messages": [{"role": "user", "content": "hi"}],
    "llm_config": {"model": "gpt-4"},
}


def test_crewai_adapter_yaml_loads_and_maps(tmp_path):
    out = gen_crewai(AgentDef(str(REPO / "examples" / "mission-writer")))
    doc = yaml.safe_load(out)
    (slug, spec), = doc["agents"].items()
    assert spec["role"] and spec["goal"] and spec["backstory"]
    assert doc["tasks"], "workflows should map to tasks"
    for tspec in doc["tasks"].values():
        assert tspec["agent"] == slug


def test_crewai_roundtrip_pair(tmp_path):
    crew = tmp_path / "crew.yaml"
    crew.write_text(gen_crewai(AgentDef(str(REPO / "examples" / "mission-writer"))), encoding="utf-8")
    out = import_crewai(str(crew), str(tmp_path / "agent"))
    result = validate(str(out))
    assert result.valid, result.errors
    agent_md = (out / "agent.md").read_text(encoding="utf-8")
    assert "## Role" in agent_md


def test_crewai_bare_agents_yaml_multi(tmp_path):
    src = tmp_path / "agents.yaml"
    src.write_text(yaml.safe_dump({
        "researcher": {"role": "Senior researcher", "goal": "Find facts", "backstory": "Years in the field."},
        "writer": {"role": "Writer", "goal": "Write reports", "backstory": "Loves clarity."},
    }), encoding="utf-8")
    import_crewai(str(src), str(tmp_path / "out"))
    for slug in ("researcher", "writer"):
        assert validate(str(tmp_path / "out" / slug)).valid


def test_letta_behavior_subset_and_dropped_state(tmp_path):
    src = tmp_path / "agent.af"
    src.write_text(json.dumps(LETTA_AF), encoding="utf-8")
    out = import_letta(str(src), str(tmp_path / "agent"))
    assert validate(str(out)).valid
    core = (out / "instructions" / "core.md").read_text(encoding="utf-8")
    assert "You are a support agent for Acme" in core
    assert "patient, precise support specialist" in core
    report = (out / "IMPORT_REPORT.md").read_text(encoding="utf-8")
    for field in ("messages", "llm_config"):
        assert field in report, f"dropped state field {field} not reported"
    tools = (out / "tools" / "letta-tools.md").read_text(encoding="utf-8")
    assert "search_kb" in tools and "escalate" in tools
