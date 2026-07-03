"""Tests that valid AgentDef examples pass validation."""

import sys
from pathlib import Path


from agentdef.validation.validate import validate


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
TEMPLATES_DIR = REPO_ROOT / "templates"


class TestTwitterDigest:
    """The twitter-digest example should pass all checks."""

    def test_validates_successfully(self):
        result = validate(str(EXAMPLES_DIR / "twitter-digest"))
        assert result.valid, result.summary()

    def test_no_warnings(self):
        result = validate(str(EXAMPLES_DIR / "twitter-digest"))
        assert len(result.warnings) == 0, f"Unexpected warnings: {result.warnings}"


class TestMissionWriter:
    """The mission-writer example should pass all checks."""

    def test_validates_successfully(self):
        result = validate(str(EXAMPLES_DIR / "mission-writer"))
        assert result.valid, result.summary()

    def test_no_warnings(self):
        result = validate(str(EXAMPLES_DIR / "mission-writer"))
        assert len(result.warnings) == 0, f"Unexpected warnings: {result.warnings}"


class TestStarterTemplate:
    """The starter template should pass structural validation.

    Note: the starter template contains placeholder text, so it is
    expected to pass structure checks but the content is intentionally
    generic.
    """

    def test_validates_successfully(self):
        result = validate(str(TEMPLATES_DIR / "starter"))
        assert result.valid, result.summary()
