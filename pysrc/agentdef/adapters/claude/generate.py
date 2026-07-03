#!/usr/bin/env python3
"""Generate CLAUDE.md from an AgentDef agent directory.

Claude uses a single CLAUDE.md file at the project root that contains
the system prompt: identity, instructions, skills, and workflow guidance.

Usage:
    python generate.py <agent-directory> [--output <file>]
"""

import argparse
import sys
from pathlib import Path

from agentdef.adapters._common import AgentDef, write_output


def _mcp_section(agent: AgentDef) -> str | None:
    """P3.8: surface tools/mcp.yaml as a labeled block so Claude tooling can
    lift it into .mcp.json, and so the importer can restore it verbatim."""
    mcp = agent.root / "tools" / "mcp.yaml"
    if not mcp.exists():
        return None
    content = mcp.read_text(encoding="utf-8").rstrip()
    return "## MCP Servers\n\n```yaml\n" + content + "\n```"


def generate(agent: AgentDef) -> str:
    sections = []

    # Header
    sections.append(f"# {agent.name}\n")
    sections.append("<!-- Generated from AgentDef. Do not edit manually. -->\n")

    # Identity from agent.md
    sections.append(agent.agent_md)

    # Instructions
    for path, content in agent.instructions:
        sections.append(f"\n---\n")
        sections.append(content)

    # Skills
    if agent.skills:
        sections.append("\n---\n")
        sections.append("# Skills\n")
        for path, content in agent.skills:
            sections.append(content)
            sections.append("")

    # Workflows
    if agent.workflows:
        sections.append("\n---\n")
        sections.append("# Workflows\n")
        for path, content in agent.workflows:
            sections.append(content)
            sections.append("")

    mcp = _mcp_section(agent)
    if mcp:
        sections.append("\n---\n")
        sections.append(mcp)

    return "\n".join(sections).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate CLAUDE.md from AgentDef.")
    parser.add_argument("agent_dir", help="Path to AgentDef agent directory.")
    parser.add_argument("--output", "-o", default=None, help="Output file path.")
    args = parser.parse_args()

    agent = AgentDef(args.agent_dir)
    result = generate(agent)
    write_output(result, args.output)


if __name__ == "__main__":
    main()
