"""P2.1: spec_version acceptance/rejection tests."""

import shutil
from pathlib import Path

from agentdef.validation.validate import validate

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "templates" / "starter"


def _copy_with_spec_version(tmp_path, line):
    agent = tmp_path / "agent"
    shutil.copytree(BASE, agent)
    mf = agent / "manifest.yaml"
    mf.write_text(mf.read_text(encoding="utf-8") + line, encoding="utf-8")
    return agent


def test_accepts_absent_spec_version(tmp_path):
    agent = _copy_with_spec_version(tmp_path, "")
    assert validate(str(agent)).valid


def test_accepts_supported_spec_version(tmp_path):
    agent = _copy_with_spec_version(tmp_path, "\nspec_version: '0.2'\n")
    assert validate(str(agent)).valid


def test_rejects_unsupported_spec_version(tmp_path):
    agent = _copy_with_spec_version(tmp_path, "\nspec_version: '99.0'\n")
    result = validate(str(agent))
    assert not result.valid
    assert "unsupported-spec-version" in result.codes
    assert any("99.0" in e and "supports" in e for e in result.errors)
