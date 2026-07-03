#!/usr/bin/env python3
"""DEPRECATED wrapper — kept for one release so documented commands keep
working. The real module lives in the installable ``agentdef`` package
(agentdef.adapters.cursor.generate). Use ``pip install -e .`` + the ``agentdef`` CLI, or import the
package module directly."""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "pysrc"))
warnings.warn(
    "adapters/cursor/generate.py is a deprecated wrapper; use the agentdef package (agentdef.adapters.cursor.generate) or the agentdef CLI instead.",
    DeprecationWarning,
    stacklevel=2,
)
from agentdef.adapters.cursor.generate import *          # noqa: F401,F403 — re-export module API
from agentdef.adapters.cursor.generate import main       # noqa: F401

if __name__ == "__main__":
    main()
