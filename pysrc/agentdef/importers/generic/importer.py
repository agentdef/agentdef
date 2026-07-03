#!/usr/bin/env python3
"""Generic markdown importer (P3.3): turn ANY markdown/prompt/persona file
into a conformant AgentDef directory, with zero framework assumptions.

Never fails on well-formed text input: everything the classifier does not
recognize lands in instructions/core.md and is flagged in IMPORT_REPORT.md
(the "nothing dropped silently" invariant, SPEC Appendix E).

Usage:
    agentdef import generic SYSTEM.md --output ./my-agent
"""

import argparse
from pathlib import Path

from agentdef.importers._common import (
    AgentDefWriter,
    ImportReport,
    generic_markdown_import,
    slugify,
    split_frontmatter,
    split_sections,
)


def import_generic(source_path: str, output_dir: str, name: str | None = None) -> Path:
    src = Path(source_path)
    raw = src.read_text(encoding="utf-8", errors="replace")

    meta, body = split_frontmatter(raw)

    if name:
        agent_name = name
    elif isinstance(meta.get("name"), str) and meta["name"].strip():
        agent_name = meta["name"]
    else:
        _, top = split_sections(body)
        agent_name = top[0].header if top else src.stem
    agent_name = slugify(agent_name, fallback=src.stem or "imported-agent")

    report = ImportReport(source=str(src), framework="generic markdown")
    writer = AgentDefWriter(output_dir, agent_name, description=str(meta.get("description", "")))

    if meta:
        report.map("YAML frontmatter parsed (name/description used; rest preserved in manifest)")
        extras = {k: v for k, v in meta.items() if k not in ("name", "description")}
        if extras:
            writer.set_extra_manifest({"x-imported-frontmatter": extras})

    generic_markdown_import(body, writer, report)
    writer.set_extra_manifest({
        "x-imported-from": {"framework": "generic", "source_file": str(src)},
    })
    return writer.write(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import any markdown/prompt file into AgentDef.")
    parser.add_argument("source", help="Path to the source markdown file.")
    parser.add_argument("--output", "-o", required=True, help="Output AgentDef directory.")
    parser.add_argument("--name", default=None, help="Override the inferred agent name.")
    args = parser.parse_args()
    out = import_generic(args.source, args.output, name=args.name)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")


if __name__ == "__main__":
    main()
