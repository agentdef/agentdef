# AgentDef

## A framework-agnostic specification for defining AI agents

Version: 0.5.0 — July 2026 (Draft)

Spec versions are independent of tooling versions; see Section 13.

---

# 1. Introduction

The current AI agent ecosystem is fragmented.

Different frameworks and platforms define agents using different conventions, file names, architectures and execution models:

- `CLAUDE.md`
- `AGENTS.md`
- `copilot-instructions.md`
- `system.md`
- `persona.md`
- `skills/`
- `workflows/`
- `memory.json`
- `tools.yaml`
- `crew.py`
- `graph.py`
- etc.

Despite the naming differences, most agent systems share the same conceptual building blocks:

- identity
- instructions
- memory
- tools
- workflows
- skills
- runtime configuration
- orchestration
- evaluation

The purpose of AgentDef is to provide a portable, framework-independent structure for defining AI agents.

---

# 2. Goals

AgentDef aims to:

- standardize agent structure
- separate semantics from implementation
- improve portability between frameworks
- simplify non-technical agent creation
- support modular and reusable components
- enable long-term maintainability

---

# 3. Core Principles

## 3.1 Framework Independence

The canonical definition of an agent should not depend on:
- Claude
- OpenAI
- Cursor
- Copilot
- LangGraph
- CrewAI
- AutoGen
- custom runtimes

Framework-specific files should be adapters.

---

## 3.2 Modular Composition

An agent is composed of reusable modules:
- instructions
- skills
- workflows
- memory
- tools
- knowledge

---

## 3.3 Separation of Concerns

Different responsibilities should be isolated:
- identity
- execution
- formatting
- memory
- orchestration
- evaluation

---

## 3.4 Human Readability

The format should:
- remain understandable
- support markdown-first design
- be editable manually
- work with Git/versioning systems

---

# 4. Canonical Directory Structure

```text
agent/
│
├── agent.md
├── manifest.yaml
├── README.md
│
├── instructions/
├── memory/
├── skills/
├── tools/
├── workflows/
├── knowledge/
├── runtime/
├── evals/
├── telemetry/
├── framework/
└── docs/
```

---

# 5. Core Components

## 5.1 `agent.md`

Primary identity definition.

## Responsibilities

Defines:

* role
* objectives
* behavior
* communication style
* priorities
* constraints

## Normative rules (RFC 2119)

* `agent.md` MUST contain a `Role` section, as a level-1 or level-2
  markdown header (`# Role` or `## Role`), matched case-insensitively.
  Deeper header levels do not satisfy this requirement.
* The section names `Role`, `Objectives`, `Style`, `Priorities`,
  `Constraints`, and `Avoid` are canonical: tools that understand these
  concepts MUST map them from/to these names.
* Other sections MAY be present. Validators MUST NOT reject unknown
  sections; converting tools MUST preserve them (typically routed to
  `instructions/core.md` on import) rather than dropping them silently.

## Example

```markdown
# Weekly Twitter Digest Agent

## Role
Editorial AI agent specialized in summarizing Twitter/X content.

## Objectives
- Reduce reading time
- Preserve signal over noise
- Produce shareable summaries

## Style
- concise
- analytical
- professional
```

---

## 5.2 `manifest.yaml`

Composition layer.

## Responsibilities

Declares:

* active modules
* workflows
* skills
* tools
* adapters
* capabilities

## Example

```yaml
name: weekly-twitter-digest

instructions:
  - instructions/core.md

skills:
  - skills/summarization

workflows:
  - workflows/weekly_digest.md
```

---

## 5.3 `instructions/`

Behavioral rules.

## Suggested Files

| File        | Purpose                   |
| ----------- | ------------------------- |
| `core.md`   | Primary instructions      |
| `safety.md` | Guardrails                |
| `style.md`  | Formatting and tone       |
| `domain.md` | Business/domain knowledge |

---

## 5.4 `skills/`

Reusable capabilities.

## Example Structure

```text
skills/
└── summarization/
    ├── SKILL.md
    └── examples/
```

## Responsibilities

Defines:

* purpose
* inputs
* outputs
* heuristics
* examples

---

## 5.5 `workflows/`

Procedural execution logic.

## Responsibilities

Defines:

* ordered execution
* multi-step tasks
* validation checkpoints
* branching logic

---

## 5.6 `memory/`

Persistent or temporary state.

## Normative rules

