# Spec Review Checklist (P2.3)

Before releasing a spec version, verify each canonical component section in
SPEC.md states what a validator MUST check (or explicitly that the
component is advisory/optional):

- [x] `agent.md` — Role required (rule 1); canonical section names; unknown-section policy (5.1)
- [x] `manifest.yaml` — required fields, schema, spec_version (rules 2, 6, 7)
- [x] `instructions/` — core.md required (rule 3)
- [x] `skills/` — directory references must exist (rule 4)
- [x] `workflows/` — file references must exist (rule 4)
- [x] `memory/` — optional, shape-not-state contract (5.6)
- [x] `knowledge/` — optional content; references covered by rules 4–5
- [x] `tools/` — optional, name/kind contract, no secrets (5.8)
- [x] `runtime/` — optional, advisory, unknown-keys-preserved (5.9)
- [x] `evals/` — optional, declarative, never executed by validators (5.10)
- [x] `framework/` — unconstrained by design (5.11)
- [x] Reference containment (rule 5) and error codes (Appendix D)
- [x] Import reports + round-trip fixed point (Appendix E)

Every normative statement above is exercised by at least one conformance
corpus case (`conformance/manifest.json`) or unit test; the coverage test
is `tests/test_conformance.py::test_every_rule_has_at_least_two_cases`.
