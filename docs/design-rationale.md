# Design Rationale

This document explains the key design decisions behind AgentDef and the reasoning that led to them.

## Why AgentDef Exists

The AI agent ecosystem has a fragmentation problem. Every framework and platform defines agents differently: Claude uses `CLAUDE.md`, OpenAI uses `AGENTS.md`, Cursor uses `cursor-rules.md`, Copilot uses `copilot-instructions.md`, LangGraph uses Python graph definitions. The underlying concepts — identity, instructions, skills, workflows, memory — are the same across all of them. Only the file formats differ.

This fragmentation creates real costs. Teams that use multiple AI tools must maintain redundant definitions. Switching frameworks means rewriting agent configurations from scratch. Knowledge about how to define a good agent is locked inside framework-specific conventions.

AgentDef addresses this by defining a canonical structure for what an agent IS, separate from how any specific framework represents it. Framework adapters handle the translation.

## Design Decisions

### Markdown-First, Not Code-First

Agent definitions are primarily markdown files, not Python classes or YAML schemas. This is intentional.

Markdown is readable by humans who are not programmers. It works with any text editor. It diffs cleanly in Git. It can be reviewed in a pull request without understanding a programming language. The people who define agent behavior — product managers, domain experts, content strategists — should be able to read and edit agent definitions directly.

Code belongs in adapters and runtime configurations, not in the canonical definition.

### Directory Structure, Not a Single File

AgentDef uses a directory with multiple files rather than a single monolithic configuration file. This supports separation of concerns: identity is separate from instructions, which are separate from skills and workflows. Each file has a clear responsibility.

This also enables composition. A skill directory can be shared across multiple agents. Instructions can be swapped without touching the identity. Workflows can be versioned independently.

### Manifest as Composition Layer

The `manifest.yaml` file declares which modules an agent uses without duplicating their content. It is a bill of materials, not a configuration dump. This makes it easy to see at a glance what an agent is composed of, and to validate that all referenced files exist.

### Minimal Required Files

Only three files are required: `agent.md`, `manifest.yaml`, and `instructions/core.md`. Everything else is optional. This keeps the barrier to entry low — you can define a useful agent in under 20 lines of markdown — while allowing complex agents to grow into the full directory structure.

### Adapters, Not Transpilers

Adapters are intentionally simple. They read markdown and YAML, concatenate and restructure the content, and output the target format. They do not parse natural language, infer intent, or apply complex transformations. The semantic content stays in the AgentDef files; adapters handle formatting.

This makes adapters easy to write, easy to debug, and easy to trust. If the output is wrong, the fix is in the AgentDef source, not in adapter logic.

### No Runtime, No Execution

AgentDef defines agent structure. It does not define how agents execute, how they call APIs, how they manage state at runtime, or how they are deployed. These are framework concerns. Mixing definition with execution would make the spec framework-dependent, which defeats the purpose.

### Extensibility Without Breaking Compatibility

Agents can include custom directories and custom manifest fields. Validators and adapters must ignore what they don't recognize. This ensures that teams can extend AgentDef for their needs without waiting for the spec to evolve, and without breaking existing tooling.

Custom manifest fields should use a namespaced prefix (e.g., `x-myorg-`) to avoid collisions with future spec versions.

## What AgentDef Is Not

AgentDef is not a framework. It does not execute agents, manage conversations, or orchestrate multi-agent systems. Use LangGraph, CrewAI, AutoGen, or any other runtime for that.

AgentDef is not a programming language. Agent definitions are structured prose, not executable code. The only code in the repo is tooling (validator, adapters, importers, and the CLI that wraps them) that operates on the definitions — none of it executes an agent.

AgentDef is not a platform. It does not host agents, provide APIs, or manage deployments. It is a file format specification with supporting tools.

## Influences

AgentDef follows the precedent of specifications like OpenAPI (for APIs), JSON Schema (for data validation), and Dockerfile (for container definitions). Each of these succeeded by defining a portable format that multiple tools can produce and consume, without owning the runtime that executes it. OpenAPI does not serve HTTP requests; Dockerfile does not run containers. AgentDef takes the same position for AI agents: the value lives in the shared format and the guarantees around it — validation, round-trips, import reports — not in yet another runtime.
