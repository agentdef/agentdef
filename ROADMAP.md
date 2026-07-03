# AgentDef Roadmap

Goal: make AgentDef the default, framework-agnostic way to define AI agents — the format people reach for first, and the format frameworks import and export natively.

> **Naming (2026-07-03):** the rename to **AgentDef** is executed — code, directories, classes, and the `agentdef` CLI all use the final name (decision record: [NAMING.md](docs/NAMING.md)).
Day-to-day execution state lives in [STATUS.md](docs/STATUS.md); this document is the strategy.

This roadmap is ordered by dependency, not by calendar. Each phase has an explicit exit criterion; a phase is done when its criterion is verifiably true, not when its tasks are merely attempted. The companion [TASKS.md](docs/TASKS.md) breaks every phase into concrete development tasks with tests.

---

## Where we are today (updated 2026-07-03, post Phases 1–4 execution)

**Built and verified:**

- **Spec v0.5.0** ([spec/SPEC.md](spec/SPEC.md)): normative RFC-2119 contracts, 7 numbered conformance rules with error codes, spec_version + compatibility policy, normative import reports & round-trip fixed-point guarantee
- **Public conformance corpus** (`conformance/`): 45 cases mapped to rules+codes, third-party testable
- **8 adapters** (Claude, OpenAI AGENTS.md, Cursor, Copilot, LangGraph, M365 declarative agent, OpenAI Assistants, CrewAI) and **9 importers** (those plus Copilot Studio, Letta `.af` subset, generic markdown) in a **self-contained pip package** (clean-machine wheel verified); 4 pairs round-trip to a byte-identical fixed point
- **CLI**: validate / adapt / import / list / **sync** (drift check for CI) / **init**
- **239-test suite** incl. golden files, conformance driver, fixed-point tests (which found and fixed 3 real bugs), fuzz over non-agent inputs; scorecard: 505 real corpus files, 0 failures
- **DX**: GitHub Action, pre-commit hooks, VS Code extension v0, mkdocs site (strict-link green), migration guides, agent gallery
- Naming decision resolved: **AgentDef** ([NAMING.md](docs/NAMING.md)); `agentdef` live on PyPI (0.0.1 placeholder), GitHub org created

**Not done:**

- ~~Rename~~ **done 2026-07-03** (P1.1: dirs/classes/CLI/marker renamed; 63 tests green; round-trip re-verified; 30-file corpus batch 30/30 valid)
- ~~Registration~~ **done for PyPI + GitHub (2026-07-03):** `agentdef` 0.0.1 placeholder live on PyPI (verified via `pip download`), GitHub org + private repo created. npm still pending ([docs/registration-guide.md](docs/registration-guide.md) step 3)
- Not a real PyPI package (CLI resolves sibling dirs at runtime; wheel would be broken)
- No GitHub remote, no CI run in anger, no community files, no releases

---

## Phase 1 — Ship something installable (foundation)

*Nothing else matters until a stranger can `pip install` the tool and it works.*

1. **Execute the rename to AgentDef** and register `agentdef` on PyPI, npm, and GitHub the same day. The name is decided; squatting risk grows with every day between decision and registration.
2. **Packaging refactor.** Move `adapters/`, `importers/`, `validation/` into a real installable package with proper imports; wheel must be self-contained.
3. **Public GitHub repo** with CI (validate + pytest + CLI smoke test on 3 OSes / 3 Python versions), branch protection, community files (CODE_OF_CONDUCT, SECURITY, issue templates).
4. **First tagged release** on GitHub + PyPI. Cut CHANGELOG "Unreleased" into v0.2.0.
5. **Honest comparison doc** extended to cover Letta Agent File, dennishavermans/agentfile, Microsoft AgentSchema, and gitagent-protocol — before, not after, the first public post.

**Exit criterion:** on a clean machine, `pip install agentdef && agentdef import claude SOMEFILE.md && agentdef validate out/ && agentdef adapt copilot out/` works end to end with nothing but the wheel.

## Phase 2 — Spec you can trust (v0.5)

*A standard is only as good as the guarantee it makes. Harden the spec before widening it.*

1. **Spec versioning discipline.** Spec version decoupled from tooling version; `spec_version` field in manifest; documented compatibility policy.
2. **Conformance test suite as a product.** A public, framework-neutral corpus of valid/invalid agents that any third-party implementation can run against — this is what makes "AgentDef-compliant" a checkable claim instead of a vibe.
3. **Tighten underspecified areas** found during real-corpus work: precise semantics for `tools/`, `memory/`, `runtime/`, `evals/` (currently described, not specified); required vs optional fields; canonical section names in `agent.md`.
4. **Round-trip guarantees, stated and tested.** Define lossless vs lossy fields per framework; every adapter/importer pair gets automated round-trip tests; IMPORT_REPORT format becomes part of the spec.
5. **Spec 0.5 release** with a formal changelog of breaking changes and migration notes.

