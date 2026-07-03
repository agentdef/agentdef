#!/usr/bin/env python3
"""Import GitHub Copilot custom instructions into a conformant AgentDef
directory.

This is the reverse of adapters/copilot/generate.py. Three source shapes are
supported, mirroring what GitHub Copilot actually reads:

  - Repository-wide instructions: a single ``.github/copilot-instructions.md``
    file with free-form markdown.
  - Path-scoped instructions: one or more ``NAME.instructions.md`` files
    under ``.github/instructions/``, each with an ``applyTo: <glob>``
    frontmatter block. Every one of these becomes its own
    ``instructions/<name>.md`` file in the output, with the glob preserved
    as a comment so the scoping isn't silently lost.
  - Custom agents: a single ``NAME.agent.md`` file (e.g. from
    github/awesome-copilot's ``agents/`` directory) with a YAML frontmatter
    block (``name``, ``description``, ``tools``) followed by the agent body.
    The frontmatter is parsed properly rather than left for the generic
    markdown classifier to absorb as plain text.

Usage:
    python import.py <path-to-copilot-instructions.md> --output <agent-directory> \\
        [--instructions-dir <path-to-.github/instructions>] [--name <name>]
"""

import argparse
import sys
from pathlib import Path

from agentdef.importers._common import (
    split_roundtrip_segments,
    AgentDefWriter,
    ImportReport,
    generic_markdown_import,
    slugify,
    split_frontmatter,
    split_sections,
)


def _parse_instructions_file(path: Path) -> tuple[str | None, str]:
    """Return (applyTo glob or None, body) for a NAME.instructions.md file."""
    text = path.read_text(encoding="utf-8")
    frontmatter_meta, body = split_frontmatter(text)
    apply_to = frontmatter_meta.get("applyTo")
    apply_to = apply_to.strip().strip('"') if isinstance(apply_to, str) else apply_to
    return apply_to, body


GENERATED_MARKER = "<!-- Generated from AgentDef. Do not edit manually. -->"


def _import_roundtrip(text, writer, report):
    """Recover structure from a copilot-instructions.md we generated ourselves
    (adapters/copilot/generate.py). Mirrors the claude importer's round-trip
    path so adapt -> import -> adapt reaches a fixed point."""
    body = text.split(GENERATED_MARKER, 1)[1].strip()
    segments = split_roundtrip_segments(body)

    generic_markdown_import(segments[0], writer, report)
    report.map("round-trip detected (AgentDef-generated marker found)")

    for segment in segments[1:]:
        if not segment:
            continue
        if segment.startswith("## Instructions"):
            content = segment[len("## Instructions"):].strip()
            if content:
                writer.add_core_text(content)
            report.map("Instructions block -> instructions/core.md [round-trip, original file split not recoverable]")
        elif segment.startswith("## Extensions"):
            _, sub = split_sections(segment[len("## Extensions"):])
            for s in sub:
                writer.add_skill(s.header, f"# {s.header}\n\n{s.content}")
            report.map(f"Extensions block -> skills/ ({len(sub)} skill(s)) [round-trip]")
        elif segment.startswith("## Task Guidance"):
            _, sub = split_sections(segment[len("## Task Guidance"):])
            for s in sub:
                writer.add_workflow(s.header, f"# {s.header}\n\n{s.content}")
            report.map(f"Task Guidance block -> workflows/ ({len(sub)} workflow(s)) [round-trip]")
        else:
            writer.add_core_text(segment)
            report.map("unlabeled block -> instructions/core.md [round-trip]")


def import_copilot(
    source_path: str,
    output_dir: str,
    instructions_dir: str | None = None,
    name: str | None = None,
) -> Path:
    src = Path(source_path)
    raw_text = src.read_text(encoding="utf-8")

    if GENERATED_MARKER in raw_text:
        if name:
            agent_name = name
        else:
            first = raw_text.lstrip().splitlines()[0]
            agent_name = first.lstrip("# ").split("\u2014")[0].split(" — ")[0].strip() or src.stem
        report = ImportReport(source=str(src), framework="GitHub Copilot (copilot-instructions.md)")
        writer = AgentDefWriter(output_dir, agent_name)
        _import_roundtrip(raw_text, writer, report)
        writer.set_extra_manifest({
            "x-imported-from": {"framework": "copilot", "source_file": str(src)},
        })
        return writer.write(report)

    meta, text = split_frontmatter(raw_text)

    if name:
        agent_name = name
    elif meta.get("name"):
        agent_name = meta["name"]
    else:
        _, top_sections = split_sections(text)
        agent_name = top_sections[0].header if top_sections else src.parent.parent.name or src.stem

    report = ImportReport(source=str(src), framework="GitHub Copilot")
    writer = AgentDefWriter(output_dir, agent_name, description=meta.get("description", ""))

    if meta:
        report.map("YAML frontmatter ('name'/'description') -> agent.md / manifest.yaml")
        tools_meta = meta.get("tools")
        if tools_meta:
            writer.set_extra_manifest({"x-copilot-tools": tools_meta})
            report.map("frontmatter 'tools' -> manifest.yaml x-copilot-tools (no portable AgentDef tools/ equivalent; these are IDE/agent capability flags, not API integrations)")
        leftover_meta = {k: v for k, v in meta.items() if k not in ("name", "description", "tools")}
        if leftover_meta:
            writer.set_extra_manifest({"x-copilot-frontmatter": leftover_meta})
            report.map(f"other frontmatter fields ({', '.join(leftover_meta)}) -> manifest.yaml x-copilot-frontmatter")

    generic_markdown_import(text, writer, report)

    # Auto-detect .github/instructions/ next to a .github/copilot-instructions.md
    if instructions_dir is None:
        candidate = src.parent / "instructions"
        if candidate.is_dir():
            instructions_dir = str(candidate)
            report.map(f"auto-detected path-scoped instructions directory: {candidate}")

    if instructions_dir:
        idir = Path(instructions_dir)
        for f in sorted(idir.glob("*.instructions.md")):
            apply_to, body = _parse_instructions_file(f)
            slug = slugify(f.stem.replace(".instructions", ""))
            header = f"<!-- Scope: applies to `{apply_to}` -->\n\n" if apply_to else ""
            writer.add_instruction_file(f"{slug}.md", header + body)
            scope_note = f" (scoped to `{apply_to}`)" if apply_to else ""
            report.map(f"{f.name}{scope_note} -> instructions/{slug}.md")

    writer.set_extra_manifest({
        "x-imported-from": {
            "framework": "github-copilot",
            "source_file": str(src),
            **({"instructions_dir": str(instructions_dir)} if instructions_dir else {}),
        }
    })

    return writer.write(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import GitHub Copilot custom instructions into an AgentDef directory."
    )
    parser.add_argument("source", help="Path to copilot-instructions.md.")
    parser.add_argument("--output", "-o", required=True, help="Output AgentDef directory.")
    parser.add_argument(
        "--instructions-dir",
        default=None,
        help="Path to .github/instructions/ (path-scoped *.instructions.md files). "
        "Auto-detected as a sibling 'instructions/' directory if omitted.",
    )
    parser.add_argument("--name", default=None, help="Override the inferred agent name.")
    args = parser.parse_args()

    out = import_copilot(args.source, args.output, args.instructions_dir, args.name)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")
    print("Next: python validation/validate.py", out)


if __name__ == "__main__":
    main()
