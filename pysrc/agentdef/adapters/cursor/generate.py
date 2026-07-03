#!/usr/bin/env python3
"""Generate cursor-rules.md from an AgentDef agent directory.

Cursor uses a cursor-rules.md file that contains
rules and instructions for the AI assistant within the editor.

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
    sections.append(f"# {agent.name} — Cursor Rules\n")
    sections.append("<!-- Generated from AgentDef. Do not edit manually. -->\n")

    # Identity as rules preamble
    sections.append("## Agent Identity\n")
    sections.append(agent.agent_md)

    # Rules from instructions
    sections.append("\n---\n")
    sections.append("## Rules\n")
    for path, content in agent.instructions:
        sections.append(content)
        sections.append("")

    # Macros from skills
    if agent.skills:
        sections.append("\n---\n")
        sections.append("## Macros\n")
        for path, content in agent.skills:
            sections.append(content)
            sections.append("")

    # Workflows as procedural rules
    if agent.workflows:
        sections.append("\n---\n")
        sections.append("## Workflows\n")
        for path, content in agent.workflows:
            sections.append(content)
            sections.append("")

    return "\n".join(sections).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate cursor-rules.md from AgentDef.")
    parser.add_argument("agent_dir", help="Path to AgentDef agent directory.")
    parser.add_argument("--output", "-o", default=None, help="Output file path.")
    args = parser.parse_args()

    agent = AgentDef(args.agent_dir)
    result = generate(agent)
    write_output(result, args.output)


if __name__ == "__main__":
    main()
