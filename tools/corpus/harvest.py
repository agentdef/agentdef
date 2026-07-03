#!/usr/bin/env python3
"""Corpus harvester (P3.9) — run from a machine WITH network access.

Downloads real-world agent-definition corpora for importer validation into
../downloads/. Redistribution licenses vary, so only source-URL manifests
are committed; the files themselves stay local.

Usage:
    python tools/corpus/harvest.py            # clone/refresh all corpora
    python tools/corpus/harvest.py --list     # show what would be fetched
"""

import argparse
import subprocess
import sys
from pathlib import Path

DOWNLOADS = Path(__file__).resolve().parent.parent.parent.parent / "downloads"

# corpus name -> (git URL, importer that consumes it)
CORPORA = {
    "awesome-claude-code-subagents-main": ("https://github.com/VoltAgent/awesome-claude-code-subagents", "claude"),
    "awesome-claude-agents-main": ("https://github.com/vijaythecoder/awesome-claude-agents", "claude"),
    "awesome-copilot-main": ("https://github.com/github/awesome-copilot", "copilot"),
    "awesome-copilot-studio-agents-main": ("https://github.com/github/awesome-copilot-studio-agents", "copilotstudio"),
    # Phase 3 expansion targets (harvest, then extend scorecard.py CORPORA):
    "cursor-rules-community": ("https://github.com/PatrickJS/awesome-cursorrules", "cursor"),
    "agents-md-examples": ("https://github.com/openai/agents.md", "openai"),
    "letta-agent-file-examples": ("https://github.com/letta-ai/agent-file", "letta"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    DOWNLOADS.mkdir(exist_ok=True)
    for name, (url, importer) in CORPORA.items():
        dest = DOWNLOADS / name
        print(f"{name:<40} {url}  (importer: {importer})")
        if args.list:
            continue
        if dest.exists():
            subprocess.run(["git", "-C", str(dest), "pull", "--ff-only"], check=False)
        else:
            subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=False)
    if not args.list:
        print("\nNow run: python tools/scorecard.py")


if __name__ == "__main__":
    sys.exit(main())
