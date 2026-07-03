#!/usr/bin/env python3
"""CrewAI importer (P3.4): agents.yaml / tasks.yaml / crew.yaml -> AgentDef.

Accepts either the single-file crew.yaml our adapter emits ({agents, tasks})
or a bare CrewAI config/agents.yaml mapping. Multiple agents in one file
produce one AgentDef directory per agent under the output directory.
Returns the (first) created agent path for single-agent files.
"""

import argparse
from pathlib import Path

import yaml

from agentdef.importers._common import AgentDefWriter, ImportReport, slugify


def _import_one(agent_key: str, spec: dict, tasks: dict, output_dir: str, src: Path) -> Path:
    report = ImportReport(source=str(src), framework="CrewAI (YAML config)")
    name = slugify(agent_key, fallback="crewai-agent")
    writer = AgentDefWriter(output_dir, name, description=str(spec.get("goal", "")))

    role = str(spec.get("role", "")).strip()
    backstory = str(spec.get("backstory", "")).strip()
    goal = str(spec.get("goal", "")).strip()

    writer.set_role(role or "(role not specified in source)")
    report.map("CrewAI 'role' -> agent.md Role")
    if goal:
        writer.add_objectives([goal])
        report.map("CrewAI 'goal' -> agent.md Objectives")
    if backstory and backstory != role:
        writer.add_core_text(f"## Backstory\n\n{backstory}")
        report.map("CrewAI 'backstory' -> instructions/core.md")

    for key in spec:
        if key not in ("role", "goal", "backstory", "system_template_note"):
            writer.add_core_text(f"## CrewAI field: {key}\n\n```yaml\n{yaml.safe_dump({key: spec[key]})}```")
            report.map(f"unrecognized CrewAI agent field '{key}' -> instructions/core.md (verbatim)")

    n = 0
    for tkey, tspec in (tasks or {}).items():
        if not isinstance(tspec, dict):
            continue
        if tspec.get("agent") not in (None, agent_key):
            continue
        desc = str(tspec.get("description", "")).strip()
        expected = str(tspec.get("expected_output", "")).strip()
        body = desc + (f"\n\n**Expected output:** {expected}" if expected else "")
        writer.add_workflow(tkey, f"# {tkey}\n\n{body}")
        n += 1
    if n:
        report.map(f"CrewAI tasks -> workflows/ ({n} task(s))")

    writer.set_extra_manifest({"x-imported-from": {"framework": "crewai", "source_file": str(src)}})
    return writer.write(report)


def import_crewai(source_path: str, output_dir: str, name: str | None = None) -> Path:
    src = Path(source_path)
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{src}: expected a YAML mapping (CrewAI agents/crew config)")

    agents = data.get("agents") if isinstance(data.get("agents"), dict) else None
    tasks = data.get("tasks") if isinstance(data.get("tasks"), dict) else {}
    if agents is None:
        # bare agents.yaml: every top-level dict value with a 'role' is an agent
        agents = {k: v for k, v in data.items() if isinstance(v, dict) and "role" in v}
        if not agents:
            raise ValueError(f"{src}: no CrewAI agent entries found (need 'role' keys)")

    keys = list(agents)
    if name and len(keys) == 1:
        keys = [keys[0]]
    first: Path | None = None
    for key in keys:
        out = Path(output_dir) if len(keys) == 1 else Path(output_dir) / slugify(key, fallback=key)
        path = _import_one(name if (name and len(keys) == 1) else key, agents[key], tasks, str(out), src)
        first = first or path
    return first


def main() -> None:
    parser = argparse.ArgumentParser(description="Import CrewAI YAML config into AgentDef.")
    parser.add_argument("source", help="crew.yaml or CrewAI config/agents.yaml")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--name", default=None)
    args = parser.parse_args()
    out = import_crewai(args.source, args.output, name=args.name)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")


if __name__ == "__main__":
    main()
