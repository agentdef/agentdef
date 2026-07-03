# AgentDef vs Other Frameworks

AgentDef occupies a different layer than most AI agent frameworks. This document clarifies the distinctions.

## The Key Difference

Most frameworks define **how agents run**. AgentDef defines **what agents are**. These are complementary, not competing.

AgentDef is a definition format. It produces files that describe an agent's identity, instructions, skills, and workflows. It does not execute anything. Frameworks like LangGraph, CrewAI, and AutoGen are runtimes that execute agent logic. AgentDef can feed into any of them via adapters.

## Comparison Table

| Aspect | AgentDef | CrewAI | AutoGen | LangGraph | OpenAI Assistants |
| ------ | --------- | ------ | ------- | --------- | ----------------- |
| **Type** | Definition format | Runtime framework | Runtime framework | Runtime framework | Platform API |
| **Language** | Markdown + YAML | Python | Python | Python | API calls |
| **Executes agents** | No | Yes | Yes | Yes | Yes |
| **Framework-independent** | Yes | No | No | No | No |
| **Human-editable** | Yes (markdown) | Requires Python | Requires Python | Requires Python | Requires API |
| **Multi-framework output** | Yes (adapters) | No | No | No | No |
| **Validation tooling** | Yes | Implicit | Implicit | Implicit | Implicit |
| **Version control friendly** | Yes (plain text) | Partial | Partial | Partial | No |

## AgentDef vs CrewAI

CrewAI defines agents as Python objects with roles, goals, and backstories, organized into crews that execute tasks. It is a runtime framework — you write Python code, and CrewAI orchestrates the execution.

AgentDef defines the same concepts (role, objectives, instructions) in markdown and YAML files. An adapter could generate CrewAI Python code from an AgentDef definition, letting you maintain the agent's identity in a human-readable format while executing it through CrewAI.

Where they diverge: CrewAI handles multi-agent orchestration, task delegation, and execution. AgentDef does not. If you need a runtime, use CrewAI (or another framework). If you want your agent definitions to be portable and framework-independent, use AgentDef as the source of truth.

## AgentDef vs AutoGen

AutoGen focuses on multi-agent conversations and autonomous collaboration between agents. Agents are Python objects that communicate through message passing.

AgentDef does not handle inter-agent communication or conversation management. It defines individual agent behavior. An AutoGen setup could use AgentDef definitions as the source for each agent's system prompt and capabilities, with AutoGen handling the orchestration layer.

## AgentDef vs LangGraph

LangGraph defines agents as directed graphs where nodes are computation steps and edges define the flow. It provides fine-grained control over execution, state management, and branching logic.

AgentDef's LangGraph adapter generates a graph scaffold from workflow steps and skills, but the actual node implementations must be written in Python. AgentDef captures the high-level structure; LangGraph handles the execution details.

They work well together: define the agent's behavior and workflow in AgentDef, generate the LangGraph scaffold, then implement the node logic.

## AgentDef vs Platform-Specific Files

Each AI platform has its own agent definition format:

| Platform | File | What it does |
| -------- | ---- | ------------ |
| Claude | `CLAUDE.md` | System prompt and project instructions |
| OpenAI | `AGENTS.md` | Agent definition and tools |
| Cursor | `cursor-rules.md` | Editor AI behavioral rules |
| Copilot | `copilot-instructions.md` | Repository-level AI instructions |

These files are functionally equivalent — they all tell an AI how to behave. AgentDef unifies them. You maintain one definition and generate whichever platform-specific file you need.

Without AgentDef, teams using multiple AI tools must maintain separate files with overlapping content. Changes must be propagated manually. AgentDef eliminates this duplication.

## AgentDef vs Other "Agent Spec"-Named Projects

Several other projects occupy similar or adjacent naming territory, and it's worth being direct about how this one differs rather than letting readers assume they're the same thing:

