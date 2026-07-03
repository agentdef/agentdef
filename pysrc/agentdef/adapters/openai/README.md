# OpenAI Adapter

Generates an `AGENTS.md` file from an AgentDef agent directory.

## Output Format

OpenAI uses `AGENTS.md` as the agent definition file. The adapter maps AgentDef components to OpenAI's system instructions, tools, and execution flow sections.

## Usage

```bash
python generate.py ../../examples/twitter-digest
python generate.py ../../examples/twitter-digest --output AGENTS.md
```

## Mapping

| AgentDef | OpenAI |
| --------- | ------ |
| `agent.md` | System instructions |
| `instructions/` | Behavioral rules |
| `skills/` | Tools / function definitions |
| `workflows/` | Execution flow |
