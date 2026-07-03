#!/usr/bin/env python3
"""Generate a Microsoft 365 Copilot declarative agent manifest
(declarativeAgent.json) from an AgentDef agent directory (P3.6).

Closes the loop with importers/m365copilot. Targets declarative agent
schema v1.5 fields that map cleanly from AgentDef: name, description,
instructions (concatenated, 8000-char schema cap), conversation_starters
(from workflow titles). Capabilities/actions are intentionally NOT
invented; declare them in the target platform.

Usage:
    python generate.py <agent-directory> [--output <file>]
"""

import argparse
import json

from agentdef.adapters._common import AgentDef, write_output

SCHEMA_VERSION = "v1.5"
INSTRUCTIONS_CAP = 8000  # declarative agent schema limit


def generate(agent: AgentDef) -> str:
    manifest = agent.manifest
    description = manifest.get("description") or f"{agent.name} (generated from AgentDef)"

    parts = [agent.agent_md.strip()]
    for _path, content in agent.instructions:
        parts.append(content.strip())
    instructions = "\n\n".join(p for p in parts if p)
    truncated = len(instructions) > INSTRUCTIONS_CAP
    if truncated:
        instructions = instructions[: INSTRUCTIONS_CAP - 60].rstrip() + "\n\n[truncated to fit the 8000-char schema limit]"

    doc = {
        "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.5/schema.json",
        "version": SCHEMA_VERSION,
        "name": agent.name[:100],
        "description": str(description)[:1000],
        "instructions": instructions,
    }

    starters = []
    for path, content in agent.workflows:
        title = content.lstrip().splitlines()[0].lstrip("# ").strip() if content.strip() else path
        starters.append({"title": title[:50], "text": f"Run the {title} workflow"[:200]})
    if starters:
        doc["conversation_starters"] = starters[:6]

    comment = "Generated from AgentDef. Do not edit manually."
    doc["$comment"] = comment
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate declarativeAgent.json from AgentDef.")
    parser.add_argument("agent_dir", help="Path to AgentDef agent directory.")
    parser.add_argument("--output", "-o", default=None, help="Output file path.")
    args = parser.parse_args()
    agent = AgentDef(args.agent_dir)
    write_output(generate(agent), args.output)
    if args.output:
        print(f"Written to {args.output}")


if __name__ == "__main__":
    main()
