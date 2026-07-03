#!/usr/bin/env python3
"""DEPRECATED wrapper — kept for one release so documented commands keep
working. The real module lives in the installable ``agentdef`` package
(agentdef.importers.copilotstudio.importer). Use ``pip install -e .`` + the ``agentdef`` CLI, or import the
package module directly."""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "pysrc"))
warnings.warn(
    "importers/copilotstudio/import.py is a deprecated wrapper; use the agentdef package (agentdef.importers.copilotstudio.importer) or the agentdef CLI instead.",
    DeprecationWarning,
    stacklevel=2,
)
from agentdef.importers.copilotstudio.importer import *          # noqa: F401,F403 — re-export module API
from agentdef.importers.copilotstudio.importer import main       # noqa: F401

if __name__ == "__main__":
    main()
