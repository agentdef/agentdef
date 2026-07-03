# Microsoft Copilot Studio Importer

Imports a Microsoft Copilot Studio **agent definition** (as published in
[github/awesome-copilot-studio-agents](https://github.com/github/awesome-copilot-studio-agents),
a single `<name>.md` file per agent) into a conformant AgentDef directory.

There is currently no forward adapter for Copilot Studio in `adapters/` —
this importer is one-directional (Copilot Studio doc → AgentDef) for now.

## Source shape

- An *optional* YAML frontmatter block: `name`, `description`, `domain`,
  `vertical`, `audience`, `knowledge_sources`, `language`, `char_count`,
  `rai_reviewed`, `tested`, `version`, `last_updated`. Some source files
  (roughly 1 in 15 in the real corpus) omit this entirely and open directly
  on the H1 title — the importer falls back to the H1 title and the
  `> **Description:** ...` blockquote in that case.
- A body with a consistent H1-wrapped skeleton: `## Description`,
  `## Conversation Starters`, `## Instructions` (a fenced code block meant
  to be pasted verbatim into the Copilot Studio "Instructions" field — this
  is the actual system prompt, and is itself a nested markdown document
  with its own `## ROLE` / `## LANGUAGE RULES` / etc. structure),
  `## Knowledge Sources`, `## Deployment Notes`, `## Changelog`.

## Usage

```bash
python import.py risk-register-manager.md --output ../../my-agent
```

## Mapping

| Copilot Studio field | AgentDef |
| --- | --- |
| frontmatter `name` / `description` (or H1 title / description blockquote if no frontmatter) | `agent.md` title / `manifest.yaml` name+description |
| `## Instructions` fenced code block | classified via the shared generic markdown importer (same Role/Objectives/Style/Priorities/Avoid/Safety/Skills/Workflows/Tools classifier used by `importers/claude` and `importers/copilot`) — this is where Role actually comes from |
| `## Description` section (if materially different from the frontmatter description) | `instructions/core.md` |
| `## Conversation Starters` | `knowledge/conversation-starters.md` |
| `## Knowledge Sources` section | `manifest.yaml` → `x-copilotstudio-knowledge-sources-detail` |
| `## Deployment Notes` | `instructions/deployment-notes.md` |
| `## Changelog` | dropped (framework/versioning metadata, not portable) — recorded in `IMPORT_REPORT.md` |
| frontmatter `domain`, `vertical`, `audience`, `language`, `rai_reviewed`, `tested`, `version`, `last_updated`, `char_count`, `knowledge_sources` | preserved verbatim under `x-copilotstudio-*` keys in `manifest.yaml` — no portable AgentDef equivalent, so they're kept rather than dropped |

Validated against 94 real agents from github/awesome-copilot-studio-agents
during development (0 failures).
