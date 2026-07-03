# Import Report — Claude (Claude Code subagent)

Source: `examples/claude-to-copilot-demo/00-source-claude-subagent.md`
Date: 2026-07-01

## Mapped cleanly

- YAML frontmatter ('name'/'description') -> agent.md / manifest.yaml
- frontmatter 'tools' -> manifest.yaml x-claude-tools (no portable AgentDef tools/ equivalent; these are Claude Code capability flags, not API integrations)
- other frontmatter fields (model) -> manifest.yaml x-claude-frontmatter
- 'Role' section -> agent.md Role
- 'Objectives' section -> agent.md Objectives
- 'Communication Style' section -> agent.md Communication Style
- 'Priorities' section -> agent.md Priorities
- 'Avoid' section -> agent.md Avoid
- 'Safety' section -> instructions/safety.md
- 'Review Checklist' section -> instructions/core.md (no specific category matched)
- leading preamble text -> instructions/core.md

## Inferred (not explicit in the source)

- (none)

## Dropped / framework-specific (not portable)

- (none)
