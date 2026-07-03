#!/usr/bin/env python3
"""Generate copilot-instructions.md from an AgentDef agent directory.

GitHub Copilot uses .github/copilot-instructions.md for custom instructions
that guide the AI assistant's behavior in the repository.

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
    sections.append(f"# {agent.name} — Copilot Instructions\n")
    sections.append("<!-- Generated from AgentDef. Do not edit manually. -->\n")

    # Identity
    sections.append(agent.agent_md)

    # Instructions
    sections.append("\n---\n")
    sections.append("## Instructions\n")
    for path, content in agent.instructions:
        sections.append(content)
        sections.append("")

    # Extensions from skills
    if agent.skills:
        sections.append("\n---\n")
        sections.append("## Extensions\n")
        for path, content in agent.skills:
            sections.append(content)
            sections.append("")

    # Task guidance from workflows
    if agent.workflows:
        sections.append("\n---\n")
        sections.append("## Task Guidance\n")
        for path, content in agent.workflows:
            sections.append(content)
            sections.append("")

    return "\n".join(sections).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate copilot-instructions.md from AgentDef.")
    parser.add_argument("agent_dir", help="Path to AgentDef agent directory.")
    parser.add_argument("--output", "-o", default=None, help="Output file path.")
    args = parser.parse_args()

    agent = AgentDef(args.agent_dir)
    result = generate(agent)
    write_output(result, args.output)


if __name__ == "__main__":
    main()
