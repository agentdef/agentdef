#!/usr/bin/env python3
"""Generate a CrewAI YAML config (crew.yaml) from an AgentDef agent (P3.4).

Output is a single YAML document with the two mappings CrewAI splits into
config/agents.yaml and config/tasks.yaml: one agent entry (role/goal/
backstory from agent.md) and one task entry per AgentDef workflow. Split it
into CrewAI's two files, or load it programmatically.
"""

import argparse
import re

import yaml

from agentdef.adapters._common import AgentDef, write_output

MARKER = "Generated from AgentDef. Do not edit manually."


def _section(md: str, header: str) -> str:
    m = re.search(rf"^##?\s+{header}\s*\n(.*?)(?=^##?\s|\Z)", md, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def generate(agent: AgentDef) -> str:
    md = agent.agent_md
    role = _section(md, "Role") or agent.name
    objectives = _section(md, "Objectives")
    goal = " ".join(line.lstrip("-* ").strip() for line in objectives.splitlines() if line.strip()) or f"Fulfil the {agent.name} mission."
    backstory_parts = [role]
    style = _section(md, "Style")
    if style:
        backstory_parts.append("Style: " + "; ".join(l.lstrip("-* ").strip() for l in style.splitlines() if l.strip()))
    core = "\n\n".join(content.strip() for _p, content in agent.instructions if content.strip())

    slug = agent.name.replace("-", "_")
    doc = {
        "_comment": MARKER,
        "agents": {
            slug: {
                "role": role.splitlines()[0][:200] if role else agent.name,
                "goal": goal[:400],
                "backstory": "\n\n".join(backstory_parts)[:2000],
            }
        },
        "tasks": {},
    }
    if core:
        doc["agents"][slug]["system_template_note"] = (
            "Full behavioral rules live in the AgentDef definition (instructions/); "
            "inject them via CrewAI custom templates if needed."
        )
    for path, content in agent.workflows:
        lines = [l for l in content.strip().splitlines() if l.strip()]
        title = lines[0].lstrip("# ").strip() if lines else path
        tslug = re.sub(r"[^a-z0-9_]+", "_", title.lower()).strip("_") or "task"
        doc["tasks"][tslug] = {
            "description": content.strip()[:2000],
            "expected_output": f"Completed output of the '{title}' workflow.",
            "agent": slug,
        }
    return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, default_flow_style=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CrewAI crew.yaml from AgentDef.")
    parser.add_argument("agent_dir")
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    write_output(generate(AgentDef(args.agent_dir)), args.output)
    if args.output:
        print(f"Written to {args.output}")


if __name__ == "__main__":
    main()
