"""Golden-file tests for every adapter (P1.3).

Each adapter's output for the two reference examples is committed under
golden/. Any change to adapter output must be deliberate: regenerate the
golden files and review the diff in the same commit.
"""

import importlib
from pathlib import Path

import pytest

from agentdef.registry import ADAPTERS

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
EXAMPLES = ["mission-writer", "twitter-digest"]


@pytest.mark.parametrize("framework", sorted(ADAPTERS))
@pytest.mark.parametrize("example", EXAMPLES)
def test_adapter_output_matches_golden(framework, example):
    golden = HERE / "golden" / f"{framework}--{example}.golden"
    assert golden.exists(), f"missing golden file {golden}"
    mod = importlib.import_module(ADAPTERS[framework].module)
    agent = mod.AgentDef(str(REPO / "examples" / example))
    generated = mod.generate(agent)
    assert generated == golden.read_text(encoding="utf-8"), (
        f"{framework} output for {example} drifted from golden file; "
        "if intentional, regenerate golden/ and review the diff"
    )
