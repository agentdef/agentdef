#!/usr/bin/env python3
"""Generate docs/gallery.md (P4.6): an index of real community agents that
import cleanly into AgentDef. Links to upstream sources (no redistribution —
licenses vary); every listed entry was import-validated by this script.

Usage: python tools/gallery.py [--per-corpus N]
"""

import argparse
import datetime as dt
import importlib
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pysrc"))

from agentdef.registry import IMPORTERS  # noqa: E402
from agentdef.validation.validate import validate  # noqa: E402

CORPORA = [
    ("claude", "awesome-claude-code-subagents-main/categories/*/*.md",
     "https://github.com/VoltAgent/awesome-claude-code-subagents"),
    ("copilot", "awesome-copilot-main/agents/*.md",
     "https://github.com/github/awesome-copilot"),
    ("copilotstudio", "awesome-copilot-studio-agents-main/agents/*/*.md",
     "https://github.com/github/awesome-copilot-studio-agents"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-corpus", type=int, default=8)
    args = ap.parse_args()
    downloads = ROOT.parent / "downloads"
    lines = [
        "# Agent Gallery",
        "",
        f"Real community agents verified to import cleanly into AgentDef "
        f"(generated {dt.date.today().isoformat()} by `tools/gallery.py`; every entry "
        "was imported and validated at generation time). Files stay at their "
        "upstream source — import them yourself:",
        "",
        "```bash",
        "agentdef import <framework> <downloaded-file> --output ./agent",
        "```",
        "",
    ]
    for fw, pattern, repo in CORPORA:
        files = sorted(p for p in downloads.glob(pattern) if p.name.lower() != "readme.md")[: args.per_corpus]
        if not files:
            continue
        spec = IMPORTERS[fw]
        fn = getattr(importlib.import_module(spec.module), spec.entrypoint)
        lines += [f"## {fw} — [{repo.split('github.com/')[1]}]({repo})", ""]
        for f in files:
            with tempfile.TemporaryDirectory() as td:
                try:
                    out = fn(str(f), str(Path(td) / "a"))
                    ok = validate(str(out)).valid
                except Exception:
                    ok = False
            if not ok:
                continue
            rel = f.relative_to(downloads).as_posix()
            rel_in_repo = rel.split("/", 1)[1]
            lines.append(f"- [`{f.stem}`]({repo}/blob/main/{rel_in_repo}) — imports clean, validates ✓")
        lines.append("")
    out = ROOT / "docs" / "gallery.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
