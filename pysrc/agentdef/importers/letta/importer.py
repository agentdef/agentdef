#!/usr/bin/env python3
"""Letta Agent File (.af) importer (P3.7): behavior-relevant subset only.

Letta's .af serializes a *stateful* agent (memory blocks, message history,
tool state, LLM config — see github.com/letta-ai/agent-file). AgentDef
captures portable behavior definitions, so this importer maps the behavior
subset (name, description, system prompt, persona block, tool names) and
explicitly REPORTS every state field it drops, by name. This is the
interop bridge, not a lossless converter.
"""

import argparse
import json
from pathlib import Path

from agentdef.importers._common import AgentDefWriter, ImportReport, find_persona_sentence, slugify

STATE_FIELDS = (
    "messages", "message_ids", "in_context_message_indices", "core_memory",
    "archival_memory", "recall_memory", "llm_config", "embedding_config",
    "tool_rules", "tool_exec_environment_variables", "sources", "tags",
    "metadata_", "created_at", "updated_at",
)


def import_letta(source_path: str, output_dir: str, name: str | None = None) -> Path:
    src = Path(source_path)
    data = json.loads(src.read_text(encoding="utf-8"))

    # .af top level may be the agent object or {"agents": [...]}
    agent = data
    if isinstance(data.get("agents"), list) and data["agents"]:
        agent = data["agents"][0]

    agent_name = name or agent.get("name") or src.stem
    report = ImportReport(source=str(src), framework="Letta Agent File (.af)")
    writer = AgentDefWriter(output_dir, slugify(str(agent_name), fallback=src.stem),
                            description=str(agent.get("description", "") or ""))

    system = str(agent.get("system", "") or "").strip()
    persona_text = ""
    for block in agent.get("memory_blocks", agent.get("blocks", [])) or []:
        if isinstance(block, dict) and block.get("label") == "persona":
            persona_text = str(block.get("value", "")).strip()

    role = find_persona_sentence(persona_text or system) or persona_text.splitlines()[0].strip() if persona_text else ""
    if not role and system:
        role = system.splitlines()[0].strip()
    writer.set_role(role or "(role not specified in source)")
    if role:
        report.infer("agent.md Role inferred from persona block / system prompt")

    if system:
        writer.add_core_text(f"## System prompt\n\n{system}")
        report.map("'system' -> instructions/core.md")
    if persona_text:
        writer.add_core_text(f"## Persona\n\n{persona_text}")
        report.map("persona memory block -> instructions/core.md")

    tools = agent.get("tools") or []
    tool_names = [t.get("name") if isinstance(t, dict) else str(t) for t in tools]
    tool_names = [t for t in tool_names if t]
    if tool_names:
        listing = "\n".join(f"- {t}" for t in tool_names)
        writer.add_tool("letta-tools", f"# Letta tools\n\nDeclared in source (definitions not portable):\n\n{listing}")
        report.map(f"tool names -> tools/letta-tools.md ({len(tool_names)} tool(s); definitions/state dropped)")

    for field in STATE_FIELDS:
        if field in agent:
            report.drop(f"Letta state field '{field}' — runtime state is out of AgentDef's scope (SPEC 5.6)")

    writer.set_extra_manifest({"x-imported-from": {"framework": "letta", "source_file": str(src)}})
    return writer.write(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a Letta .af agent file (behavior subset) into AgentDef.")
    parser.add_argument("source", help="Path to the .af (JSON) file.")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--name", default=None)
    args = parser.parse_args()
    out = import_letta(args.source, args.output, name=args.name)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")


if __name__ == "__main__":
    main()
