#!/usr/bin/env python3
"""Generate a LangGraph Python scaffold from an AgentDef agent directory.

LangGraph uses a graph-based execution model with nodes and edges.
This adapter generates a starter graph.py with nodes derived from
the agent's workflow steps and skills.

Usage:
    python generate.py <agent-directory> [--output <file>]
"""

import argparse
import re
import sys
from pathlib import Path

from agentdef.adapters._common import AgentDef, write_output


def _extract_steps(workflow_content: str) -> list[str]:
    """Extract step names from a workflow markdown file."""
    steps = []
    for match in re.finditer(r"^##\s+Step\s+\d+\s*[—–-]\s*(.+)", workflow_content, re.MULTILINE):
        name = match.group(1).strip()
        # Convert to Python identifier
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
        if slug:
            steps.append(slug)
    return steps


def _extract_role(agent_md: str) -> str:
    """Extract the Role section content from agent.md."""
    match = re.search(r"^##?\s+Role\s*\n(.*?)(?=\n##?\s|\Z)", agent_md, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return "AI agent"


def generate(agent: AgentDef) -> str:
    role = _extract_role(agent.agent_md)

    # Collect workflow steps
    all_steps = []
    for path, content in agent.workflows:
        all_steps.extend(_extract_steps(content))

    if not all_steps:
        all_steps = ["process", "respond"]

    # Collect skill names
    skill_names = []
    for path, _ in agent.skills:
        name = Path(path).name
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
        skill_names.append(slug)

    lines = [
        '"""',
        f"{agent.name} — LangGraph Agent",
        "",
        "Generated from AgentDef. Customize the node implementations.",
        '"""',
        "",
        "from typing import TypedDict",
        "",
        "from langgraph.graph import StateGraph, END",
        "",
        "",
        "# --- State ---",
        "",
        "class AgentState(TypedDict):",
        '    """State passed between graph nodes."""',
        '    input: str',
        '    output: str',
        '    context: dict',
        "",
        "",
        f'SYSTEM_PROMPT = """{role}"""',
        "",
        "",
        "# --- Nodes ---",
        "",
    ]

    for step in all_steps:
        lines.extend([
            f"def {step}(state: AgentState) -> AgentState:",
            f'    """TODO: Implement {step} logic."""',
            f"    return state",
            "",
            "",
        ])

    for skill in skill_names:
        if skill not in all_steps:
            lines.extend([
                f"def {skill}(state: AgentState) -> AgentState:",
                f'    """Skill: {skill}. TODO: Implement."""',
                f"    return state",
                "",
                "",
            ])

    # Build graph
    lines.extend([
        "# --- Graph ---",
        "",
        "def build_graph() -> StateGraph:",
        '    """Construct the agent execution graph."""',
        "    graph = StateGraph(AgentState)",
        "",
    ])

    all_nodes = all_steps + [s for s in skill_names if s not in all_steps]
    for node in all_nodes:
        lines.append(f'    graph.add_node("{node}", {node})')

    lines.append("")
    lines.append(f'    graph.set_entry_point("{all_nodes[0]}")')

    for i in range(len(all_nodes) - 1):
        lines.append(f'    graph.add_edge("{all_nodes[i]}", "{all_nodes[i + 1]}")')

    lines.append(f'    graph.add_edge("{all_nodes[-1]}", END)')
    lines.append("")
    lines.append("    return graph")
    lines.append("")
    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    g = build_graph()")
    lines.append("    app = g.compile()")
    lines.append('    result = app.invoke({"input": "", "output": "", "context": {}})')
    lines.append('    print(result["output"])')
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate LangGraph scaffold from AgentDef.")
    parser.add_argument("agent_dir", help="Path to AgentDef agent directory.")
    parser.add_argument("--output", "-o", default=None, help="Output file path.")
    args = parser.parse_args()

    agent = AgentDef(args.agent_dir)
    result = generate(agent)
    write_output(result, args.output)


if __name__ == "__main__":
    main()