* `memory/` is OPTIONAL. Validators MUST NOT require it.
* Files in `memory/` describe state *shape and policy*, not live runtime
  state. Tools MUST NOT expect a canonical serialization here (runtime
  state belongs to platforms — cf. Letta's `.af`, which serializes state).
* Adapters SHOULD surface memory policy to frameworks that support it and
  MUST ignore it otherwise.

## Possible Contents

| File              | Purpose                |
| ----------------- | ---------------------- |
| `session.md`      | Current session memory |
| `profile.json`    | User/system profile    |
| `worldstate.yaml` | Mutable global state   |

---

## 5.7 `knowledge/`

Structured domain knowledge.

## Possible Contents

```text
knowledge/
├── glossary.md
├── ontology.yaml
├── faq.md
└── entities/
```

---

## 5.8 `tools/`

External integrations.

## Responsibilities

Defines:

* APIs
* schemas
* permissions
* authentication
* usage rules

## Normative rules

* `tools/` is OPTIONAL. When present, each tool declaration MUST be a
  single YAML or JSON file with at least a `name` (string) key; `kind`
  (string, e.g. `http`, `mcp`, `function`) is RECOMMENDED.
* Authentication material (tokens, secrets) MUST NOT be stored in tool
  files; use references (env var names, secret-manager keys).
* Adapters targeting frameworks without a tool concept MUST ignore
  `tools/` and SHOULD note the omission in their output header comment.

---

## 5.9 `runtime/`

Execution configuration.

## Normative rules

* `runtime/` is OPTIONAL and advisory: it expresses *preferences*
  (model, temperature, context budget, retry policy), not requirements.
* Recognized keys: `model`, `temperature`, `max_context`, `retry_policy`.
  Unknown keys MUST be preserved by tools and MUST NOT fail validation.
* Adapters MUST NOT hard-fail when a target framework cannot honor a
  runtime preference; they SHOULD emit the preference as a comment.

## Example

```yaml
model: gpt-5
temperature: 0.3
max_context: 128k
retry_policy: aggressive
```

---

## 5.10 `evals/`

Evaluation and regression testing.

## Normative rules

* `evals/` is OPTIONAL. When present, each eval SHOULD declare, in
  markdown or YAML: an input (or input reference), the expected
  property of the output, and a scoring method (exact, contains, rubric).
* Validators MUST NOT execute evals; execution belongs to runtimes and CI.

## Responsibilities

Defines:

* benchmarks
* hallucination checks
* expected outputs
* quality metrics

---

## 5.11 `framework/`

Framework adapters.

## Example

```text
framework/
├── claude/
│   └── CLAUDE.md
│
├── openai/
│   └── AGENTS.md
│
├── cursor/
│   └── cursor-rules.md
│
└── langgraph/
    └── graph.py
```

---

# 6. Minimal Agent Definition

The smallest viable AgentDef agent:

```text
agent/
├── agent.md
├── manifest.yaml
└── instructions/
    └── core.md
```

This already defines:

* identity
* objectives
* behavior
* composition

---

# 7. Example: Twitter/X Weekly Digest Agent

## Use Case

Transform weekly batches of saved Twitter/X links into concise professional reports.

---

## Problem

Users accumulate many saved links during the week:

* fragmented discussions
* uneven quality
* limited reading time
* duplicated themes

The goal is not only reading the links, but transforming them into a high-signal briefing.

---

# Example Structure

```text
twitter-digest-agent/
│
├── agent.md
├── manifest.yaml
├── README.md
│
├── instructions/
│   └── core.md
│
├── workflows/
│   └── weekly_digest.md
│
├── skills/
│   └── summarization/
│       └── SKILL.md
│
└── output/
    └── template.md
```

---

# Example `agent.md`

```markdown
# Weekly Twitter Digest Agent

## Role
Editorial AI agent specialized in summarizing Twitter/X discussions.

## Objectives
- Reduce reading time
- Preserve key insights
- Detect recurring themes
- Produce shareable reports

## Style
- concise
- professional
- analytical
```

---

# Example Workflow

```markdown
# Weekly Digest Workflow

1. Collect links
2. Extract content
3. Remove duplicates
4. Group by topic
5. Rank by importance
6. Summarize findings
7. Produce final report
```

---

# Example Skill

```markdown
# Summarization Skill

## Inputs
- tweets
- threads
- screenshots

## Outputs
- summaries
- insights
- topic clusters

## Rules
- prioritize signal
- avoid repetition
- minimize hallucinations
```

---

# 8. Evolution Path

A basic agent may evolve into:

* multi-agent orchestration
* semantic clustering
* memory-aware summarization
* autonomous prioritization
* retrieval augmented generation
* graph-based execution
* telemetry-driven optimization

---

# 9. Benefits of AgentDef

## Portability

Agents become transferable across frameworks.

---

## Modularity

Skills and workflows become reusable assets.

---

## Versionability

Agents become manageable using Git and CI/CD.

---

## Human Accessibility

Non-technical users can understand:

* identity
* goals
* workflows
* skills

without needing implementation knowledge.

---

# 10. Conformance

An agent directory is **AgentDef-compliant** when it satisfies all of the
following numbered rules. Each rule maps to machine-readable validator
error codes (Appendix D); the public conformance corpus (`conformance/`)
exercises every rule with at least two cases.

1. Contains `agent.md` at the root with at least a Role section
   (level-1 or level-2 header, case-insensitive).
   *Codes: `missing-agent-md`, `missing-role`.*
2. Contains `manifest.yaml` at the root: a parseable YAML mapping with at
   least a `name` field and one `instructions` entry.
   *Codes: `missing-manifest`, `invalid-yaml`, `schema-violation`.*
3. Contains `instructions/core.md` with the agent's primary behavioral
   rules. *Code: `missing-core-instructions`.*
4. Every file or directory referenced in `manifest.yaml` exists at the
   declared path. *Code: `missing-reference`.*
5. Every path referenced in `manifest.yaml` resolves to a location inside
   the agent directory — no `../` escapes, no absolute paths.
   *Code: `reference-escapes-root`.*
6. The `manifest.yaml` validates against the AgentDef JSON Schema
   (see `pysrc/agentdef/schemas/manifest.schema.json` in the reference implementation, shipped inside the `agentdef` package). *Code: `schema-violation`.*
7. If `spec_version` is present in `manifest.yaml`, it names a spec
   version the validating tool supports (Section 13).
   *Code: `unsupported-spec-version`.*

Agents MAY include additional directories and files beyond the canonical
structure. Conformance checks MUST ignore unrecognized directories; the
former rule requiring directory names to "match the canonical structure"
(spec 0.1 rule 5) was unenforceable alongside Section 11 extensibility and
is replaced by the containment rule above. Canonical component directories,
when used for their canonical concept, SHOULD use the names of Section 4.

---

# 11. Extensibility

AgentDef is designed to be extended without breaking compatibility.

## Custom Directories

Agents may include directories not defined in the canonical structure. Validators and adapters MUST ignore directories they do not recognize. Custom directories SHOULD be documented in the agent's `README.md`.

## Custom Manifest Fields

The `manifest.yaml` file MAY include additional fields beyond those defined in the schema. Validators MUST NOT reject a manifest for containing unrecognized fields. Custom fields SHOULD use a namespaced prefix (e.g., `x-myorg-`) to avoid future collisions with the spec.

## Framework-Specific Extensions

Framework adapters in `framework/` are inherently extensible. Each subdirectory follows its target framework's conventions. AgentDef does not constrain the contents of `framework/` subdirectories.

---

# 12. Future Extensions

Possible future standardization:

* formal schemas
* ontology specifications
* execution graphs
* evaluation protocols
* capability negotiation
* inter-agent communication standards

---

# 13. Spec Versioning and Compatibility

The specification versions independently from any tool that implements it.

* `manifest.yaml` MAY declare `spec_version` (e.g. `spec_version: "0.5"`).
  Omitting it implies the oldest spec version the consuming tool supports.
* A validator MUST accept every spec version it lists as supported, and
  MUST reject unknown versions with a clear message naming the versions it
  supports (never guess semantics of a future version).
* Within a major spec line, later minor versions only add optional
  constructs: a 0.x-valid agent remains valid under any later 0.y (y > x).
  Breaking changes are documented in the Spec Changelog with migration
  notes.

# Appendix D — Validator Error Codes

| Code | Conformance rule | Meaning |
| ---- | ---------------- | ------- |
| `missing-agent-md` | 1 | `agent.md` absent |
| `missing-role` | 1 | no Role section in `agent.md` |
| `missing-manifest` | 2 | `manifest.yaml` absent |
| `invalid-yaml` | 2 | `manifest.yaml` unparseable or not a mapping |
| `missing-core-instructions` | 3 | `instructions/core.md` absent |
| `missing-reference` | 4 | manifest references a nonexistent path |
| `reference-escapes-root` | 5 | manifest reference resolves outside the agent directory |
| `schema-violation` | 2, 6 | manifest violates the JSON Schema |
| `unsupported-spec-version` | 7 | declared `spec_version` unknown to the validator |
| `generic` | — | any other error |

# Appendix E — Import Reports and Round-Trips (normative)

Every importer run MUST produce an `IMPORT_REPORT.md` in the output agent
directory with three sections listing, item by item: **Mapped** (source
content placed in its canonical AgentDef location), **Inferred** (content
synthesized by heuristics, e.g. a Role recovered from a persona sentence),
and **Dropped** (source content intentionally not carried over). Importers
MUST NOT drop content silently: anything unclassified goes to
`instructions/core.md` and is flagged in the report.

Adapters MUST embed the marker comment
`<!-- Generated from AgentDef. Do not edit manually. -->` in generated
files. Importers encountering the marker MUST take their round-trip path
and state `round-trip detected` in the report. For every
adapter/importer pair, one adapt → import cycle MUST reach a fixed point:
re-running the cycle on its own output produces byte-identical results
(the first cycle MAY normalize documented lossy details; see each
framework's fidelity table in `adapters/<fw>/README.md` and
`importers/<fw>/README.md`).

# Spec Changelog

## 0.5.0 (July 2026)

* `spec_version` manifest field + compatibility policy (Section 13).
* Conformance rules renumbered 1–7 with machine-readable error codes
  (Appendix D); old rule 5 (canonical directory names) replaced by the
  reference-containment rule; `spec_version` check added as rule 7.
* Normative (RFC 2119) contracts for `agent.md` sections, `tools/`,
  `runtime/`, `memory/`, and `evals/`.
* IMPORT_REPORT.md format and round-trip fixed-point guarantee made
  normative (Appendix E).
* Migration from 0.1: no action needed — every 0.1-valid agent remains
  0.5-valid. The containment rule only rejects agents whose manifests
  referenced paths outside their own directory (previously undefined
  behavior).

## 0.1.0 (June 2026)

Initial public draft.

# Conclusion

AgentDef proposes that AI agents should be treated as structured, modular, portable systems rather than framework-specific prompt files.

By separating:

* semantics
* capabilities
* workflows
* memory
* adapters

agents become:

* reusable
* composable
* maintainable
* understandable
* evolvable

---

# Appendix A — Framework Mapping

| AgentDef Concept | Claude      | OpenAI          | Cursor            | Copilot                   | LangGraph           | Microsoft 365 Copilot | Microsoft Copilot Studio |
| ----------------- | ----------- | --------------- | ----------------- | ------------------------- | ------------------- | ---------------------- | ------------------------- |
| Identity          | `CLAUDE.md` | `AGENTS.md`     | `cursor-rules.md` | `copilot-instructions.md` | graph/system prompt | `declarativeAgent.json` (`name`, `description`) | agent doc frontmatter (`name`, `description`) |
| Instructions      | prompts     | system prompts  | rules             | instructions              | nodes               | `instructions`         | `## Instructions` fenced code block |
| Skills            | skills      | tools/functions | rules/macros      | extensions                | nodes               | `capabilities`         | (not modeled — single-purpose agents) |
| Workflows         | chains      | agents          | workflows         | tasks                     | graph edges         | `conversation_starters` / `actions` | `## Conversation Starters` |
| Memory            | context     | memory          | session           | workspace                 | state               | conversation thread (not in manifest) | conversation thread (not in doc) |
| Runtime           | config      | model config    | editor config     | extension config          | runtime graph       | `behavior_overrides`   | `## Knowledge Sources` / `## Deployment Notes` |
| Evaluation        | manual      | evals           | testing           | testing                   | tracing             | manual                 | `tested` frontmatter flag (manual) |

Importers exist for Claude, GitHub Copilot, Microsoft 365 Copilot, and Microsoft Copilot Studio — see [importers/](../importers/) for the reverse direction (framework file → AgentDef).

---

# Appendix B — Conceptual Model

```text
Canonical Agent Definition
            ↓
    AgentDef Structure
            ↓
   Framework Adapters
            ↓
 Claude / OpenAI / Cursor / LangGraph
```

---

# Appendix C — Azure AI Ecosystem Mapping

See [docs/azure-mapping.md](../docs/azure-mapping.md) for the full mapping of AgentDef concepts to Microsoft Copilot Studio, Azure AI Foundry, Semantic Kernel, and Prompt Flow.