- **Oracle's Open Agent Spec** (`pyagentspec`, github.com/oracle/agent-spec) is the closest conceptual neighbor: a framework-agnostic declarative language for defining agents and multi-agent systems, with a reference runtime (WayFlow) and adapters for several agent frameworks. The biggest practical difference is direction of travel: Oracle's tooling is primarily spec-to-runtime (define once, execute via WayFlow or an adapter). This project puts equal weight on the reverse direction — deterministic importers that turn an *existing* Claude, C

## AgentDef vs Same-Named and Near-Named Projects

Claims below were verified against each project's public README/docs on
**2026-07-02** (naming study, see [../NAMING.md](https://github.com/agentdef/agentdef/blob/main/NAMING.md)) and re-checked
in part on **2026-07-03**. These projects are why this project is named
AgentDef and not AgentSpec or Agentfile (both names it nearly carried).

### Letta Agent File (`.af`)

[letta-ai/agent-file](https://github.com/letta-ai/agent-file) defines `.af`, a
serialization format for *stateful* Letta agents: memory blocks, message
history, tool state, and LLM configuration, importable into a Letta server.

Different layer than AgentDef: `.af` captures a **runtime snapshot** of one
agent on one platform; AgentDef captures a **portable behavior definition**
meant to be adapted to many platforms. They are complementary — an importer
for the behavior-relevant subset of `.af` (system prompt, persona, tool
declarations) is on the AgentDef roadmap (TASKS.md P3.7), explicitly reporting
state fields as out of scope rather than pretending to carry them.

### dennishavermans/agentfile

[dennishavermans/agentfile](https://github.com/dennishavermans/agentfile) is
the closest pitch to this project found under any name: "define your rules
once and generate the right instruction file for each agent automatically"
for GitHub Copilot, Claude, and Cursor (it had its own Show HN launch).

How AgentDef differs, concretely: (1) **importers** — AgentDef puts equal
weight on the reverse direction, turning existing CLAUDE.md / Copilot /
M365 / Copilot Studio files into canonical definitions, with a deterministic
classifier validated against 500+ real community agents at 0 failures;
(2) **a spec with conformance rules and JSON Schemas**, not only a generator;
(3) **round-trip guarantees** tested in CI (adapt → import → validate with a
generation marker); (4) broader target set (8 adapters incl. LangGraph
scaffolds and Microsoft/OpenAI/CrewAI formats, 9 importers).

### Microsoft AgentSchema

[microsoft/AgentSchema](https://github.com/microsoft/AgentSchema) (checked
2026-07-03) is a declarative agent object model from Copilot Studio + Foundry,
with emitters for C#, Node, Python, and Go. It is the strongest big-vendor
entry in this space and worth tracking closely.

Differences today: AgentSchema is an object model / schema first (typed,
emitter-driven, Microsoft-ecosystem gravity); AgentDef is markdown-first and
human-editable, with working bidirectional tooling across vendors (Anthropic,
OpenAI, GitHub, Microsoft) and real-corpus validation. If AgentSchema gains
cross-vendor adoption, the right move for AgentDef is an adapter/importer
pair for it — cooperation, not turf war (same policy as Letta above).

### open-gitagent/gitagent-protocol

[open-gitagent/gitagent-protocol](https://github.com/open-gitagent/gitagent-protocol)
is a framework-agnostic, git-native standard for defining AI agents with
identity/rules/policy files, versioned prompts, and runtime export. Similar
goals, earlier stage on the import/round-trip side; the same differentiators
as above apply (importers + corpus validation + conformance tooling).

### The two other "AgentSpec"s

For completeness, since readers will find them when searching: PyPI's
[`agentspec`](https://pypi.org/project/agentspec/) (keyurgolani) generates
instruction guides for AI coding assistants from curated guideline templates
— a template/best-practices generator, not a portable definition format with
importers. And [agents-oss/agentspec](https://agents-oss.github.io/agentspec/)
("Universal Agent Manifest System") centers on a single `agent.yaml` with a
runtime control plane — spec-to-runtime, one direction, YAML-first. Neither
is affiliated with this project.

