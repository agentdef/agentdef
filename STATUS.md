# Project Status

> **The single source of truth for "where are we".** Last updated: 2026-07-03.
> If this file disagrees with PUBLISHING.md (a historical planning record),
> this file wins.

## TL;DR

The project is **feature-complete for a v0.2.0 public release and blocked on
nothing technical**. All engineering of Roadmap Phases 1–4 is built, tested
(239 tests), and committed (`bfee5ce` + `b0da12e`). What remains is
**publishing work that only the maintainer can do** (accounts, network), in
the order below.

## What is DONE (built + verified + committed)

| Area | State | Proof |
| ---- | ----- | ----- |
| Name: **AgentDef** | decided + registered | PyPI `agentdef` 0.0.1 placeholder live; GitHub org created ([NAMING.md](NAMING.md)) |
| Rename across repo | done | 0 stale references outside historical records |
| Installable package | done | `pysrc/agentdef/`; wheel passes clean-machine test (install → init → validate → adapt → import → sync) |
| Spec **0.5.0** | done | [spec/SPEC.md](spec/SPEC.md): 7 conformance rules + error codes, RFC-2119 contracts, Appendices D/E |
| Conformance corpus | done | [conformance/](conformance/): 45 cases mapped to rules+codes |
| Adapters / importers | **8 / 9** | claude, openai, cursor, copilot, langgraph, m365copilot, assistants, crewai / + copilotstudio, letta, generic |
| Round-trips | guaranteed | 4 pairs reach byte-identical fixed point (3 real bugs found+fixed by these tests) |
| CLI | done | validate · adapt · import · list · **sync --check** · **init --yes** |
| Test suite | **239 green** | goldens ×16, conformance driver, fixed-point, fuzz (60 non-agent files), MCP round-trip |
| Corpus validation | 505 files, 0 failures | [docs/scorecard.md](docs/scorecard.md), regenerable via `tools/scorecard.py` |
| CI + release automation | written, never run remotely | `.github/workflows/validate.yml` (3 OS × 3 Py, wheel-first), `release.yml` (Trusted Publishing on tag) |
| Community files | done | CODE_OF_CONDUCT, SECURITY, issue templates |
| DX tooling | done | GitHub Action, pre-commit hooks, VS Code extension v0 ([integrations/](integrations/)), mkdocs site (`--strict` green), 5 migration guides, gallery (24 agents) |

Per-task detail with test evidence: [TASKS.md](TASKS.md) (✅/🟡/⬜ marks).

## What is NOT done — your runbook, in order

Everything below needs your accounts, your network, or real humans.
Steps 1–5 are one sitting (~1.5 h). **Follow [RUNBOOK.md](RUNBOOK.md) step by step** (checkboxes + verify checks); RELEASING.md has the underlying command reference.

1. **Publish the repo** — push `agentdef/` as the root of
   `github.com/agentdef/agentdef` (RELEASING.md §0). ~30 min.
2. **Watch the first CI run** — the workflow has never executed remotely;
   if the matrix goes green, enable branch protection requiring it. ~15 min.
3. **Configure PyPI Trusted Publishing** for `release.yml`
   (RELEASING.md §1). ~10 min.
4. **Tag `v0.2.0`** — cut CHANGELOG "Unreleased", push the tag, let CI
   publish; verify `pip install agentdef` on a clean machine
   (RELEASING.md §2). ~20 min.
5. **Register `agentdef` on npm** — still pending from the name
   registration (docs/registration-guide.md step 3). ~10 min.
6. **Harvest corpora → 2,000+ agents** — from any machine with network:
   `python tools/corpus/harvest.py`, then `python tools/scorecard.py`;
   commit the regenerated scorecard. ~1 h, mostly waiting.
7. **Onboarding test (P4.7)** — 3–5 people, stopwatch, docs-only; fix the
   top stumbles. Do this BEFORE announcing.
8. **Launch (Phase 5.1)** — Show HN / r/LocalLLaMA / dev.to, leading with
   the scorecard claim; awesome-list PRs. Then the rest of
   [ROADMAP.md](ROADMAP.md) Phase 5 (upstream PRs, governance, spec 1.0).

**Dashboard: resolved (2026-07-04).** Scan regenerated against `pysrc/`;
dashboard source is published, and `.github/workflows/pages.yml` deploys
docs + dashboard to GitHub Pages (one-time: Settings → Pages → Source =
GitHub Actions, after Step 1). Local scan data (`.understand-anything/`)
stays private; the dashboard ships its own graph copy in `public/`.

Optional, anytime after step 4: deploy the docs site to GitHub Pages
(`mkdocs gh-deploy`), publish the Action and the VS Code extension to their
marketplaces (maintainer sections in each `integrations/*/README.md`).

## Which document is for what

| Document | Role |
| -------- | ---- |
| **STATUS.md** (this) | Current state + ordered next steps. Start here |
| [README.md](README.md) | For users: what AgentDef is, install, usage |
| [ROADMAP.md](ROADMAP.md) | Strategy: 5 phases toward becoming the standard, exit criteria |
| [TASKS.md](TASKS.md) | Engineering detail: every task + its test + status mark |
| [RELEASING.md](RELEASING.md) | Maintainer runbook: exact commands for steps 1–4 above |
| RUNBOOK.md *(private)* | Step-by-step checklist for the 8 steps; not in the public repo |
| [NAMING.md](NAMING.md) | Decision record: why AgentDef |
| PUBLISHING.md *(private)* | **Historical** planning doc; superseded by STATUS + RELEASING; not in the public repo |
| [CHANGELOG.md](CHANGELOG.md) | What changed, release by release |
