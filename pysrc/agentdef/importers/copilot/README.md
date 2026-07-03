# GitHub Copilot Importer

Imports GitHub Copilot custom instructions into a conformant AgentDef
directory. Reverse of [`adapters/copilot/`](../../adapters/copilot/).

## Inputs

- `.github/copilot-instructions.md` — repository-wide instructions
  (required).
- `.github/instructions/*.instructions.md` — optional path-scoped
  instruction files, each with an `applyTo: <glob>` frontmatter block.
  Auto-detected as a sibling `instructions/` directory next to the source
  file, or pass `--instructions-dir` explicitly.

## Usage

```bash
python import.py .github/copilot-instructions.md --output ../../my-agent
python import.py .github/copilot-instructions.md --output ../../my-agent \
    --instructions-dir .github/instructions
```

## Behavior

- `copilot-instructions.md` is parsed with the same generic markdown
  classification as the Claude importer (see `../_common.py`).
- Each `NAME.instructions.md` file becomes its own
  `instructions/<name>.md` in the output. Its `applyTo` glob is preserved
  as a leading HTML comment (`<!-- Scope: applies to \`glob\` -->`) since
  AgentDef's `instructions/` doesn't have a native path-scoping concept —
  this is noted in `IMPORT_REPORT.md` rather than silently dropped.

## Mapping

| GitHub Copilot | AgentDef |
| --------------- | --------- |
| `copilot-instructions.md` body | `agent.md` + `instructions/core.md` (generic classification) |
| `NAME.instructions.md` (+ `applyTo`) | `instructions/<name>.md` (scope noted in a comment) |

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
