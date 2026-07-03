# Demo: Claude Subagent → AgentDef → GitHub Copilot

A real, runnable end-to-end example showing AgentDef's round-trip in action: take an existing Claude Code subagent, convert it to a portable AgentDef agent, then generate a GitHub Copilot instructions file from it — with no manual editing at any step.

## The pipeline

```
00-source-claude-subagent.md   (real Claude Code subagent format)
        │
        │  agentdef import claude ...
        ▼
01-agentdef/                  (portable AgentDef agent directory)
        │
        │  agentdef adapt copilot ...
        ▼
02-copilot-instructions.md     (GitHub Copilot instructions format)
```

## Reproduce it yourself

From the `agentdef/` directory:

```bash
agentdef import claude examples/claude-to-copilot-demo/00-source-claude-subagent.md \
  --output examples/claude-to-copilot-demo/01-agentdef

agentdef validate examples/claude-to-copilot-demo/01-agentdef

agentdef adapt copilot examples/claude-to-copilot-demo/01-agentdef \
  --output examples/claude-to-copilot-demo/02-copilot-instructions.md
```

All three files in this directory were generated exactly this way — nothing here was hand-edited after generation.

## What to notice

1. **The source is a real Claude Code subagent shape**: YAML frontmatter (`name`, `description`, `tools`, `model`) followed by a system-prompt body with `## Role`, `## Objectives`, `## Priorities`, etc. — the same shape found across community collections like `awesome-claude-agents`.
2. **The importer classifies each section deterministically** — see `01-agentdef/IMPORT_REPORT.md`: every section mapped cleanly to a known AgentDef category (Role, Objectives, Communication Style, Priorities, Avoid, a dedicated `instructions/safety.md` for the Safety section). Nothing was dropped, nothing was guessed.
3. **Framework-specific metadata isn't lost, it's namespaced**: the `tools` and `model` frontmatter fields aren't portable to other frameworks, so they land in `manifest.yaml` under `x-claude-tools` / `x-claude-frontmatter` rather than being silently discarded.
4. **The AgentDef directory validates cleanly** (`agentdef validate` → `PASS`) before it's ever adapted to another framework — round-tripping through a conformant intermediate format, not a direct file-to-file conversion.
5. **The Copilot output carries the round-trip marker** (`<!-- Generated from AgentDef. Do not edit manually. -->`). If this same AgentDef agent is later adapted back to Claude's `CLAUDE.md` format, or if this Copilot file needs re-importing, that marker is what lets the tooling recover the original section structure instead of falling back to generic best-effort parsing.

## Try a different target framework

The same `01-agentdef/` directory can be adapted to any of the other four supported frameworks with no re-import needed:

```bash
agentdef adapt claude    examples/claude-to-copilot-demo/01-agentdef --output CLAUDE.md
agentdef adapt openai    examples/claude-to-copilot-demo/01-agentdef --output AGENTS.md
agentdef adapt cursor    examples/claude-to-copilot-demo/01-agentdef --output cursor-rules.md
agentdef adapt langgraph examples/claude-to-copilot-demo/01-agentdef --output graph.py
```

That's the point of the intermediate format: define the agent once, generate for as many frameworks as you need.
