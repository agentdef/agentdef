# Copilot Adapter

Generates a `copilot-instructions.md` file from an AgentDef agent directory.

## Output Format

GitHub Copilot reads `.github/copilot-instructions.md` for repository-level custom instructions. The adapter maps AgentDef components to Copilot's instructions, extensions, and task guidance sections.

## Usage

```bash
python generate.py ../../examples/twitter-digest
python generate.py ../../examples/twitter-digest --output .github/copilot-instructions.md
```

## Mapping

| AgentDef | Copilot |
| --------- | ------- |
| `agent.md` | Identity and role |
| `instructions/` | Custom instructions |
| `skills/` | Extensions |
| `workflows/` | Task guidance |

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
