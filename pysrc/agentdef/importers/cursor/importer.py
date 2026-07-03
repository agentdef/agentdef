#!/usr/bin/env python3
"""Cursor importer (P3.1): cursor-rules.md, legacy .cursorrules, and
.cursor/rules/*.mdc files (MDC frontmatter: description, globs, alwaysApply)
-> AgentDef directory.

Round-trip: detects the AgentDef-generated marker written by
adapters/cursor/generate.py and recovers Agent Identity / Rules / Macros /
Workflows blocks so adapt -> import -> adapt reaches a fixed point.
"""

import argparse
from pathlib import Path

from agentdef.importers._common import (
    AgentDefWriter,
    ImportReport,
    generic_markdown_import,
    slugify,
    split_frontmatter,
    split_roundtrip_segments,
    split_sections,
)

GENERATED_MARKER = "<!-- Generated from AgentDef. Do not edit manually. -->"


def _strip_label(segment: str, label: str) -> str:
    return segment[len(label):].strip() if segment.startswith(label) else segment.strip()


def _import_roundtrip(text: str, writer: AgentDefWriter, report: ImportReport) -> None:
    body = text.split(GENERATED_MARKER, 1)[1].strip()
    segments = split_roundtrip_segments(body)

    first = _strip_label(segments[0], "## Agent Identity")
    generic_markdown_import(first, writer, report)
    report.map("round-trip detected (AgentDef-generated marker found)")

    for segment in segments[1:]:
        if not segment:
            continue
        if segment.startswith("## Rules"):
            content = _strip_label(segment, "## Rules")
            if content:
                writer.add_core_text(content)
            report.map("Rules block -> instructions/core.md [round-trip, original file split not recoverable]")
        elif segment.startswith("## Macros"):
            _, sub = split_sections(segment[len("## Macros"):])
            for s in sub:
                writer.add_skill(s.header, f"# {s.header}\n\n{s.content}")
            report.map(f"Macros block -> skills/ ({len(sub)} skill(s)) [round-trip]")
        elif segment.startswith("## Workflows"):
            _, sub = split_sections(segment[len("## Workflows"):])
            for s in sub:
                writer.add_workflow(s.header, f"# {s.header}\n\n{s.content}")
            report.map(f"Workflows block -> workflows/ ({len(sub)} workflow(s)) [round-trip]")
        else:
            writer.add_core_text(segment)
            report.map("unlabeled block -> instructions/core.md [round-trip]")


def import_cursor(source_path: str, output_dir: str, name: str | None = None) -> Path:
    src = Path(source_path)
    raw = src.read_text(encoding="utf-8", errors="replace")

    if GENERATED_MARKER in raw:
        if name:
            agent_name = name
        else:
            first = raw.lstrip().splitlines()[0]
            agent_name = first.lstrip("# ").split(" — ")[0].strip() or src.stem
        report = ImportReport(source=str(src), framework="Cursor (cursor-rules.md)")
        writer = AgentDefWriter(output_dir, slugify(agent_name, fallback=src.stem))
        _import_roundtrip(raw, writer, report)
        writer.set_extra_manifest({
            "x-imported-from": {"framework": "cursor", "source_file": str(src)},
        })
        return writer.write(report)

    # MDC / plain path. MDC frontmatter keys: description, globs, alwaysApply.
    meta, body = split_frontmatter(raw)

    if name:
        agent_name = name
    elif isinstance(meta.get("name"), str) and meta["name"].strip():
        agent_name = meta["name"]
    else:
        _, top = split_sections(body)
        agent_name = top[0].header if top else src.stem
    agent_name = slugify(agent_name, fallback=src.stem or "cursor-rules")

    label = "Cursor (.mdc rule)" if src.suffix == ".mdc" else "Cursor (cursor-rules.md)"
    report = ImportReport(source=str(src), framework=label)
    writer = AgentDefWriter(output_dir, agent_name, description=str(meta.get("description", "")))

    cursor_meta = {}
    for key in ("globs", "alwaysApply"):
        if key in meta:
            cursor_meta[key] = meta[key]
            report.map(f"MDC frontmatter '{key}' -> manifest x-cursor.{key}")
    if meta.get("description"):
        report.map("MDC frontmatter 'description' -> manifest description")

    generic_markdown_import(body, writer, report)

    extra = {"x-imported-from": {"framework": "cursor", "source_file": str(src)}}
    if cursor_meta:
        extra["x-cursor"] = cursor_meta
    writer.set_extra_manifest(extra)
    return writer.write(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Cursor rules into AgentDef.")
    parser.add_argument("source", help="cursor-rules.md, .cursorrules, or a .cursor/rules/*.mdc file.")
    parser.add_argument("--output", "-o", required=True, help="Output AgentDef directory.")
    parser.add_argument("--name", default=None, help="Override the inferred agent name.")
    args = parser.parse_args()
    out = import_cursor(args.source, args.output, name=args.name)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")


if __name__ == "__main__":
    main()
