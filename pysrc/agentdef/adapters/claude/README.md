# Claude Adapter

Generates a `CLAUDE.md` file from an AgentDef agent directory.

## Output Format

Claude uses a single markdown file (`CLAUDE.md`) at the project root as its system prompt. The adapter concatenates identity, instructions, skills, and workflows into this single file.

## Usage

```bash
python generate.py ../../examples/twitter-digest
python generate.py ../../examples/twitter-digest --output CLAUDE.md
```

## Mapping

| AgentDef | Claude |
| --------- | ------ |
| `agent.md` | System prompt header (role, objectives, style) |
| `instructions/` | Behavioral rules in the system prompt |
| `skills/` | Capability descriptions in the system prompt |
| `workflows/` | Procedural guidance in the system prompt |

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
