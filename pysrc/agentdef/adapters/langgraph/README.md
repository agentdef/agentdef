# LangGraph Adapter

Generates a `graph.py` scaffold from an AgentDef agent directory.

## Output Format

LangGraph uses a graph-based execution model. The adapter creates a Python file with a `StateGraph` whose nodes are derived from the agent's workflow steps and skills.

The generated code is a **scaffold** — node implementations are left as TODOs for the developer to fill in.

## Usage

```bash
python generate.py ../../examples/twitter-digest
python generate.py ../../examples/twitter-digest --output graph.py
```

## Mapping

| AgentDef | LangGraph |
| --------- | --------- |
| `agent.md` Role | `SYSTEM_PROMPT` constant |
| `workflows/` steps | Graph nodes (sequential edges) |
| `skills/` | Additional graph nodes |
| `manifest.yaml` | Graph construction metadata |
