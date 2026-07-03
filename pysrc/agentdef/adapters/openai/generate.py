#!/usr/bin/env python3
"""Generate AGENTS.md from an AgentDef agent directory.

OpenAI uses AGENTS.md as the agent definition file, structured with
system instructions, tools, and behavioral guidance.

Usage:
    python generate.py <agent-directory> [--output <file>]
"""

import argparse
import sys
from pathlib import Path

from agentdef.adapters._common import AgentDef, write_output


def generate(agent: AgentDef) -> str:
    sections = []

    # Header
    sections.append(f"# {agent.name}\n")
    sections.append("<!-- Generated from AgentDef. Do not edit manually. -->\n")

    # System Instructions from agent.md
    sections.append("## System Instructions\n")
    sections.append(agent.agent_md)

    # Behavioral rules from instructions
    for path, content in agent.instructions:
        sections.append(f"\n---\n")
        sections.append(content)

    # Tools / Skills
    if agent.skills:
        sections.append("\n---\n")
        sections.append("## Tools\n")
        for path, content in agent.skills:
            sections.append(content)
            sections.append("")

    # Execution flow
    if agent.workflows:
        sections.append("\n---\n")
        sections.append("## Execution Flow\n")
        for path, content in agent.workflows:
            sections.append(content)
            sections.append("")

    return "\n".join(sections).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate AGENTS.md from AgentDef.")
    parser.add_argument("agent_dir", help="Path to AgentDef agent directory.")
    parser.add_argument("--output", "-o", default=None, help="Output file path.")
    args = parser.parse_args()

    agent = AgentDef(args.agent_dir)
    result = generate(agent)
    write_output(result, args.output)


if __name__ == "__main__":
    main()
