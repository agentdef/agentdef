# AgentDef — Portable AI Agent Definitions

> **Renamed:** this project was **Agentfile** until 2026-07-03; it is now **AgentDef** (`agentdef`) per the availability study in [NAMING.md](NAMING.md).

> Define your agent once. Run it on any framework.

AgentDef is an open specification for defining AI agents in a framework-independent, human-readable format.

## The Problem

Every AI framework invents its own way to define agents: Claude uses `CLAUDE.md`, OpenAI uses `AGENTS.md`, Cursor uses `cursor-rules.md`, Copilot uses `copilot-instructions.md`...

The concepts are the same. The files are different.

## The Solution

AgentDef defines a canonical directory structure that captures what an agent IS — its identity, instructions, skills, workflows, memory, and tools — separate from HOW it runs.

Framework adapters translate your agent definition into whatever format your target platform needs.

## Quick Start

The smallest valid agent:

```
my-agent/
├── agent.md          # Who is this agent?
├── manifest.yaml     # What does it use?
└── instructions/
    └── core.md       # How does it behave?
```

Copy the [starter template](templates/starter/) and fill in your content.

## CLI

Install the `agentdef` command (editable install from this directory):

```bash
pip install -e .
```

```bash
agentdef validate ./my-agent/
agentdef adapt claude ./my-agent/ --output CLAUDE.md
agentdef import copilotstudio risk-register-manager.md --output ./my-agent/
agentdef list        # show every available adapter/importer framework
```

The CLI is a thin wrapper around the same `validation/`, `adapters/`, and
`importers/` scripts documented below — use whichever is more convenient.
It currently only works from an editable install of this git checkout (it
resolves its sibling `adapters/`/`importers/`/`validation/` directories at
runtime); a fully self-contained PyPI package is planned, see
[PUBLISHING.md](PUBLISHING.md).

## Keep framework files in sync

Declare targets once in `manifest.yaml`, then one command regenerates them all:

```yaml
sync:
  - framework: claude
    output: framework/claude/CLAUDE.md
  - framework: copilot
    output: framework/copilot/copilot-instructions.md
```

```bash
agentdef sync ./my-agent/          # regenerate
agentdef sync ./my-agent/ --check  # CI drift check (exit 1 if stale)
```

## Validate

```bash
agentdef validate ./my-agent/
```

## Adapters

Generate framework-specific files:

```bash
agentdef adapt claude ./my-agent/        # → CLAUDE.md
agentdef adapt openai ./my-agent/        # → AGENTS.md
agentdef adapt cursor ./my-agent/        # → cursor-rules.md
agentdef adapt copilot ./my-agent/       # → copilot-instructions.md
agentdef adapt langgraph ./my-agent/     # → graph.py (LangGraph scaffold)
agentdef adapt m365copilot ./my-agent/   # → declarativeAgent.json
agentdef adapt assistants ./my-agent/    # → OpenAI Assistants create payload
agentdef adapt crewai ./my-agent/        # → crew.yaml (CrewAI agents+tasks)
```

Each adapter supports `--output <file>` to write to a specific path instead of stdout.

## Import

Go the other way: turn an existing framework agent definition into an
AgentDef directory.

```bash
agentdef import claude CLAUDE.md --output ./my-agent          # also Claude Code subagents
agentdef import copilot copilot-instructions.md -o ./my-agent # also *.agent.md
agentdef import m365copilot declarativeAgent.json -o ./my-agent
agentdef import copilotstudio agent-doc.md -o ./my-agent
agentdef import cursor .cursor/rules/api.mdc -o ./my-agent    # also cursor-rules.md
agentdef import openai AGENTS.md -o ./my-agent
agentdef import crewai config/agents.yaml -o ./my-agent
agentdef import letta agent.af -o ./my-agent                  # behavior subset
agentdef import generic SYSTEM.md -o ./my-agent               # any prompt file
```

Each run writes an `IMPORT_REPORT.md` alongside the agent directory listing
what mapped cleanly, what was inferred, and what was dropped. See
[importers/](importers/) for details and the full mapping tables.

## Examples

- [Twitter Weekly Digest](examples/twitter-digest/) — editorial agent that turns saved tweets into weekly briefings
- [Mission Writer](examples/mission-writer/) — structured documentation agent that converts vague requests into actionable mission briefs
- [Claude → AgentDef → Copilot Demo](examples/claude-to-copilot-demo/) — a real, runnable end-to-end example: import a Claude Code subagent, validate it as AgentDef, adapt it to GitHub Copilot. Includes a visual walkthrough (`demo.html`).

## Take the tour

Explore this repo's own architecture as an interactive knowledge graph —
adapters, importers, the CLI, and how they connect:

- **Live:** https://agentdef.github.io/agentdef/dashboard/ (static build, deployed by CI)
- **Locally:** `cd understand-dashboard && npm install && npm run dev` — see the [dashboard tour](docs/dashboard-tour.md)

The graph is generated from the code itself with the **understand-anything** plugin, so it can't silently go stale — regenerating it is a re-scan, not a redraw.

## Documentation

- [Getting Started](docs/getting-started.md) — build your first agent, validate it, generate framework output
- [Dashboard Tour](docs/dashboard-tour.md) — explore this repo's own architecture visually via the generated knowledge-graph dashboard
- [FAQ](docs/faq.md)
- [Comparisons](docs/comparisons.md) — how AgentDef relates to other agent-spec-shaped projects
- [Design Rationale](docs/design-rationale.md)
- [Azure Mapping](docs/azure-mapping.md)

## Specification

Read the full spec: [spec/SPEC.md](spec/SPEC.md)

## Status

See **[STATUS.md](STATUS.md)** for the live "what's done / what's next" picture.

**Spec 0.5.0, tooling 0.2.0** — pre-release, feature-complete for v0.2.0; publication steps pending. Draft specification. The format is stable enough for experimentation and feedback. Breaking changes are possible before 1.0.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
