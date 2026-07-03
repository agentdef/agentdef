"""P2.4: round-trip fixed-point tests.

Guarantee: for the claude and copilot adapter/importer pairs,
adapt(import(adapt(x))) is byte-identical to adapt(import(x)) — i.e. one
import/adapt cycle reaches a fixed point and nothing accumulates. First
generation vs second may differ in documented lossy ways (see the fidelity
tables in each framework README); convergence after one cycle may not.
"""

import importlib
from pathlib import Path

import pytest

from agentdef.registry import ADAPTERS, IMPORTERS

REPO = Path(__file__).resolve().parent.parent
DOWNLOADS = REPO.parent / "downloads"
EXAMPLES = ["mission-writer", "twitter-digest"]
PAIRS = ["claude", "copilot", "cursor", "openai"]  # frameworks with both adapter and importer


def _cycle(framework, source_dir, tmp_path, tag):
    a_mod = importlib.import_module(ADAPTERS[framework].module)
    i_spec = IMPORTERS[framework]
    i_fn = getattr(importlib.import_module(i_spec.module), i_spec.entrypoint)
    out_file = tmp_path / f"{tag}.md"
    out_file.write_text(a_mod.generate(a_mod.AgentDef(str(source_dir))), encoding="utf-8")
    return i_fn(str(out_file), str(tmp_path / f"{tag}-imported")), out_file


@pytest.mark.parametrize("framework", PAIRS)
@pytest.mark.parametrize("example", EXAMPLES)
def test_examples_reach_fixed_point(framework, example, tmp_path):
    a_mod = importlib.import_module(ADAPTERS[framework].module)
    agent1, _ = _cycle(framework, REPO / "examples" / example, tmp_path, "g1")
    gen2 = a_mod.generate(a_mod.AgentDef(str(agent1)))
    agent2, _ = _cycle(framework, agent1, tmp_path, "g2")
    gen3 = a_mod.generate(a_mod.AgentDef(str(agent2)))
    assert gen2 == gen3, f"{framework}/{example}: no fixed point after one cycle"


def _corpus_files():
    """Up to 20 real corpus agents (10 claude subagents + 10 copilot)."""
    cases = []
    cl = DOWNLOADS / "awesome-claude-code-subagents-main" / "categories"
    if cl.is_dir():
        files = sorted(p for p in cl.glob("*/*.md") if p.name != "README.md")[:10]
        cases += [("claude", p) for p in files]
    cp = DOWNLOADS / "awesome-copilot-main" / "agents"
    if cp.is_dir():
        files = sorted(p for p in cp.glob("*.md") if p.name != "README.md")[:10]
        cases += [("copilot", p) for p in files]
    return cases


CORPUS = _corpus_files()


@pytest.mark.skipif(not CORPUS, reason="local corpus downloads/ not present")
@pytest.mark.parametrize("framework,src", CORPUS, ids=[f"{f}-{p.stem}" for f, p in CORPUS])
def test_corpus_agents_reach_fixed_point(framework, src, tmp_path):
    i_spec = IMPORTERS[framework]
    i_fn = getattr(importlib.import_module(i_spec.module), i_spec.entrypoint)
    a_mod = importlib.import_module(ADAPTERS[framework].module)

    # Cycle 0: import the raw community file. Cycle 1 may normalize
    # documented lossy details (e.g. literal '---' thematic breaks merge with
    # the adapter's own separators); from cycle 1 on, output must be stable.
    agent1 = i_fn(str(src), str(tmp_path / "imp1"))
    gen1 = a_mod.generate(a_mod.AgentDef(str(agent1)))
    (tmp_path / "g1.md").write_text(gen1, encoding="utf-8")
    agent2 = i_fn(str(tmp_path / "g1.md"), str(tmp_path / "imp2"))
    gen2 = a_mod.generate(a_mod.AgentDef(str(agent2)))
    (tmp_path / "g2.md").write_text(gen2, encoding="utf-8")
    agent3 = i_fn(str(tmp_path / "g2.md"), str(tmp_path / "imp3"))
    gen3 = a_mod.generate(a_mod.AgentDef(str(agent3)))
    assert gen2 == gen3, f"{framework}/{src.name}: no fixed point after one cycle"