**Exit criterion:** a third party could write an independent validator from SPEC.md + schemas + conformance corpus alone, and agree with ours on every corpus case.

## Phase 3 — Cover the ecosystem (breadth)

*The standard for everyone must speak to everyone's framework. Importers are the wedge: people adopt when their existing agents come along for free.*

1. **New importers** (priority order by corpus availability): Cursor rules, OpenAI `AGENTS.md`, generic `SYSTEM.md`/persona files, CrewAI YAML, LangGraph (best-effort), Letta `.af` (state-aware subset).
2. **New adapters:** CrewAI, AutoGen, OpenAI Assistants API (JSON), M365 Copilot declarative manifest (closing the loop with its importer), Semantic Kernel.
3. **MCP alignment.** Map `tools/` to MCP server declarations — MCP is winning the tool-protocol layer; AgentDef should slot in as the agent-definition layer above it, not compete with it.
4. **Corpus expansion to 2,000+ real agents** across all importers, with per-framework fidelity scorecards published in the repo.
5. **`agentdef sync`:** one command that regenerates every configured framework file from the canonical definition — the daily-driver feature for teams using multiple AI tools.

**Exit criterion:** ≥8 importers and ≥8 adapters; a team using Claude + Copilot + Cursor simultaneously can maintain one definition and generate all three, round-trip tested.

## Phase 4 — Make it effortless (developer experience)

*Formats win by being the path of least resistance, not by being right.*

1. **`agentdef init`** — interactive scaffold; the "npm init" moment.
2. **GitHub Action** (validate + drift check: fail CI if generated framework files are stale vs canonical definition) and **pre-commit hook**.
3. **VS Code extension:** schema-backed completion/diagnostics for `manifest.yaml`, section linting for `agent.md`, one-click adapt/import.
4. **Docs site** with tutorials, per-framework migration guides ("Move your CLAUDE.md to AgentDef in 5 minutes"), and the interactive architecture dashboard.
5. **Agent gallery/registry (static first):** browsable index of imported community agents as ready-to-use AgentDef packages — the 500+ already-validated imports are the seed content.

**Exit criterion:** time from "never heard of it" to first validated agent under 10 minutes, measured with real users.

## Phase 5 — Become infrastructure (adoption & governance)

*A format becomes the standard when other people's software emits and consumes it without asking us.*

1. **Launch properly:** Show HN / r/LocalLLaMA / dev.to, leading with the verifiable claim — "we imported 2,000+ real agents from N communities; here's the scorecard" — plus awesome-list PRs.
2. **Framework-native support campaign:** PRs and proposals to frameworks/tools to read or emit AgentDef directly (a `--from-agentdef` flag in a scaffold tool beats ten blog posts).
3. **Neutral governance:** move spec decisions to a lightweight RFC process with public review; multiple maintainers; explicit non-affiliation with any model vendor — nobody adopts a "universal" standard owned by one player.
4. **Spec 1.0:** frozen core, extension mechanism for the rest, conformance levels (minimal / standard / full), and a compatibility promise.
5. **Interop bridges, not turf wars:** documented, tested conversions to/from Letta `.af` and Oracle Open Agent Spec — being the format that cooperates is itself a differentiator.

**Exit criterion:** at least three independent projects (not ours) emit or consume AgentDef; spec 1.0 published under shared governance; "how do I define an agent portably?" answers on search/SO/LLMs name AgentDef.

---

## What we deliberately do NOT do

- **No runtime.** AgentDef defines agents; it never executes them. The moment it has a runtime it competes with every framework instead of complementing all of them.
- **No lock-in features.** Anything that only works with one vendor's models goes in `framework/`, never in the core spec.
- **No LLM-dependent tooling in the core path.** Importers stay deterministic — reproducibility is what makes 0-failure corpus claims possible.

## Standing risks

| Risk | Mitigation |
| ---- | ---------- |
| `agentdef` names get squatted before we register them | Register PyPI/npm/GitHub same-day with the P1.1 rename — availability verified 2026-07-02, treat as perishable |
| Confusion with same-space neighbors (AgentSpec×3, Agentfile×2, AgentSchema) | [NAMING.md](docs/NAMING.md) chose a collision-free name; comparisons doc addresses neighbors head-on (Phase 1 task 5) |
| A big vendor ships a competing "standard" | Speed to Phase 3 breadth + neutrality stance + interop bridges (Phase 5) |
| Spec churn burns early adopters | Conformance corpus + migration notes from Phase 2 onward; freeze at 1.0 |
| Single-maintainer bus factor | Governance work starts in Phase 5 but contributor docs are already in place; keep PR-sized changes and honest history |
