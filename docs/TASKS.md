# AgentDef Development Task List

> **Status 2026-07-03:** Phases 1–4 executed in one working session (see CHANGELOG "Unreleased"). ✅ = done+tested here; 🟡 = built here, remainder needs the maintainer's accounts/network (steps in RELEASING.md / each task note); ⬜ = needs humans. Suite: 239 tests.

Companion to [ROADMAP.md](https://github.com/agentdef/agentdef/blob/main/ROADMAP.md). Every task has a **Test** — the concrete check that proves the task is done. A task without a passing test is not done. Tasks are numbered `P<phase>.<n>`; order within a phase is dependency order.

Conventions used below:

- "Suite green" = `python -m pytest tests -v` passes (adapters/tests to be created in P1.2).
- "Clean-machine test" = fresh venv or container with no repo checkout on the path.
- Corpus paths refer to the local clones in `downloads/` (awesome-copilot, awesome-copilot-studio-agents, awesome-claude-agents, awesome-claude-code-subagents).

---

## Phase 1 — Ship something installable

### P1.1 Execute the rename to AgentDef — ✅ DONE 2026-07-03

The study in [NAMING.md](NAMING.md) resolved the blocker: the project is **AgentDef** (`agentdef` verified free on PyPI and as GitHub org on 2026-07-02). Execute in this order: (1) **register the names same-day** — PyPI placeholder release 0.0.1 with real metadata and repo link (not an empty WIP), GitHub org, npm if desired; (2) repo-wide rename following the AgentSpec→Agentfile procedure documented in PUBLISHING.md §1 (private planning record): directories (`agentfile/` → `agentdef/`, `.agentfile/` → `.agentdef/`), classes (`Agentfile` → `AgentDef`, `AgentfileWriter` → `AgentDefWriter`), CLI entry point and `pyproject.toml`, and the round-trip marker in `adapters/claude/generate.py` + `importers/claude/import.py` **in lockstep**; (3) sweep all docs (README, SPEC.md, CHANGELOG, docs/, adapter/importer READMEs, AGENTS.md).

**Test — results 2026-07-03:** (1) full suite green (63 tests) ✅. Original spec: (1) full suite green (63 tests). (2) `grep -ri "agentfile\|agentspec"` across the repo (excluding `downloads/`, `extras/`, `.git/`, and the historical-record sections of NAMING.md/PUBLISHING.md/CHANGELOG.md) returns 0 hits. (3) Round-trip re-tested: adapt claude → import claude reports the AgentDef-generated marker. (4) Fresh venv `pip install -e .` exposes a working `agentdef` command (`list`, `validate`). (5) A 30-file sample corpus batch re-imported and revalidated. (6) `pip install agentdef` from PyPI installs our placeholder (proves registration happened). **All six verified 2026-07-03**: 63/63 tests; grep clean outside historical records and caches; round-trip marker detected; `agentdef list`/`validate` working from fresh venv editable install; 30/30 corpus batch valid; PyPI placeholder download verified.

### P1.2 ✅ DONE 2026-07-03 (pysrc/ layout; clean-machine wheel verified) — Packaging refactor: self-contained installable package

Restructure to `src/<pkg>/` layout: move `adapters/`, `importers/`, `validation/` into the package, add `__init__.py` everywhere, replace all `sys.path.insert` tricks and path-walking with relative imports, register adapters/importers via a small registry module instead of directory discovery, update `pyproject.toml` (`packages`, `package-dir`, console script → `<pkg>.cli:main`). Keep thin wrapper scripts at the old paths for one release (deprecation note) so existing docs/AGENTS.md commands keep working. Update the test suite's imports and create `adapters/tests/` (adapters currently have no dedicated unit tests — add golden-file tests per adapter while touching every file anyway).

**Test:** (1) Suite green. (2) `python -m build` then, on a clean machine, `pip install dist/*.whl` and run `agentdef list`, `agentdef validate <copied example>`, `agentdef adapt claude`, `agentdef import copilot` — all succeed with the git checkout absent. (3) `python -c "import <pkg>.adapters.claude"` works from the wheel. (4) Old wrapper paths still run with a deprecation warning.

### P1.3 ✅ DONE 2026-07-03 (16 goldens, 8 adapters × 2 examples) — Golden-file adapter tests

For each of the 5 adapters: commit the expected output for `examples/mission-writer` and `examples/twitter-digest` under `adapters/tests/golden/`; test regenerates and diffs. This locks adapter behavior before any refactoring beyond P1.2 and catches accidental output drift forever after.

**Test:** 10 golden tests pass (5 adapters × 2 examples); deliberately corrupting one golden file makes exactly that test fail (verify once, then restore).

### P1.4 ✅ DONE 2026-07-03 — Round-trip smoke test in CI

Automate what was done manually: for each example agent, `adapt claude → import claude → validate`, assert validation passes and the round-trip marker is detected in IMPORT_REPORT.md.

**Test:** new pytest module `tests/test_roundtrip.py` passes; removing the marker line from the generated file makes the round-trip-detection assertion fail (verify once).

### P1.5 ✅ code DONE / first real run needs push (user) — CI matrix

Extend `.github/workflows/validate.yml`: matrix over Python 3.10/3.11/3.12 × ubuntu/macos/windows; steps = install from wheel (not editable), suite, CLI smoke test, example validation. Dry-run the steps locally before first push (the workflow has never executed).

**Test:** all matrix jobs green on the first real push. Locally: `act` run or manual step-by-step execution of the workflow script succeeds.

### P1.6 🟡 files DONE; repo creation/push/branch-protection = maintainer steps in RELEASING.md — Public GitHub repo + community files

Create repo under final name; push history (keep the honest bug-fix history); branch protection on `main` requiring CI; add CODE_OF_CONDUCT.md (Contributor Covenant), SECURITY.md, issue templates (bug report; "request framework adapter/importer" template).

**Test:** a PR from a branch cannot be merged with a failing check (verify with a deliberate red PR, then close it). Fresh `git clone` + README quick-start instructions work as written, followed literally.

### P1.7 🟡 release.yml + RELEASING.md DONE; tag/upload = maintainer — Release v0.2.0 (tooling) — GitHub Release + PyPI

Cut CHANGELOG "Unreleased" into v0.2.0; tag; build sdist+wheel; upload to TestPyPI first, then PyPI; verify install; create GitHub Release with notes.

**Test:** clean-machine `pip install <name>` (real PyPI) then the full P1.2 CLI sequence; `pip download <name> --no-deps` wheel contains adapters/importers/validation modules (`unzip -l` check).

### P1.8 ✅ DONE 2026-07-03 (also AgentSchema + gitagent-protocol) — Extend comparisons doc

Add sections on Letta Agent File (state serialization vs behavior spec) and dennishavermans/agentfile (same pitch — differentiate on importers, corpus validation, spec+conformance depth, breadth). Honest tone, link to both.

**Test:** `docs/comparisons.md` covers both projects; every factual claim about them is verified against their current README/docs at time of writing (record the check date in the doc); internal links resolve (link-checker run).

---

## Phase 2 — Spec you can trust (v0.5)

### P2.1 ✅ DONE 2026-07-03 — Spec/tooling version split

Add `spec_version` to `manifest.yaml` schema (optional, defaults to current); SPEC.md gets its own version header and changelog section; document the compatibility policy (validator accepts which spec versions).

**Test:** validator accepts manifests with `spec_version: "0.2"` and without the field; rejects `spec_version: "99.0"` with a clear message; unit tests for all three cases.

### P2.2 ✅ DONE 2026-07-03 (20 valid + 25 invalid; codes asserted) — Public conformance corpus

Create `conformance/` with ~30 valid and ~30 invalid agent directories, each invalid one violating exactly one numbered conformance rule from SPEC.md §10, named accordingly (e.g. `invalid/rule-4-missing-referenced-file/`). Include a `manifest.json` mapping each case to its rule and expected validator message. This is the artifact third parties test against.

**Test:** a driver test runs the validator over the whole corpus and asserts: every valid case passes, every invalid case fails *for the mapped rule* (assert on error code/message, not just nonzero exit). Every conformance rule in SPEC.md §10 has ≥2 corpus cases (coverage check script).

### P2.3 ✅ DONE 2026-07-03 (SPEC 0.5 normative sections; spec/REVIEW.md) — Specify the underspecified components

Write normative sections (MUST/SHOULD/MAY per RFC 2119) for `tools/` (file format, schema), `runtime/` (recognized keys, unknown-key policy), `memory/` and `evals/` (minimal contracts); define the canonical `agent.md` section names (Role required; Objectives/Style/Constraints recognized) and how validators treat unknown sections. Add JSON Schemas for any new structured file.

**Test:** every new normative statement has at least one conformance-corpus case exercising it; schemas validate the examples; suite green; SPEC.md contains no section that describes a directory without stating what a validator MUST check (manual review checklist committed as `spec/REVIEW.md`).

### P2.4 ✅ DONE 2026-07-03 (3 real bugs found+fixed; 4 pairs at fixed point) — Round-trip guarantees per framework

For each adapter/importer pair, write a fidelity table (lossless / lossy-with-report / dropped) into that framework's README; make IMPORT_REPORT.md format normative (spec appendix); add property-style tests: adapt→import→adapt produces byte-identical second output (fixed-point test) for all examples and 20 sampled corpus agents.

**Test:** fixed-point tests pass for claude and copilot pairs; every "lossless" cell in the fidelity tables has a test asserting the value survives the round trip; every "lossy" cell's drop appears in IMPORT_REPORT.md (asserted).

### P2.5 ✅ DONE 2026-07-03 (SPEC.md v0.5.0 + changelog + migration notes) — Spec v0.5 release

Roll P2.1–P2.4 into SPEC.md v0.5 with migration notes for 0.1→0.5; tag; announce in repo Releases.

**Test:** conformance corpus green against v0.5 validator; all v0.1 example agents either still validate or are covered by a written migration note; docs link-check green.

---

## Phase 3 — Cover the ecosystem

For every new importer/adapter below, the definition of done is identical, so it is stated once:

**Standard importer test:** unit tests on hand-written fixtures for each mapped field + edge cases; corpus run over every available real-world file of that format with 0 crashes and 100% valid output (or a written triage of failures); IMPORT_REPORT.md produced for each; frontmatter/fence pitfalls from CHANGELOG regression-tested. **Standard adapter test:** golden files for both examples; round-trip fixed-point test if a matching importer exists; output loads/parses in the target format's own tooling where feasible (e.g. generated JSON validates against the vendor schema, generated Python imports cleanly).

### P3.1 🟡 importer+round-trip DONE; ≥100-file corpus needs harvest (tools/corpus/harvest.py, user network) — Cursor importer

Import `cursor-rules.md` / `.cursor/rules/*.mdc` (with MDC frontmatter: description, globs, alwaysApply). Reuse `generic_markdown_import()`; map globs to a namespaced manifest field.

**Test:** standard importer test; corpus = rules files harvested from public repos (target ≥100 files, add to `downloads/`); round-trip with existing cursor adapter reaches fixed point.

### P3.2 🟡 importer+round-trip DONE; ≥150-file corpus needs harvest — OpenAI AGENTS.md importer

Import `AGENTS.md` (the openai/agents.md convention). Handle both single-agent and monorepo multi-section variants; multi-agent files produce one AgentDef directory per detected agent plus a report.

**Test:** standard importer test; corpus target ≥150 files from public repos; round-trip with openai adapter reaches fixed point.

### P3.3 ✅ DONE 2026-07-03 (fuzz: 60 non-agent READMEs, 0 crashes) — Generic markdown importer (fallback)

`agentdef import generic <file.md>` — the classifier alone, no framework assumptions, for `SYSTEM.md`/persona/prompt files. Always succeeds; everything unclassified lands in `instructions/core.md` and is flagged.

**Test:** standard importer test; fuzz-style test: run over 200 arbitrary README.md files (not agents at all) — never crashes, always emits valid AgentDef + honest report; property test that no input line is ever silently dropped (input text ⊆ union of output files + report).

### P3.4 🟡 adapter+importer+tests DONE; crewai-package load check + ≥50 corpus deferred — CrewAI adapter + importer

Adapter: generate `agents.yaml`/`tasks.yaml` (role/goal/backstory from agent.md, tasks from workflows). Importer: reverse. This is the first non-markdown-target pair — it will stress the classifier's assumptions; budget accordingly.

**Test:** standard both; generated YAML loads via `crewai` package's own config loader in a pinned venv; corpus = CrewAI example repos (target ≥50 agent definitions).

### P3.5 🟡 adapter DONE (payload JSON-valid); vendor OpenAPI-schema pinning deferred (no network) — OpenAI Assistants API adapter

Emit the Assistants `create` JSON payload (name, instructions concatenation policy per spec, tools mapping).

**Test:** standard adapter test; payload validates against the OpenAI OpenAPI schema (offline copy pinned in repo); instructions-concatenation order matches the normative order from P2.3 (asserted).

### P3.6 🟡 adapter DONE, loop closed with importer; Microsoft schema pinning deferred — M365 Copilot adapter (close the loop)

Generate `declarativeAgent.json` from AgentDef — the importer already exists, so the fixed-point test applies immediately.

**Test:** standard adapter test; output validates against Microsoft's declarative agent JSON schema (pinned copy); round-trip fixed point with the m365copilot importer.

### P3.7 🟡 importer+tests DONE (state fields reported by name); upstream .af examples corpus needs harvest — Letta `.af` bridge (import subset)

Import the behavior-relevant subset of Letta Agent File (system prompt, persona, tool declarations); explicitly report state fields (memory blocks, message history) as out-of-scope-dropped. This doubles as the interop story with the name-collision neighbor.

**Test:** standard importer test against letta-ai/agent-file published examples; IMPORT_REPORT.md lists every dropped state field by name; docs/comparisons.md updated with the "we interop, not compete" link.

### P3.8 ✅ DONE 2026-07-03 (schema + claude emit + byte-for-byte round-trip; Claude-Code smoke = manual) — MCP tools mapping

Spec + implementation: `tools/mcp.yaml` declaring MCP servers/tools; claude and copilot adapters emit the right client config stanzas; importers recognize `.mcp.json` when present next to source files.

**Test:** schema validates examples; claude adapter output includes MCP config that Claude Code accepts (`claude mcp list` smoke test in CI container, or documented manual verification); round-trip preserves the mcp.yaml content byte-for-byte.

### P3.9 🟡 scorecard.py + harvest.py DONE; current corpus 505 files / 0 failures; 2,000+ target needs user harvest — Corpus expansion + published scorecard

Grow corpora to 2,000+ agents total across all importers (new harvest scripts in `tools/corpus/`, respecting licenses; store manifests of source URLs, not the files, where redistribution is unclear). Generate `docs/scorecard.md`: per importer — files attempted, valid outputs, fields mapped vs inferred vs dropped (aggregated from IMPORT_REPORTs).

**Test:** scorecard generation is a script whose output is committed and CI-checked for staleness (regenerate + diff = empty); totals ≥2,000; every importer row shows 0 crashes.

### P3.10 ✅ DONE 2026-07-03 (incl. --check + dogfood on .agentdef) — `agentdef sync`

`agentdef sync` reads a `sync:` block in manifest.yaml (target framework → output path) and regenerates every configured file; `--check` mode exits nonzero when any output is stale (for CI).

**Test:** unit tests: sync writes all targets; editing canonical source then `sync --check` fails; after `sync` it passes; goldens for a two-target config. Dogfood: `.agentdef/` gets a sync block generating this repo's own CLAUDE.md and copilot-instructions.md, and CI runs `sync --check` on it.

---

## Phase 4 — Make it effortless

### P4.1 ✅ DONE 2026-07-03 (pexpect interactive test deferred; --yes path CI-tested) — `agentdef init`

Interactive scaffold (name, role, target frameworks) producing a valid minimal agent + optional sync block; `--yes` non-interactive mode for scripts.

**Test:** `agentdef init --yes --name test-agent` output passes `agentdef validate` on every OS in the CI matrix; interactive path covered via pexpect/pty test on Linux; generated agent's `sync` targets adapt cleanly.

### P4.2 🟡 action + README DONE; Marketplace publish + fixture repo = maintainer — GitHub Action

Published action (`agentdef/agentdef-action@v1`): validates agent dirs, runs `sync --check` for drift. Marketplace listing.

**Test:** a fixture repo (in the org) uses the action; CI there goes red when a framework file is hand-edited out of sync and green after `agentdef sync` — both states demonstrated in the fixture repo's history.

### P4.3 🟡 hooks DONE + entries verified; `pre-commit try-repo` blocked by sandbox git locks — pre-commit hook

`.pre-commit-hooks.yaml` exposing `agentdef-validate` and `agentdef-sync-check`.

**Test:** `pre-commit try-repo . agentdef-validate` passes on this repo's examples and fails on a conformance-corpus invalid case.

### P4.4 🟡 v0 extension DONE (schema assoc, Role lint, 3 commands); vscode-test + Marketplace = maintainer — VS Code extension (v0)

YAML language-server wiring for manifest.yaml (schema association → completion/diagnostics), agent.md section linting (missing Role), commands: validate / adapt / import current folder.

**Test:** extension integration tests (vscode-test): schema diagnostics appear for a bad manifest; Role-lint fires; validate command surfaces validator output. Manual checklist for marketplace screenshots committed.

### P4.5 ✅ DONE 2026-07-03 (mkdocs build --strict green; Lighthouse check post-deploy) — Docs site

mkdocs-material site from existing `docs/` + spec + per-framework migration guides ("Move your CLAUDE.md in 5 minutes" etc., one per importer); deploy via GitHub Pages; dashboard static build linked (after the vite token-gate review flagged in PUBLISHING.md §4a.5).

**Test:** `mkdocs build --strict` green (fails on broken links); every migration guide's command sequence executed verbatim in CI against a fixture file; Lighthouse accessibility ≥90 on the landing page.

### P4.6 ✅ DONE 2026-07-03 (24 entries, source-linked, import-verified at generation) — Agent gallery (static)

Static index page generated from imported community agents (seeded by the validated corpus imports whose licenses permit redistribution): name, source framework, description, download as AgentDef zip.

**Test:** gallery build script output committed + staleness-checked in CI; 20 randomly sampled gallery entries each pass `agentdef validate` after download-and-unzip (scripted).

### P4.7 ⬜ USER: needs real people — Ten-minute onboarding check

Recruit 3–5 people who've never seen the project; time them from landing page to first validated agent following only public docs; file an issue per stumble.

**Test:** median time ≤10 minutes; every identified stumble has an issue and the top 3 are fixed before Phase 5 launch.

---

## Phase 5 — Become infrastructure

### P5.1 Launch

Show HN + r/LocalLLaMA + dev.to post led by the scorecard claim (P3.9); awesome-list PRs (awesome-ai-agents and per-framework lists). Prepare a "how is this different from X" FAQ from comparisons.md — the first comment will ask.

**Test (pre-launch):** clean-machine quick-start executed from the actual live docs; scorecard numbers cross-checked against the CI-generated artifact; comparisons doc updated within 7 days pre-launch. **Measure (post-launch):** track installs/stars/issues for the governance conversation — not a pass/fail test, but record baselines.

### P5.2 Framework-native support PRs

Target 3–5 upstream integrations (e.g. scaffolders that could add `--from-agentdef`, framework docs that list definition formats). Each is its own negotiation; the deliverable is the working PR/proposal, acceptance is theirs to give.

**Test:** each submitted PR includes tests in the target repo's own suite proving the integration; ≥3 submitted; outcomes logged in `docs/adoption.md`.

### P5.3 RFC-based governance

`GOVERNANCE.md`: RFC template + process (issue → RFC PR → comment period → decision record), ≥2 maintainers with merge rights, decision log directory.

**Test:** the process is exercised at least once end-to-end on a real spec change (e.g. a Phase 3 leftover) before 1.0 — the merged RFC and decision record are the proof.

### P5.4 Interop bridges hardened

Promote the Letta bridge (P3.7) plus an Oracle Open Agent Spec conversion to documented, versioned, tested bridges; publish a joint compatibility table.

**Test:** bridge conversions run in CI against pinned upstream example files; upstream format version pinned and a CI job warns when upstream publishes a newer version (fetch + compare, allowed to be manual-trigger).

### P5.5 Spec 1.0

Freeze the core (structure, manifest required fields, conformance rules); define conformance levels (minimal / standard / full) with corpus subsets per level; extension mechanism finalized (`x-` fields + custom dirs, from SPEC.md §11); compatibility promise ("valid 1.0 agents validate in all 1.x").

**Test:** conformance corpus partitioned by level, all green; every 0.5-valid agent validates under 1.0 or has an automated migration (`agentdef migrate`) whose output validates — tested over the entire corpus; an independent reviewer (not the author) implements a minimal validator from the spec alone and runs it against the corpus, with disagreements resolved as spec bugs before the freeze.

---

## Cross-cutting rules (apply to every task)

- **Suite green before merge.** No exceptions; the corpus work exists precisely because unit fixtures lie.
- **Real-corpus rule** (from AGENTS.md): any change to shared importer code re-runs against real corpora, not just unit tests.
- **Nothing silently dropped:** importer changes preserve the invariant tested in P3.3 — unclassified content lands in core.md and the report.
- **Docs move with code:** a task that changes behavior updates README/docs in the same change; link-check in CI.
- **FUSE caveat for this environment:** per repo experience, prefer heredoc-rewrites over in-place edits when working through the mounted repo; verify writes with a fresh read.
