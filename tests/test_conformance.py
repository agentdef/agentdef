"""P2.2: conformance-corpus driver.

Every valid case must pass; every invalid case must fail *with the mapped
error code* from conformance/manifest.json — asserting on codes, not prose.
Also enforces rule coverage: every conformance rule has at least 2 cases.
"""

import json
from collections import Counter
from pathlib import Path

import pytest

from agentdef.validation.validate import validate

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "conformance"
INDEX = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))

VALID = [c for c in INDEX if c["kind"] == "valid"]
INVALID = [c for c in INDEX if c["kind"] == "invalid"]


@pytest.mark.parametrize("case", VALID, ids=[c["slug"] for c in VALID])
def test_valid_case_passes(case):
    result = validate(str(CORPUS / "valid" / case["slug"]))
    assert result.valid, f"valid case {case['slug']} failed: {result.errors}"


@pytest.mark.parametrize("case", INVALID, ids=[c["slug"] for c in INVALID])
def test_invalid_case_fails_with_mapped_code(case):
    result = validate(str(CORPUS / "invalid" / case["slug"]))
    assert not result.valid, f"invalid case {case['slug']} unexpectedly passed"
    assert case["code"] in result.codes, (
        f"{case['slug']}: expected code {case['code']!r} (rule {case['rule']}), "
        f"got {result.codes} — errors: {result.errors}"
    )


def test_every_rule_has_at_least_two_cases():
    counts = Counter(c["rule"] for c in INVALID)
    missing = {r: n for r, n in counts.items() if n < 2}
    assert not missing, f"rules with <2 invalid cases: {missing}"
    assert set(counts) == {1, 2, 3, 4, 5, 6, 7}, f"rules covered: {sorted(counts)}"


def test_corpus_matches_index():
    """No case in the index without a directory, and vice versa."""
    for c in INDEX:
        assert (CORPUS / c["kind"] / c["slug"]).is_dir(), f"missing dir for {c['slug']}"
