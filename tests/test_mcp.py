"""P3.8: tools/mcp.yaml mapping tests."""

import json
import shutil
from pathlib import Path

import jsonschema
import yaml

from agentdef.adapters.claude.generate import AgentDef, generate
from agentdef.importers.claude.importer import import_claude_md
from agentdef.validation.validate import validate

REPO = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((REPO / "pysrc/agentdef/schemas/mcp.schema.json").read_text(encoding="utf-8"))

MCP_YAML = """servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env: ["GITHUB_TOKEN"]
    description: GitHub issues and PRs
  internal-kb:
    url: https://mcp.example.com/sse
"""


def _agent_with_mcp(tmp_path):
    dst = tmp_path / "agent"
    shutil.copytree(REPO / "examples" / "mission-writer", dst)
    (dst / "tools").mkdir(exist_ok=True)
    (dst / "tools" / "mcp.yaml").write_text(MCP_YAML, encoding="utf-8")
    return dst


def test_mcp_yaml_validates_against_schema():
    jsonschema.validate(yaml.safe_load(MCP_YAML), SCHEMA)


def test_claude_adapter_emits_mcp_section(tmp_path):
    agent = _agent_with_mcp(tmp_path)
    out = generate(AgentDef(str(agent)))
    assert "## MCP Servers" in out
    assert "@modelcontextprotocol/server-github" in out
    assert "GITHUB_TOKEN" in out  # env var NAME is fine; values never stored


def test_mcp_yaml_roundtrips_verbatim(tmp_path):
    agent = _agent_with_mcp(tmp_path)
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(generate(AgentDef(str(agent))), encoding="utf-8")
    imported = import_claude_md(str(claude_md), str(tmp_path / "imported"))
    assert validate(str(imported)).valid
    restored = (imported / "tools" / "mcp.yaml").read_text(encoding="utf-8")
    assert yaml.safe_load(restored) == yaml.safe_load(MCP_YAML)
    assert restored.strip() == MCP_YAML.strip()
