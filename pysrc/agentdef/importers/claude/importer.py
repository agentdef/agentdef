#!/usr/bin/env python3
"""Import a CLAUDE.md file, or a Claude Code *subagent* definition file,
into a conformant AgentDef directory.

This is the reverse of adapters/claude/generate.py: the framework file is
the input, the AgentDef directory is the output.

Three source shapes are supported:

1. Round-trip: if the file carries the
   "<!-- Generated from AgentDef. Do not edit manually. -->" marker that
   adapters/claude/generate.py writes, the original section structure
   (Role/Objectives/Style/Priorities/Avoid, Skills, Workflows) is recovered
   with high fidelity.
2. Claude Code subagent: a single ``<name>.md`` file (e.g. from
   ``.claude/agents/`` or a community collection like
   github/awesome-claude-agents or github/awesome-claude-code-subagents)
   with a YAML frontmatter block (``name``, ``description``, ``tools``,
   optionally ``model`` and other metadata) followed by the system-prompt
   body. The frontmatter is parsed properly rather than left for the
   generic markdown classifier to absorb as noise.
3. Generic: any other CLAUDE.md (no frontmatter, no round-trip marker) is
   parsed with the same best-effort heuristics used for GitHub Copilot
   instructions (see _common.py).

Usage:
    python import.py <path-to-file.md> --output <agent-directory> [--name <name>]
"""

import argparse
import sys
from pathlib import Path

from agentdef.importers._common import (
    split_roundtrip_segments,
    AgentDefWriter,
    ImportReport,
    generic_markdown_import,
    split_frontmatter,
    split_sections,
)

GENERATED_MARKER = "<!-- Generated from AgentDef. Do not edit manually. -->"


def _import_roundtrip(text: str, writer: AgentDefWriter, report: ImportReport) -> None:
    """Recover structure from a file we generated ourselves."""
    body = text.split(GENERATED_MARKER, 1)[1].strip()
    segments = split_roundtrip_segments(body)

    # First segment is the original agent.md content verbatim.
    generic_markdown_import(segments[0], writer, report)
    report.map("round-trip detected (AgentDef-generated marker found)")

    for segment in segments[1:]:
        if not segment:
            continue
        if segment.startswith("# Skills"):
            _, sub = split_sections(segment[len("# Skills"):])
            for s in sub:
                writer.add_skill(s.header, f"# {s.header}\n\n{s.content}")
            report.map(f"Skills block -> skills/ ({len(sub)} skill(s)) [round-trip]")
        elif segment.startswith("# Workflows"):
            _, sub = split_sections(segment[len("# Workflows"):])
            for s in sub:
                writer.add_workflow(s.header, f"# {s.header}\n\n{s.content}")
            report.map(f"Workflows block -> workflows/ ({len(sub)} workflow(s)) [round-trip]")
        elif segment.startswith("## MCP Servers"):
            body_lines = segment.splitlines()
            inside = False
            yaml_lines = []
            for line in body_lines:
                if line.strip().startswith("```"):
                    inside = not inside
                    continue
                if inside:
                    yaml_lines.append(line)
            writer.add_tool("mcp", "\n".join(yaml_lines).rstrip() + "\n", filename="mcp.yaml")
            report.map("MCP Servers block -> tools/mcp.yaml [round-trip, verbatim]")
        else:
            writer.add_core_text(segment)
            report.map("instructions block -> instructions/core.md [round-trip, original file split not recoverable]")


def import_claude_md(source_path: str, output_dir: str, name: str | None = None) -> Path:
    src = Path(source_path)
    text = src.read_text(encoding="utf-8")

    if GENERATED_MARKER in text:
        # Round-trip path: name comes from the recovered content, frontmatter
        # doesn't apply to our own generated files.
        if name:
            agent_name = name
        else:
            _, top_sections = split_sections(text)
            agent_name = top_sections[0].header if top_sections else src.stem

        report = ImportReport(source=str(src), framework="Claude (CLAUDE.md)")
        writer = AgentDefWriter(output_dir, agent_name)
        _import_roundtrip(text, writer, report)

        writer.set_extra_manifest({
            "x-imported-from": {"framework": "claude", "source_file": str(src)},
        })
        return writer.write(report)

    meta, body = split_frontmatter(text)

    if name:
        agent_name = name
    elif meta.get("name"):
        agent_name = meta["name"]
    else:
        _, top_sections = split_sections(body)
        agent_name = top_sections[0].header if top_sections else src.stem

    framework_label = "Claude (Claude Code subagent)" if meta else "Claude (CLAUDE.md)"
    report = ImportReport(source=str(src), framework=framework_label)
    writer = AgentDefWriter(output_dir, agent_name, description=meta.get("description", ""))

    if meta:
        report.map("YAML frontmatter ('name'/'description') -> agent.md / manifest.yaml")
        tools_meta = meta.get("tools")
        if tools_meta:
            writer.set_extra_manifest({"x-claude-tools": tools_meta})
            report.map(
                "frontmatter 'tools' -> manifest.yaml x-claude-tools (no portable AgentDef "
                "tools/ equivalent; these are Claude Code capability flags, not API integrations)"
            )
        leftover_meta = {k: v for k, v in meta.items() if k not in ("name", "description", "tools")}
        if leftover_meta:
            writer.set_extra_manifest({"x-claude-frontmatter": leftover_meta})
            report.map(f"other frontmatter fields ({', '.join(leftover_meta)}) -> manifest.yaml x-claude-frontmatter")

    generic_markdown_import(body, writer, report)

    writer.set_extra_manifest({
        "x-imported-from": {
            "framework": "claude",
            "source_file": str(src),
        }
    })

    return writer.write(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import CLAUDE.md into an AgentDef directory.")
    parser.add_argument("source", help="Path to the CLAUDE.md file to import.")
    parser.add_argument("--output", "-o", required=True, help="Output AgentDef directory.")
    parser.add_argument("--name", default=None, help="Override the inferred agent name.")
    args = parser.parse_args()

    out = import_claude_md(args.source, args.output, args.name)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")
    print("Next: python validation/validate.py", out)


if __name__ == "__main__":
    main()
