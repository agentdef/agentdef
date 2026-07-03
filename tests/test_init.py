"""P4.1: agentdef init tests."""

import pytest

from agentdef.init import init_agent
from agentdef.sync import sync
from agentdef.validation.validate import validate


def test_init_yes_produces_valid_agent(tmp_path):
    root = init_agent(str(tmp_path / "my-agent"), yes=True)
    result = validate(str(root))
    assert result.valid, result.errors


def test_init_sync_targets_adapt_cleanly(tmp_path):
    root = init_agent(str(tmp_path / "bot"), name="release-bot",
                      frameworks=["claude", "copilot", "m365copilot"], yes=True)
    assert validate(str(root)).valid
    changed, _ = sync(str(root))
    assert len(changed) == 3
    assert (root / "framework/m365copilot/declarativeAgent.json").exists()


def test_init_refuses_existing_agent(tmp_path):
    init_agent(str(tmp_path / "a"), yes=True)
    with pytest.raises(FileExistsError):
        init_agent(str(tmp_path / "a"), yes=True)


def test_init_rejects_unknown_framework(tmp_path):
    with pytest.raises(ValueError):
        init_agent(str(tmp_path / "b"), frameworks=["notaframework"], yes=True)
