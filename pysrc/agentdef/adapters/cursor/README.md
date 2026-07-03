# Cursor Adapter

Generates a `cursor-rules.md` file from an AgentDef agent directory.

## Output Format

Cursor uses `cursor-rules.md` at the project root. The adapter maps AgentDef components to Cursor's rules, macros, and workflow sections.

## Usage

```bash
python generate.py ../../examples/twitter-digest
python generate.py ../../examples/twitter-digest --output cursor-rules.md
```

## Mapping

| AgentDef | Cursor |
| --------- | ------ |
| `agent.md` | Agent identity preamble |
| `instructions/` | Rules |
| `skills/` | Macros |
| `workflows/` | Procedural rules |
