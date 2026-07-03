# AgentDef Conformance Corpus

A framework-neutral test corpus for ANY AgentDef validator implementation —
ours or third-party. `manifest.json` maps every case to its SPEC.md S10
conformance rule and the machine-readable error code (Appendix D) a
conforming validator must produce.

- `valid/` — agents that MUST pass validation.
- `invalid/` — agents that MUST fail, each violating exactly one rule.

Regenerate deterministically with `python tools/gen_conformance.py`.
The driver for our validator is `tests/test_conformance.py`.
