"""Shared utilities for AgentDef *importers* (reverse adapters).

Forward adapters (see ../adapters/) turn an AgentDef directory into a
framework-specific file. Importers do the opposite: they read a
framework-specific file and produce a conformant AgentDef directory.

This module provides:
  - a generic markdown section splitter/classifier shared by the
    markdown-based importers (Claude, GitHub Copilot)
  - an ``AgentDefWriter`` that writes a valid AgentDef directory
    (passes ``validation/validate.py``) from already-classified content
  - an ``ImportReport`` that records what mapped cleanly, what was
    inferred, and what was dropped, per the framework-import skill's
    rules (.agentdef/skills/framework-import/SKILL.md)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "ERROR: PyYAML is required. Install with: pip install pyyaml"
    ) from exc


# ---------------------------------------------------------------------------
# YAML frontmatter (shared by the copilot, copilotstudio, and claude
# importers -- was previously duplicated three times, which is how the bug
# below survived in two of the three copies for a while)
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^-{3,}[ \t]*\n(.*?)\n-{3,}[ \t]*\n(.*)$", re.DOTALL)
_FRONTMATTER_KEY_RE = re.compile(r"^[A-Za-z_][\w-]*$")


def _lenient_frontmatter_parse(frontmatter_text: str) -> dict:
    """Best-effort recovery for frontmatter that isn't strictly valid YAML.

    The most common real-world cause: a plain-scalar value (typically a
    natural-language ``description``) contains its own ``': '`` sequence
    later in the same line -- e.g. ``description: ... Triggers on: 'X'.``
    A strict YAML parser reads that as an attempt to open a nested mapping
    and raises ``ScannerError: mapping values are not allowed here``, which
    would otherwise silently discard name/description/tools/etc. for a
    file that a human would call perfectly reasonable frontmatter.

    This recovers simple flat ``key: value`` frontmatter by splitting each
    top-level (non-indented) line on its *first* colon only. It does not
    attempt to reconstruct genuinely nested/multi-line YAML structures
    (those should parse fine with real YAML in the first place); indented
    continuation lines are appended to the previous scalar value so at
    least the content isn't lost outright.
    """
    result: dict = {}
    current_key: str | None = None
    for line in frontmatter_text.splitlines():
        if not line.strip():
            continue
        if not line[:1].isspace() and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            if _FRONTMATTER_KEY_RE.match(key):
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                    value = value[1:-1]
                result[key] = value
                current_key = key
                continue
        if current_key is not None and isinstance(result.get(current_key), str):
            result[current_key] = f"{result[current_key]} {line.strip()}".strip()
    return result


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return ``(parsed frontmatter dict, body)`` for a file that may start
    with a ``---\\n...\\n---`` YAML frontmatter block. Returns an empty dict
    and the original text unchanged if there's no frontmatter block at all.

    Tries real YAML first (handles nested structures like an MCP server
    config correctly); falls back to :func:`_lenient_frontmatter_parse` for
    the common case of an otherwise-simple frontmatter block that trips up
    strict YAML because of an unescaped colon in a description -- rather
    than silently dropping the whole block, per the "nothing is dropped
    silently" rule the rest of these importers follow.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw_frontmatter, body = m.group(1), m.group(2)
    try:
        meta = yaml.safe_load(raw_frontmatter)
        if not isinstance(meta, dict):
            raise ValueError("frontmatter did not parse to a mapping")
    except Exception:
        meta = _lenient_frontmatter_parse(raw_frontmatter)
    return meta or {}, body.strip()


# ---------------------------------------------------------------------------
# Naming
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"[^a-z0-9_-]+")


def slugify(name: str, fallback: str = "imported-agent") -> str:
    """Turn arbitrary text into a valid manifest ``name`` (^[a-z0-9][a-z0-9_-]*$)."""
    slug = _NAME_RE.sub("-", name.strip().lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug or not re.match(r"^[a-z0-9]", slug):
        slug = f"agent-{slug}" if slug else fallback
    return slug or fallback


# ---------------------------------------------------------------------------
# Generic markdown section splitting (shared by Claude + Copilot importers)
# ---------------------------------------------------------------------------

@dataclass
class Section:
    level: int          # 1 = '#', 2 = '##', etc.
    header: str          # raw header text
    content: str          # body text, with deeper-level subsections nested verbatim


_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_FENCE_RE = re.compile(r"^\s*(```+|~~~+)")


def split_sections(text: str) -> tuple[str, list[Section]]:
    """Split markdown into a leading preamble (before any header) and a list
    of *top-level* header sections, using standard outline nesting: a
    section's content runs until the next header whose level is <= its own
    (siblings/shallower end it; deeper headers stay nested inside its
    content, reconstructed as markdown so a recursive ``split_sections``
    call can descend into them).

    Lines inside fenced code blocks (``` or ~~~) are never treated as
    headers, even if they start with '#' (e.g. a shell/Python/YAML comment
    in an example snippet) — only real markdown headers outside of fences
    count."""
    tokens: list[tuple[int | None, str]] = []  # (header_level_or_None, text)
    in_fence = False
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            tokens.append((None, line))
            continue
        m = None if in_fence else _HEADER_RE.match(line)
        if m:
            tokens.append((len(m.group(1)), m.group(2).strip()))
        else:
            tokens.append((None, line))

    i, n = 0, len(tokens)
    preamble_lines: list[str] = []
    while i < n and tokens[i][0] is None:
        preamble_lines.append(tokens[i][1])
        i += 1

    sections: list[Section] = []
    while i < n:
        level, header = tokens[i]
        i += 1
        body: list[str] = []
        while i < n:
            sub_level, sub_text = tokens[i]
            if sub_level is not None and sub_level <= level:
                break
            body.append(sub_text if sub_level is None else f"{'#' * sub_level} {sub_text}")
            i += 1
        sections.append(Section(level=level, header=header, content="\n".join(body).strip()))

    return "\n".join(preamble_lines).strip(), sections


# Header name -> AgentDef target category, per SPEC.md Appendix A read
# backwards and the framework-import skill's reverse mapping table.
_CATEGORY_SYNONYMS: dict[str, set[str]] = {
    "role": {"role", "identity", "persona", "about", "who you are", "overview"},
    "objectives": {"objectives", "goals", "purpose", "mission"},
    "style": {"style", "tone", "communication style", "formatting", "voice"},
    "priorities": {"priorities", "priority"},
    "avoid": {"avoid", "don't", "do not", "constraints", "limitations"},
    "safety": {"safety", "guardrails", "safety guidelines", "boundaries"},
    "skills": {"skills", "capabilities", "extensions"},
    "workflows": {"workflows", "procedures", "tasks", "playbooks"},
    "tools": {"tools", "integrations", "apis", "actions", "connectors"},
}


def split_roundtrip_segments(body: str) -> list[str]:
    """Split an AgentDef-generated file body on standalone '---' separator
    lines, ignoring any '---' that appears inside a fenced code block.

    Used by the round-trip paths of the claude and copilot importers; a naive
    body.split('\\n---\\n') breaks on YAML frontmatter examples embedded in
    fenced code blocks (found via the P2.4 fixed-point corpus tests).
    """
    segments: list[str] = []
    current: list[str] = []
    fence = None
    for line in body.splitlines():
        stripped = line.strip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            current.append(line)
            continue
        if fence is not None:
            if stripped.startswith(fence):
                fence = None
            current.append(line)
            continue
        if stripped == "---":
            segments.append("\n".join(current).strip())
            current = []
            continue
        current.append(line)
    segments.append("\n".join(current).strip())
    return [s for s in segments if s != ""] or [""]


def classify_header(header: str) -> str:
    """Map a section header to a known AgentDef category, or 'core' if
    it doesn't match a known synonym (falls back into instructions/core.md)."""
    key = header.strip().lower()
    for category, synonyms in _CATEGORY_SYNONYMS.items():
        if key in synonyms:
            return category
    return "core"


_PERSONA_RE = re.compile(
    r"\b(?:You are|You're|Your role is|Your job is|You act as|You serve as|You help)\b"
    r"(?:(?!\n\s*\n).)*?\.",
    re.DOTALL,
)


def find_persona_sentence(text: str) -> str | None:
    """Best-effort extraction of a 'You are ...' / 'Your role is ...' /
    'You help ...' identity sentence from free-form prose, used when no
    explicit Role section exists.

    The sentence is allowed to span a soft line-wrap (a single newline,
    common when prose is hard-wrapped at ~80 columns) but not a full
    paragraph break (blank line), so it won't run away and swallow
    unrelated content looking for the next '.'.
    """
    m = _PERSONA_RE.search(text)
    if m:
        return re.sub(r"\s+", " ", m.group(0)).strip()
    return None


_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_NUMBERED_BULLET_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")


def extract_bullets(text: str) -> list[str]:
    """Pull markdown bullet items out of a section's content. Falls back to
    non-empty lines if there are no bullets at all.

    Handles both unordered (``-``/``*``) and ordered (``1.``/``1)``) source
    lists. Ordered-list markers are stripped here rather than left in the
    returned strings: callers like ``AgentDefWriter._render_agent_md``
    (e.g. for Priorities) apply their own numbering when re-rendering, and
    leaving the original "1. " prefix in place would double up as
    "1. 1. ..." in the generated agent.md.
    """
    bullets = [m.group(1).strip() for line in text.splitlines() if (m := _BULLET_RE.match(line))]
    if bullets:
        return bullets
    numbered = [m.group(1).strip() for line in text.splitlines() if (m := _NUMBERED_BULLET_RE.match(line))]
    if numbered:
        return numbered
    return [line.strip() for line in text.splitlines() if line.strip()]


def generic_markdown_import(text: str, writer: "AgentDefWriter", report: ImportReport) -> None:
    """Best-effort, deterministic import of an arbitrary markdown agent
    definition (CLAUDE.md, copilot-instructions.md, system.md, ...) into an
    AgentDefWriter. Shared by the Claude and GitHub Copilot importers.

    Strategy: split into header sections, classify each header against the
    known AgentDef categories (role/objectives/style/priorities/avoid/
    skills/workflows/tools), and fall back to instructions/core.md for
    anything unrecognized. Nothing is dropped silently.
    """
    preamble, sections = split_sections(text)

    # Common real-world shape: a single H1 title wrapping everything else
    # (e.g. "# My Agent\n\n## Role\n...\n## Objectives\n..."). Standard
    # outline nesting makes that lone H1's content swallow all of its H2+
    # children, so descend into it once when it doesn't classify to
    # anything on its own and has nested sections worth surfacing.
    if len(sections) == 1 and classify_header(sections[0].header) == "core":
        sub_preamble, sub_sections = split_sections(sections[0].content)
        if sub_sections:
            preamble = (preamble + "\n\n" + sub_preamble).strip() if preamble else sub_preamble
            sections = sub_sections

    role_found = False
    for section in sections:
        category = classify_header(section.header)

        if category == "role" and not role_found:
            writer.set_role(section.content or section.header)
            report.map(f"'{section.header}' section -> agent.md Role")
            role_found = True
        elif category == "objectives":
            writer.add_objectives(extract_bullets(section.content))
            report.map(f"'{section.header}' section -> agent.md Objectives")
        elif category == "style":
            writer.add_style(extract_bullets(section.content))
            report.map(f"'{section.header}' section -> agent.md Communication Style")
        elif category == "priorities":
            writer.add_priorities(extract_bullets(section.content))
            report.map(f"'{section.header}' section -> agent.md Priorities")
        elif category == "avoid":
            writer.add_avoid(extract_bullets(section.content))
            report.map(f"'{section.header}' section -> agent.md Avoid")
        elif category == "safety":
            writer.add_instruction_file("safety.md", f"# Safety\n\n{section.content}")
            report.map(f"'{section.header}' section -> instructions/safety.md")
        elif category == "skills":
            _, sub = split_sections(section.content)
            if sub:
                for s in sub:
                    writer.add_skill(s.header, f"# {s.header}\n\n{s.content}")
                report.map(f"'{section.header}' section -> skills/ ({len(sub)} skill(s))")
            else:
                writer.add_skill(section.header, f"# {section.header}\n\n{section.content}")
                report.map(f"'{section.header}' section -> skills/{slugify(section.header)}/")
        elif category == "workflows":
            _, sub = split_sections(section.content)
            if sub:
                for s in sub:
                    writer.add_workflow(s.header, f"# {s.header}\n\n{s.content}")
                report.map(f"'{section.header}' section -> workflows/ ({len(sub)} workflow(s))")
            else:
                writer.add_workflow(section.header, f"# {section.header}\n\n{section.content}")
                report.map(f"'{section.header}' section -> workflows/{slugify(section.header)}.md")
        elif category == "tools":
            _, sub = split_sections(section.content)
            if sub:
                for s in sub:
                    writer.add_tool(s.header, f"# {s.header}\n\n{s.content}")
                report.map(f"'{section.header}' section -> tools/ ({len(sub)} tool(s))")
            else:
                writer.add_tool(section.header, f"# {section.header}\n\n{section.content}")
                report.map(f"'{section.header}' section -> tools/{slugify(section.header)}.md")
        else:
            if section.content:
                writer.add_core_text(f"## {section.header}\n\n{section.content}")
                report.map(f"'{section.header}' section -> instructions/core.md (no specific category matched)")

    if not role_found:
        persona = find_persona_sentence(preamble) or find_persona_sentence(text)
        if persona:
            writer.set_role(persona)
            report.infer("agent.md Role inferred from a 'You are ...' sentence in the source")
        elif preamble:
            first_line = preamble.strip().splitlines()[0]
            writer.set_role(first_line)
            report.infer("agent.md Role inferred from the source's opening line (no explicit Role/Identity section found)")
        elif sections:
            # Real-world docs sometimes have *no* preamble at all (the file
            # opens directly on a header) and no 'You are ...'-style sentence
            # anywhere either -- e.g. a doc that opens with "# Some Agent"
            # then jumps straight into "## Mission". Rather than giving up
            # and leaving a bare placeholder, fall back to the first
            # sentence of the first section's content so Role still says
            # *something* useful instead of nothing.
            first_section_text = sections[0].content or sections[0].header
            first_sentence_m = re.search(r"^(.*?\.)(?:\s|$)", first_section_text, re.DOTALL)
            fallback = (
                re.sub(r"\s+", " ", first_sentence_m.group(1)).strip()
                if first_sentence_m
                else first_section_text.strip().splitlines()[0]
            )
            if fallback:
                writer.set_role(fallback)
                report.infer(
                    "agent.md Role inferred from the first sentence of the first section "
                    "(no explicit Role section, preamble, or 'You are ...' sentence found)"
                )
            else:
                report.infer("agent.md Role could not be inferred; placeholder text was used — please edit manually")
        else:
            report.infer("agent.md Role could not be inferred; placeholder text was used — please edit manually")

    if preamble:
        # Always keep the preamble even when a persona sentence inside it was
        # also used for the Role — a persona sentence is rarely the *only*
        # thing in the preamble (e.g. it may sit alongside YAML frontmatter
        # or other context), and silently discarding the rest would violate
        # the "nothing is dropped silently" rule. A little redundancy with
        # Role is a fair trade for never losing content.
        writer.add_core_text(preamble)
        report.map("leading preamble text -> instructions/core.md")


# ---------------------------------------------------------------------------
# Import report
# ---------------------------------------------------------------------------

@dataclass
class ImportReport:
    source: str
    framework: str
    mapped: list[str] = field(default_factory=list)
    inferred: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)

    def map(self, msg: str) -> None:
        self.mapped.append(msg)

    def infer(self, msg: str) -> None:
        self.inferred.append(msg)

    def drop(self, msg: str) -> None:
        self.dropped.append(msg)

    def render(self) -> str:
        lines = [
            f"# Import Report — {self.framework}",
            "",
            f"Source: `{self.source}`",
            f"Date: {date.today().isoformat()}",
            "",
            "## Mapped cleanly",
            "",
        ]
        lines += [f"- {m}" for m in self.mapped] or ["- (none)"]
        lines += ["", "## Inferred (not explicit in the source)", ""]
        lines += [f"- {m}" for m in self.inferred] or ["- (none)"]
        lines += ["", "## Dropped / framework-specific (not portable)", ""]
        lines += [f"- {m}" for m in self.dropped] or ["- (none)"]
        lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# AgentDef directory writer
# ---------------------------------------------------------------------------

class AgentDefWriter:
    """Accumulates classified content and writes a conformant AgentDef
    directory: agent.md (with Role), manifest.yaml (name + >=1
    instructions), instructions/core.md, plus optional skills/, workflows/,
    tools/, knowledge/, runtime/, and an IMPORT_REPORT.md.
    """

    def __init__(self, output_dir: str, name: str, description: str = ""):
        self.root = Path(output_dir).resolve()
        self.name = slugify(name)
        self.description = description.strip()
        self._role = ""
        self._objectives: list[str] = []
        self._style: list[str] = []
        self._priorities: list[str] = []
        self._avoid: list[str] = []
        self._instructions: list[str] = []     # manifest paths, core.md always first
        self._instruction_files: dict[str, str] = {}
        self._skills: list[str] = []
        self._skill_files: dict[str, str] = {}
        self._workflows: list[str] = []
        self._workflow_files: dict[str, str] = {}
        self._tools: list[str] = []
        self._tool_files: dict[str, str] = {}
        self._knowledge_files: dict[str, str] = {}
        self._runtime: dict | None = None
        self._extra_manifest: dict = {}
        self._core_chunks: list[str] = []

    # -- identity -----------------------------------------------------

    def set_role(self, text: str) -> None:
        self._role = text.strip()

    def add_objectives(self, items: list[str]) -> None:
        self._objectives.extend(i.strip() for i in items if i.strip())

    def add_style(self, items: list[str]) -> None:
        self._style.extend(i.strip() for i in items if i.strip())

    def add_priorities(self, items: list[str]) -> None:
        self._priorities.extend(i.strip() for i in items if i.strip())

    def add_avoid(self, items: list[str]) -> None:
        self._avoid.extend(i.strip() for i in items if i.strip())

    # -- core instructions ---------------------------------------------

    def add_core_text(self, text: str) -> None:
        """Append free text to instructions/core.md."""
        text = text.strip()
        if text:
            self._core_chunks.append(text)

    def add_instruction_file(self, filename: str, content: str) -> None:
        """Write a *named* instructions file (e.g. style.md, safety.md)."""
        rel = f"instructions/{filename}"
        self._instruction_files[rel] = content.strip() + "\n"

    # -- modules ---------------------------------------------------------

    def add_skill(self, name: str, content: str) -> None:
        slug = slugify(name)
        rel_dir = f"skills/{slug}"
        self._skill_files[f"{rel_dir}/SKILL.md"] = content.strip() + "\n"
        if rel_dir not in self._skills:
            self._skills.append(rel_dir)

    def add_workflow(self, name: str, content: str) -> None:
        slug = slugify(name)
        rel = f"workflows/{slug}.md"
        self._workflow_files[rel] = content.strip() + "\n"
        if rel not in self._workflows:
            self._workflows.append(rel)

    def add_tool(self, name: str, content: str, filename: str | None = None) -> None:
        rel = f"tools/{filename}" if filename else f"tools/{slugify(name)}.md"
        self._tool_files[rel] = content.strip() + "\n"
        if rel not in self._tools:
            self._tools.append(rel)

    def add_knowledge(self, filename: str, content: str) -> None:
        self._knowledge_files[f"knowledge/{filename}"] = content.strip() + "\n"

    def set_runtime(self, config: dict) -> None:
        self._runtime = config

    def set_extra_manifest(self, extra: dict) -> None:
        """Custom, namespaced manifest fields (e.g. x-imported-from)."""
        self._extra_manifest.update(extra)

    # -- rendering ---------------------------------------------------------

    def _render_agent_md(self) -> str:
        title = self.name.replace("-", " ").replace("_", " ").title()
        lines = [f"# {title}", "", "## Role", "", (self._role or "").strip() or "(role not specified in source)", ""]
        if self.description and self.description.strip() != self._role.strip():
            # Keep a blank line after the "## Role" header so re-importing the
            # rendered file classifies identically (fixed-point requirement).
            lines.insert(3, self.description)
            lines.insert(3, "")
        if self._objectives:
            lines += ["## Objectives", ""]
            lines += [f"- {o}" for o in self._objectives]
            lines.append("")
        if self._style:
            lines += ["## Communication Style", ""]
            lines += [f"- {s}" for s in self._style]
            lines.append("")
        if self._priorities:
            lines += ["## Priorities", ""]
            lines += [f"{i+1}. {p}" for i, p in enumerate(self._priorities)]
            lines.append("")
        if self._avoid:
            lines += ["## Avoid", ""]
            lines += [f"- {a}" for a in self._avoid]
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def _render_core_md(self) -> str:
        if not self._core_chunks:
            return "# Core Instructions\n\n(no behavioral rules found in source)\n"
        body = "\n\n---\n\n".join(self._core_chunks)
        # Idempotence guard: when re-importing content that already carries
        # our own "# Core Instructions" header (round-trips), do not stack a
        # second copy on top — adapt->import->adapt must reach a fixed point
        # (SPEC Appendix E; found via the P2.4 fixed-point tests).
        if body.lstrip().startswith("# Core Instructions"):
            return body.strip() + "\n"
        return f"# Core Instructions\n\n{body}\n"

    def write(self, report: ImportReport | None = None) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)

        (self.root / "agent.md").write_text(self._render_agent_md(), encoding="utf-8")

        instructions_dir = self.root / "instructions"
        instructions_dir.mkdir(exist_ok=True)
        (instructions_dir / "core.md").write_text(self._render_core_md(), encoding="utf-8")
        manifest_instructions = ["instructions/core.md"]

        for rel, content in self._instruction_files.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            manifest_instructions.append(rel)

        for rel, content in self._skill_files.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        for rel, content in self._workflow_files.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        for rel, content in self._tool_files.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        for rel, content in self._knowledge_files.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        if self._runtime:
            runtime_dir = self.root / "runtime"
            runtime_dir.mkdir(exist_ok=True)
            (runtime_dir / "config.yaml").write_text(
                yaml.safe_dump(self._runtime, sort_keys=False), encoding="utf-8"
            )

        manifest = {
            "name": self.name,
            "version": "0.1.0",
            "description": self.description or f"Imported AgentDef agent: {self.name}",
            "instructions": manifest_instructions,
        }
        if self._skills:
            manifest["skills"] = self._skills
        if self._workflows:
            manifest["workflows"] = self._workflows
        if self._tools:
            manifest["tools"] = self._tools
        manifest.update(self._extra_manifest)

        (self.root / "manifest.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
        )

        if report is not None:
            (self.root / "IMPORT_REPORT.md").write_text(report.render(), encoding="utf-8")

        return self.root
