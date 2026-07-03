# Naming Study

> **DECISION (2026-07-02): the project is named AgentDef** (package/CLI `agentdef`). Chosen by the project owner from the candidates below — the zero-collision option. The rename is executed as TASKS.md P1.1; register `agentdef` on PyPI/GitHub/npm same-day. The study below is kept as the decision record.

Resolves the blocker in PUBLISHING.md (private planning record) §0 and TASKS.md P1.1. All availability checks performed **2026-07-02** against live PyPI project pages, npm package pages, GitHub org pages, and web search. Availability is a snapshot — re-verify (and register immediately) the moment a decision is made.

Method note: PyPI/npm/GitHub checks were done by fetching the actual project/org URL. Taken names return a full page; free names return 404. Web search was used to detect mindshare collisions that registries can't show.

---

## 1. "AgentSpec" — the name we like, and why it's unrecoverable

Four distinct collisions, three of them in our exact conceptual space:

| Collision | What it is | Severity |
| --------- | ---------- | -------- |
| [`agentspec` on PyPI](https://pypi.org/project/agentspec/) — keyurgolani/AgentSpec | **Active, v2.1.1, "Production/Stable"**, releases through Sep 2025, Trusted Publishing. And it's the same space: "creates instruction guides for AI coding assistants (Copilot, ChatGPT, Claude)" | Fatal for PyPI. PEP 541 name transfer does not apply to actively maintained packages |
| [agents-oss AgentSpec](https://agents-oss.github.io/agentspec/) — "Universal Agent Manifest System" | `agent.yaml` as single source of truth for an agent (model, memory, tools, guardrails). Near-identical pitch to ours | Fatal for search. Two "universal agent spec" projects named AgentSpec already exist |
| [Oracle Open Agent Spec](https://github.com/oracle/agent-spec) + the [CAIS 2026 paper](https://www.caisconf.org/program/2026/papers/open-agent-specification-a-unified-representation-for-ai-agents/) | Framework-agnostic declarative agent language, now with academic publications using it as *the* common representation layer | High. Owns the "agent spec" phrase in research circles |
| [AgentSpec (ICSE'26 paper)](https://arxiv.org/pdf/2503.18666) — runtime enforcement for safe LLM agents | Academic project, same exact name, top SE venue | Medium. Owns the name in another research community |

Conclusion: **AgentSpec is not salvageable.** The PyPI name is held by an active production package in our own niche, and even if it weren't, search for "agentspec" is already split between three other projects, two of which pitch almost exactly what we pitch. Keeping the name means starting every conversation with "no, not that one" — the opposite of what a would-be standard needs.

## 2. "Agentfile" — current name, confirmed weak

Re-verified today; PUBLISHING.md §0's fears all confirmed, with one new fact:

- [`agentfile` on PyPI](https://pypi.org/project/agentfile/): **taken** — a 0.0.0 "WIP" placeholder (850-byte sdist) squatted since Apr 2025 by the Polyaxon maintainer. A [PEP 541](https://peps.python.org/pep-0541/) claim ("name squatting" ground) is plausible but the process routinely takes months and often stalls; not something to gate a launch on.
- [Letta's Agent File (`.af`)](https://github.com/letta-ai/agent-file): established standard, same name, real mindshare.
- [dennishavermans/agentfile](https://github.com/dennishavermans/agentfile): same pitch (one definition → generated per-framework instruction files), same name, already had its Show HN.

Conclusion: publishable only under a qualified package name (`agentfile-spec`, verified free today) while fighting two established "Agentfile"s for search results. Viable, but permanently uphill.

## 3. Candidates verified available

All checked today. "Free" = 404 on the registry page and no meaningful search-result mindshare in the AI-agent space.

| Name | PyPI | npm | GitHub org | Collisions found | Notes |
| ---- | ---- | --- | ---------- | ---------------- | ----- |
| **agent-rosetta** | ✅ free | ✅ free | ✅ free | None with this exact name. Adjacent: [griddynamics/rosetta](https://github.com/griddynamics/rosetta) (instructions management for AI coding agents) and a few other Rosetta-metaphor AI tools | Matches the project's own tagline — "the missing Rosetta stone for defining agents agnostically." Instantly explains the mission |
| **agentbabel** | ✅ free | ✅ free | ✅ free | None. Babel (JS compiler) is a big brand but a different world; no agent-space usage found | Universal-translation metaphor, exactly our function. Short, one word |
| **agentdef** | ✅ free | (not checked) | ✅ free | None found anywhere | Descriptive and safe: "agent definition." Zero story, zero collisions |
| **agentstone** | ✅ free | (not checked) | (not checked) | None found | Rosetta-stone allusion without the word; weaker semantics |
| **agentmanifest** | ✅ free | (not checked) | (not checked) | Generic-term trap: Microsoft AgentSchema defines an `AgentManifest` type; [Ardor-Cerebrum/agents-manifest](https://github.com/Ardor-Cerebrum/agents-manifest) spec exists; AMD GAIA uses "agent manifest" | **Avoid** — the phrase is becoming a common noun owned by bigger players |
| **agentfile-spec** | ✅ free | — | n/a | Inherits both Agentfile collisions | Fallback only: keeps today's name at the cost of permanent disambiguation |

Also relevant context found during the search: [Microsoft AgentSchema](https://microsoft.github.io/AgentSchema/guides/) (declarative, platform-agnostic agent format from a major vendor) and [open-gitagent/gitagent-protocol](https://github.com/open-gitagent/gitagent-protocol) ("framework-agnostic, git-native standard for defining AI agents") are direct competitors regardless of what we're called — both belong in docs/comparisons.md (TASKS.md P1.8).

## 4. Decision matrix

Scored 1–5. Weights reflect what matters for a would-be standard: being findable and unambiguous beats sentiment.

| Criterion (weight) | agent-rosetta | agentbabel | agentdef | agentfile-spec | keep AgentSpec |
| ------------------ | ------------- | ---------- | -------- | -------------- | -------------- |
| Registry availability, all channels (×3) | 5 | 5 | 5 | 4 | 1 |
| Search uniqueness / mindshare headroom (×3) | 4 | 4 | 5 | 2 | 1 |
| Says what it does (×2) | 4 | 4 | 3 | 4 | 4 |
| Memorable / brandable (×2) | 5 | 4 | 2 | 2 | 3 |
| Risk of future collision (×2) | 3 | 4 | 4 | 2 | 1 |
| **Weighted total (/60)** | **51** | **50** | **47** | **34** | **22** |

## 5. Recommendation

1. **First choice: `agent-rosetta`** (display name **AgentRosetta** or simply **Rosetta for Agents**). It is free on PyPI, npm, and as a GitHub org; it carries the project's founding metaphor in the name itself; and "we're the Rosetta stone between CLAUDE.md, AGENTS.md, copilot-instructions and the rest" is a launch pitch that explains itself. Known trade-off: the Rosetta metaphor is popular in AI tooling (griddynamics/rosetta is the closest), so we own "agent-rosetta" but not "rosetta" — acceptable, and far better than owning neither word as with AgentSpec. Minor note: Rosetta Stone Inc. holds trademarks in language education; different class, low risk, but don't imitate their branding.
2. **Close second: `agentbabel`** — pick this if the Rosetta adjacency feels too crowded after your own review. Cleanest availability of the storied names.
3. **Safe harbor: `agentdef`** — if you want zero-collision boredom.
4. **Not recommended:** keeping AgentSpec (unrecoverable, see §1); keeping Agentfile bare (unpublishable on PyPI without a months-long PEP 541 gamble); agentmanifest (generic-term trap).

## 6. If accepted, immediately (same day)

1. Register the PyPI name with a minimal placeholder release (0.0.1, real description, link to repo — not an empty WIP like the one that blocked us).
2. Register the npm name and GitHub org.
3. Grep-sweep rename Agentfile → new name (the AgentSpec→Agentfile rename procedure in PUBLISHING.md §1 is the template; the round-trip marker in `adapters/claude/generate.py` + `importers/claude/import.py` must change in lockstep).
4. Re-run the full suite + adapter smoke tests + a fresh corpus batch (the P1.1 test in TASKS.md).
5. Update PUBLISHING.md §0 to record the decision, and extend docs/comparisons.md with AgentSchema and gitagent-protocol found during this study.

Domain names (.dev/.io) were not checked — do that at registration time; they're nice-to-have, not gating.
