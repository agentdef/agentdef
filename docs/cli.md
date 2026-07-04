# CLI & Frameworks Reference

Install: `pip install agentdef` (self-contained; adapters, importers,
validator, and JSON Schemas ship in the wheel).

## Commands

| Command | What it does |
| ------- | ------------ |
| `agentdef init <dir> [--yes] [--frameworks a,b]` | Scaffold a new, valid agent (interactive unless `--yes`) |
| `agentdef validate <dir>` | Check conformance (SPEC §10 rules; machine-readable error codes) |
| `agentdef adapt <framework> <dir> [--output F]` | Generate a framework-specific file from the agent |
| `agentdef import <framework> <file> --output <dir> [--name N]` | Convert an existing framework file into an agent (+ `IMPORT_REPORT.md`) |
| `agentdef sync <dir> [--check]` | Regenerate every file declared under `sync:` in the manifest; `--check` exits 1 on drift |
| `agentdef list` | Show every available adapter and importer |

## Adapters (AgentDef → framework)

| Framework | Output | Notes |
| --------- | ------ | ----- |
| `claude` | `CLAUDE.md` | includes `tools/mcp.yaml` as an MCP Servers block; round-trips |
| `copilot` | `copilot-instructions.md` | round-trips |
| `cursor` | `cursor-rules.md` | round-trips |
| `openai` | `AGENTS.md` | round-trips |
| `langgraph` | `graph.py` | executable scaffold; node logic is yours |
| `m365copilot` | `declarativeAgent.json` | declarative agent manifest |
| `assistants` | `assistant.json` | OpenAI Assistants API create payload |
| `crewai` | `crew.yaml` | agents + tasks YAML |

## Importers (framework → AgentDef)

| Framework | Input | Notes |
| --------- | ----- | ----- |
| `claude` | `CLAUDE.md`, Claude Code subagent files | frontmatter-aware; detects round-trip marker |
| `copilot` | `copilot-instructions.md`, `*.agent.md`, path-scoped instructions | |
| `copilotstudio` | Copilot Studio agent docs | extracts the fenced Instructions block |
| `m365copilot` | `declarativeAgent.json` (schema v1.0–1.7) | |
| `cursor` | `.cursor/rules/*.mdc`, `cursor-rules.md`, `.cursorrules` | MDC `globs`/`alwaysApply` → `x-cursor` |
| `openai` | `AGENTS.md` | |
| `crewai` | `crew.yaml`, `config/agents.yaml` | multi-agent files → one directory per agent |
| `letta` | `.af` (Letta Agent File) | behavior subset; state fields reported as dropped |
| `generic` | any markdown prompt/persona file | never fails; everything lands somewhere visible |

Every import writes an `IMPORT_REPORT.md` with three sections — **Mapped**,
**Inferred**, **Dropped** — as required by SPEC Appendix E.

## Validator error codes

| Code | Rule | Meaning |
| ---- | ---- | ------- |
| `missing-agent-md` | 1 | `agent.md` absent |
| `missing-role` | 1 | no Role section in `agent.md` |
| `missing-manifest` | 2 | `manifest.yaml` absent |
| `invalid-yaml` | 2 | manifest unparseable or not a mapping |
| `missing-core-instructions` | 3 | `instructions/core.md` absent |
| `missing-reference` | 4 | manifest references a nonexistent path |
| `reference-escapes-root` | 5 | reference resolves outside the agent directory |
| `schema-violation` | 2, 6 | manifest violates the JSON Schema |
| `unsupported-spec-version` | 7 | `spec_version` unknown to this validator |
