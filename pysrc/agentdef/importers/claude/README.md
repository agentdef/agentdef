# Claude Importer

Imports a `CLAUDE.md` file, or a Claude Code *subagent* definition file
(`.claude/agents/<name>.md`-style, as published in community collections
like github/awesome-claude-agents and github/awesome-claude-code-subagents),
into a conformant AgentDef directory. Reverse of
[`adapters/claude/`](../../adapters/claude/).

## Usage

```bash
python import.py path/to/CLAUDE.md --output ../../my-agent
python import.py path/to/CLAUDE.md --output ../../my-agent --name my-agent-name
```

## Behavior — three source shapes

1. **Round-trip**: if the file contains the `<!-- Generated from AgentDef.
   Do not edit manually. -->` marker (i.e. it was produced by
   `adapters/claude/generate.py`), the importer recovers
   Role/Objectives/Style/Priorities/Avoid, Skills, and Workflows with high
   fidelity.
2. **Claude Code subagent**: a file opening with a YAML frontmatter block
   (`name`, `description`, `tools`, optionally `model` and other metadata)
   followed by the system-prompt body. The frontmatter is parsed by the
   shared `split_frontmatter()` (see `../_common.py`) rather than left for
   the generic markdown classifier to absorb as noise: `name`/`description`
   map straight to `agent.md`/`manifest.yaml`, `tools` is preserved as
   `manifest.yaml` → `x-claude-tools` (a Claude Code capability flag list,
   not a portable AgentDef `tools/` integration), and any other frontmatter
   fields land in `x-claude-frontmatter`. The body is then run through the
   same generic markdown classification as shape 3.
3. **Generic**: any other CLAUDE.md (no frontmatter, no round-trip marker)
   falls back to generic markdown classification: known section headers
   (Role, Identity, Objectives, Goals, Style, Tone, Priorities, Avoid,
   Skills, Workflows, Tools, Safety/Guardrails — see `../_common.py`) map to
   the matching AgentDef component. Anything unrecognized is preserved in
   `instructions/core.md` rather than dropped.

In shapes 2 and 3, if no Role/Identity section exists, the importer looks
for a "You are ..." sentence, then falls back to the opening line (or first
sentence of the first section). All three cases are marked **inferred** in
`IMPORT_REPORT.md`.

## Mapping

| Claude source | AgentDef |
| -------------- | --------- |
| YAML frontmatter `name`/`description` | `agent.md` / `manifest.yaml` |
| YAML frontmatter `tools` | `manifest.yaml` → `x-claude-tools` |
| Identity / "You are…" prose | `agent.md` → Role |
| Objectives / Goals section | `agent.md` → Objectives |
| Style / Tone section | `agent.md` → Communication Style |
| Skills section | `skills/<name>/SKILL.md` |
| Workflows section | `workflows/<name>.md` |
| Everything else | `instructions/core.md` |

Validated against 187 real Claude Code subagent files from
github/awesome-claude-agents and github/awesome-claude-code-subagents
(0 failures — see CHANGELOG.md).

## Round-trip fidelity (SPEC Appendix E)

One adapt → import cycle reaches a fixed point (tested in
`tests/test_fixedpoint.py` against the examples and real corpus agents).
Field-by-field guarantees:

| Content | Fidelity | Notes |
| ------- | -------- | ----- |
| Role / Objectives / Style / Priorities / Avoid sections | lossless | recovered by section classifier |
| Other `agent.md` sections | lossy-with-report | routed to `instructions/core.md`, flagged in IMPORT_REPORT.md |
| Instruction file *contents* | lossless | concatenated; original multi-file split not recoverable (reported) |
| Instruction file *boundaries* | dropped-with-report | merge into `core.md` separated by `---` |
| Skills / Workflows | lossless | recovered from labeled blocks |
| `manifest.yaml` custom `x-` fields | dropped-with-report | not represented in generated file |
| Literal `---` thematic breaks in content | lossy (first cycle only) | may merge with block separators; stable from cycle 1 on |
