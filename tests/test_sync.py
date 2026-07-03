"""P3.10: agentdef sync tests."""

import shutil
from pathlib import Path

import pytest

from agentdef.sync import SyncError, sync

REPO = Path(__file__).resolve().parent.parent

SYNC_BLOCK = """
sync:
  - framework: claude
    output: framework/claude/CLAUDE.md
  - framework: copilot
    output: framework/copilot/copilot-instructions.md
"""


@pytest.fixture()
def agent(tmp_path):
    dst = tmp_path / "agent"
    shutil.copytree(REPO / "examples" / "mission-writer", dst)
    mf = dst / "manifest.yaml"
    mf.write_text(mf.read_text(encoding="utf-8") + SYNC_BLOCK, encoding="utf-8")
    return dst


def test_sync_writes_all_targets(agent):
    changed, same = sync(str(agent))
    assert len(changed) == 2 and not same
    assert (agent / "framework/claude/CLAUDE.md").exists()
    assert (agent / "framework/copilot/copilot-instructions.md").exists()
    assert "Generated from AgentDef" in (agent / "framework/claude/CLAUDE.md").read_text(encoding="utf-8")


def test_check_fails_when_stale_then_passes_after_sync(agent):
    sync(str(agent))
    changed, _ = sync(str(agent), check=True)
    assert not changed  # fresh
    core = agent / "instructions" / "core.md"
    core.write_text(core.read_text(encoding="utf-8") + "\n- new canonical rule\n", encoding="utf-8")
    changed, _ = sync(str(agent), check=True)
    assert len(changed) == 2  # both outputs stale, nothing written in check mode
    assert "new canonical rule" not in (agent / "framework/claude/CLAUDE.md").read_text(encoding="utf-8")
    sync(str(agent))
    changed, _ = sync(str(agent), check=True)
    assert not changed
    assert "new canonical rule" in (agent / "framework/claude/CLAUDE.md").read_text(encoding="utf-8")


def test_sync_rejects_escaping_output(agent):
    mf = agent / "manifest.yaml"
    mf.write_text(mf.read_text(encoding="utf-8").replace(
        "framework/claude/CLAUDE.md", "../escape.md"), encoding="utf-8")
    with pytest.raises(SyncError):
        sync(str(agent))


def test_sync_without_config_errors(tmp_path):
    dst = tmp_path / "agent"
    shutil.copytree(REPO / "examples" / "twitter-digest", dst)
    with pytest.raises(SyncError):
        sync(str(dst))
