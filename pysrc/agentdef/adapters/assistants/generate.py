#!/usr/bin/env python3
"""Generate an OpenAI Assistants API create-payload (JSON) from an AgentDef
agent directory (P3.5).

Output is the JSON body for POST /v1/assistants: name, description,
instructions (agent.md + instruction files, in manifest order — the
normative concatenation order, SPEC 5.3), model (from runtime/config.yaml
if present, else a placeholder you MUST set), and tools (code_interpreter /
file_search only when declared under manifest `capabilities`).

Usage:
    python generate.py <agent-directory> [--output <file>]
"""

import argparse
import json

from agentdef.adapters._common import AgentDef, write_output

DEFAULT_MODEL = "SET-YOUR-MODEL-HERE"
CAPABILITY_TOOLS = {
    "code-interpreter": {"type": "code_interpreter"},
    "code_interpreter": {"type": "code_interpreter"},
    "file-search": {"type": "file_search"},
    "file_search": {"type": "file_search"},
}


def generate(agent: AgentDef) -> str:
    manifest = agent.manifest

    parts = [agent.agent_md.strip()]
    for _path, content in agent.instructions:
        parts.append(content.strip())
    instructions = "\n\n".join(p for p in parts if p)

    model = DEFAULT_MODEL
    runtime = manifest.get("runtime")
    if isinstance(runtime, dict) and runtime.get("model"):
        model = str(runtime["model"])

    payload = {
        "model": model,
        "name": agent.name[:256],
        "instructions": instructions[:256000],
        "tools": [],
        "metadata": {"generated_from": "AgentDef", "agentdef_marker": "Generated from AgentDef. Do not edit manually."},
    }
    if manifest.get("description"):
        payload["description"] = str(manifest["description"])[:512]

    for cap in manifest.get("capabilities", []) or []:
        tool = CAPABILITY_TOOLS.get(str(cap).lower())
        if tool and tool not in payload["tools"]:
            payload["tools"].append(tool)

    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an OpenAI Assistants create payload from AgentDef.")
    parser.add_argument("agent_dir", help="Path to AgentDef agent directory.")
    parser.add_argument("--output", "-o", default=None, help="Output file path.")
    args = parser.parse_args()
    agent = AgentDef(args.agent_dir)
    write_output(generate(agent), args.output)
    if args.output:
        print(f"Written to {args.output}")


if __name__ == "__main__":
    main()
