# Frequently Asked Questions

## General

### What is AgentDef?

AgentDef is an open specification for defining AI agents in a portable, framework-independent, human-readable format. It defines a canonical directory structure that separates what an agent IS from how it runs on any specific platform.

### Who is AgentDef for?

Anyone who defines AI agent behavior: developers, product managers, AI engineers, prompt engineers, technical writers. If you configure AI assistants and want your definitions to work across multiple tools, AgentDef is for you.

### Is AgentDef a framework?

No. AgentDef is a file format specification, not a runtime. It defines how to describe an agent, not how to execute one. You use AgentDef alongside frameworks like LangGraph, CrewAI, or platform-specific tools like Claude or OpenAI.

### What license is AgentDef under?

Apache 2.0. You can use it freely in commercial and open-source projects.

## Using AgentDef

### What is the smallest valid agent?

Three files:

```
my-agent/
├── agent.md            # Role and identity
├── manifest.yaml       # name + instructions list
└── instructions/
    └── core.md         # Behavioral rules
```

### Do I need to use all the directories in the spec?

No. Only `agent.md`, `manifest.yaml`, and `instructions/core.md` are required. Add `skills/`, `workflows/`, `memory/`, `knowledge/`, `tools/`, and other directories only when your agent needs them.

### Can I add custom directories?

Yes. Validators and adapters will ignore directories they don't recognize. Document custom directories in your agent's `README.md`. If you add custom fields to `manifest.yaml`, use a namespaced prefix like `x-myorg-` to avoid future collisions.

### How do I validate my agent?

```bash
agentdef validate ./my-agent/
```

The validator checks that required files exist, `manifest.yaml` is valid YAML conforming to the schema, all file references resolve, and `agent.md` has a Role section.

### How do I generate framework-specific files?

Use an adapter:

```bash
agentdef adapt claude ./my-agent/       # → CLAUDE.md
agentdef adapt openai ./my-agent/       # → AGENTS.md
agentdef adapt cursor ./my-agent/       # → cursor-rules.md
agentdef adapt copilot ./my-agent/      # → copilot-instructions.md
agentdef adapt langgraph ./my-agent/    # → graph.py
```

### Can I use AgentDef with a framework that doesn't have an adapter?

Yes. Writing an adapter is straightforward — read the AgentDef files, restructure the content into the target format. See `adapters/_common.py` for shared loading logic and any existing adapter as a template. Contributions of new adapters are welcome.

### I already have agents defined in another framework. Do I have to rewrite them by hand?

No — use an importer to convert an existing framework file into an AgentDef directory automatically:

```bash
agentdef import claude CLAUDE.md --output ./my-agent
```

Importers exist for Claude (`CLAUDE.md` and Claude Code subagent files), GitHub Copilot (`copilot-instructions.md` and custom `*.agent.md` agents), Microsoft 365 Copilot (`declarativeAgent.json`), and Microsoft Copilot Studio (agent docs). Each run produces an `IMPORT_REPORT.md` listing what mapped cleanly, what was inferred, and what was dropped as framework-specific — imports are best-effort, not lossless. See [importers/](../importers/) for details.

### Is there a single command-line tool, or do I have to call each script separately?

Use the `agentdef` CLI (`pip install agentdef`, or `pip install -e .` from a checkout): `agentdef validate`, `agentdef adapt <framework>`, `agentdef import <framework>`, `agentdef sync`, `agentdef init`, and `agentdef list` to see every supported framework.

## Design

### Why markdown instead of YAML or JSON for agent definitions?

Markdown is human-readable, diffs cleanly in Git, and can be edited by people who aren't programmers. The people who define agent behavior — product managers, domain experts — should be able to read and edit definitions directly. YAML is used only for the manifest (structured metadata), not for prose content.

### Why a directory structure instead of a single file?

