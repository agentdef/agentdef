# AgentDef Adapters

Adapters translate an AgentDef agent directory into framework-specific files.

## Concept

An AgentDef agent defines **what** an agent is. An adapter translates that definition into **how** a specific framework expects it.

```
AgentDef Directory → Adapter → Framework-Specific File(s)
```

## Available Adapters

| Adapter | Output | Command |
| ------- | ------ | ------- |
| [claude](claude/) | `CLAUDE.md` | `agentdef adapt claude <agent-dir>` |
| [openai](openai/) | `AGENTS.md` | `agentdef adapt openai <agent-dir>` |
| [cursor](cursor/) | `cursor-rules.md` | `agentdef adapt cursor <agent-dir>` |
| [copilot](copilot/) | `.github/copilot-instructions.md` | `agentdef adapt copilot <agent-dir>` |
| [langgraph](langgraph/) | `graph.py` scaffold | `agentdef adapt langgraph <agent-dir>` |

## Usage

All adapters follow the same interface:

```bash
python adapters/<framework>/generate.py <agent-directory> [--output <file>]
```

If `--output` is omitted, the result is printed to stdout.

## Writing Your Own Adapter

Each adapter is a standalone Python script that:

1. Reads `agent.md`, `manifest.yaml`, and referenced files from the agent directory
2. Transforms the content into the target framework's format
3. Outputs the result

All adapters use `_common.py` for shared loading logic. See any existing adapter as a starting point.
