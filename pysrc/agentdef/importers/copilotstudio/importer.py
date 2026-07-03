#!/usr/bin/env python3
"""Import Microsoft Copilot Studio agent definitions into a conformant
AgentDef directory.

Source shape: a single agent ``<name>.md`` file (as published in
github/awesome-copilot-studio-agents) with:

  - an *optional* YAML frontmatter block (``name``, ``description``,
    ``domain``, ``vertical``, ``audience``, ``knowledge_sources``,
    ``language``, ``char_count``, ``rai_reviewed``, ``tested``, ``version``,
    ``last_updated``) -- some source files omit this entirely and open
    directly on the H1 title.
  - a body with a consistent H1-wrapped skeleton: ``## Description``,
    ``## Conversation Starters``, ``## Instructions`` (a fenced code block
    meant to be pasted verbatim into the Copilot Studio "Instructions"
    field -- this is the actual system prompt, and is itself a nested
    markdown document with its own H1 + ``##`` sections), ``## Knowledge
    Sources``, ``## Deployment Notes``, ``## Changelog``.

The fenced Instructions block is what actually defines agent behavior, so
it is extracted and run back through ``generic_markdown_import`` (the same
classifier used by ``importers/claude`` and ``importers/copilot``) rather
than being flattened into free text -- that's how its own Role/Objectives/
Avoid/etc. sub-structure gets classified correctly instead of dumped
verbatim into instructions/core.md.

Usage:
    python import.py <path-to-agent>.md --output <agent-directory> [--name <name>]
"""

import argparse
import re
import sys
from pathlib import Path

from agentdef.importers._common import (
    AgentDefWriter,
    ImportReport,
    extract_bullets,
    generic_markdown_import,
    split_frontmatter,
    split_sections,
)

FENCE_BLOCK_RE = re.compile(r"```[^\n]*\n(.*?)\n```", re.DOTALL)
BLOCKQUOTE_DESC_RE = re.compile(r"^>\s*\*\*Description:\*\*\s*(.+)$", re.MULTILINE)

# Frontmatter fields with no direct AgentDef equivalent -- preserved
# verbatim as namespaced manifest extras rather than dropped.
_KNOWN_EXTRA_FRONTMATTER_FIELDS = (
    "domain",
    "vertical",
    "audience",
    "language",
    "rai_reviewed",
    "tested",
    "version",
    "last_updated",
    "char_count",
    "knowledge_sources",
)


def _extract_first_fenced_block(text: str) -> str | None:
    """Return the inner content of the first ``` ... ``` fenced block in
    *text*, or None if there isn't one."""
    m = FENCE_BLOCK_RE.search(text)
    return m.group(1) if m else None


def import_copilotstudio(source_path: str, output_dir: str, name: str | None = None) -> Path:
    src = Path(source_path)
    raw_text = src.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw_text)

    _, top_sections = split_sections(body)
    # Common shape: a single H1 title wraps every ## section below it.
    if len(top_sections) == 1:
        h1_title = top_sections[0].header
        _, sections = split_sections(top_sections[0].content)
    else:
        h1_title = None
        sections = top_sections
    by_header = {s.header.strip().lower(): s for s in sections}

    blockquote_m = BLOCKQUOTE_DESC_RE.search(body)
    description = meta.get("description") or (blockquote_m.group(1).strip() if blockquote_m else "")

    if name:
        agent_name = name
    elif meta.get("name"):
        agent_name = meta["name"]
    elif h1_title:
        agent_name = h1_title
    else:
        agent_name = src.stem

    report = ImportReport(source=str(src), framework="Microsoft Copilot Studio")
    writer = AgentDefWriter(output_dir, agent_name, description=description)

    if meta:
        report.map("YAML frontmatter ('name'/'description') -> agent.md / manifest.yaml")
        present = [k for k in _KNOWN_EXTRA_FRONTMATTER_FIELDS if k in meta]
        if present:
            writer.set_extra_manifest({f"x-copilotstudio-{k}": meta[k] for k in present})
            report.map(
                f"other frontmatter fields ({', '.join(present)}) -> manifest.yaml x-copilotstudio-*"
            )
    else:
        report.infer("no YAML frontmatter found in source; name/description inferred from the H1 title and description blockquote")

    instructions_section = by_header.get("instructions")
    instructions_body = _extract_first_fenced_block(instructions_section.content) if instructions_section else None

    if instructions_body:
        generic_markdown_import(instructions_body, writer, report)
        report.map(
            "'Instructions' fenced code block -> classified via the generic markdown "
            "importer (this is the actual Copilot Studio system prompt)"
        )
    else:
        # No fenced Instructions block found (unexpected shape) -- fall
        # back to classifying the whole body so nothing is silently
        # dropped, matching the "never lose content" rule the other
        # importers follow.
        generic_markdown_import(body, writer, report)
        report.drop(
            "no fenced 'Instructions' code block found in the source; classified "
            "the raw document body instead"
        )

    description_section = by_header.get("description")
    if description_section and description_section.content and description_section.content.strip() != description.strip():
        writer.add_core_text(f"## Description (Copilot Studio listing)\n\n{description_section.content}")
        report.map("'Description' section -> instructions/core.md")

    starters_section = by_header.get("conversation starters")
    if starters_section:
        bullets = extract_bullets(starters_section.content)
        if bullets:
            lines = ["# Conversation Starters", ""] + [f"- {b}" for b in bullets]
            writer.add_knowledge("conversation-starters.md", "\n".join(lines))
            report.map("'Conversation Starters' section -> knowledge/conversation-starters.md")

    knowledge_section = by_header.get("knowledge sources")
    if knowledge_section and knowledge_section.content:
        writer.set_extra_manifest({"x-copilotstudio-knowledge-sources-detail": knowledge_section.content.strip()})
        report.map("'Knowledge Sources' section -> manifest.yaml x-copilotstudio-knowledge-sources-detail")

    deployment_section = by_header.get("deployment notes")
    if deployment_section and deployment_section.content:
        writer.add_instruction_file("deployment-notes.md", f"# Deployment Notes\n\n{deployment_section.content}")
        report.map("'Deployment Notes' section -> instructions/deployment-notes.md")

    if by_header.get("changelog"):
        report.drop("'Changelog' section dropped (framework/versioning metadata, not portable)")

    writer.set_extra_manifest({
        "x-imported-from": {"framework": "microsoft-copilot-studio", "source_file": str(src)},
    })

    return writer.write(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import a Microsoft Copilot Studio agent .md file into an AgentDef directory."
    )
    parser.add_argument("source", help="Path to the Copilot Studio agent .md file.")
    parser.add_argument("--output", "-o", required=True, help="Output AgentDef directory.")
    parser.add_argument("--name", default=None, help="Override the inferred agent name.")
    args = parser.parse_args()

    out = import_copilotstudio(args.source, args.output, args.name)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")
    print("Next: python validation/validate.py", out)


if __name__ == "__main__":
    main()
