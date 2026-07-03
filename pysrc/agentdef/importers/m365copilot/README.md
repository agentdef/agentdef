# Microsoft 365 Copilot Importer

Imports a Microsoft 365 Copilot **declarative agent manifest**
(`declarativeAgent.json`, schema v1.0–v1.7) into a conformant AgentDef
directory.

The forward adapter lives at `adapters/m365copilot/` (added in Phase 3): `agentdef adapt m365copilot` generates a `declarativeAgent.json`, closing the round-trip loop with this importer.
## Usage

```bash
python import.py declarativeAgent.json --output ../../my-agent
```

## Mapping

| M365 Copilot manifest field | AgentDef |
| ----------------------------- | --------- |
| `name` | `agent.md` title / `manifest.yaml` name |
| `description` | `agent.md` intro / `manifest.yaml` description |
| `instructions` | `instructions/core.md` (full text); a persona sentence within it (or `description` as fallback) becomes `agent.md` Role |
| `capabilities[]` | `tools/<capability-name>.md` (one per capability object, full JSON preserved) |
| `actions[]` | `tools/action-<id>.md` (plugin reference or inlined manifest) |
| `conversation_starters[]` | `knowledge/conversation-starters.md` |
| `editorial_answers.answers[]` | `knowledge/editorial-answers.md` |
| `disclaimer`, `behavior_overrides.special_instructions`, `behavior_overrides.suggestions` | `instructions/safety.md` |
| `worker_agents`, `user_overrides`, `sensitivity_label`, `behavior_overrides` (raw) | preserved verbatim under `x-m365-*` keys in `runtime/config.yaml` — no portable AgentDef equivalent, so they're kept rather than dropped, and flagged in `IMPORT_REPORT.md` |

Manifest schema versions 1.0–1.7 are read leniently (missing fields are
simply skipped), so any version in that range works as input.
