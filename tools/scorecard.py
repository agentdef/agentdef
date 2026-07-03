#!/usr/bin/env python3
"""Generate docs/scorecard.md (P3.9): per-importer fidelity stats from
running every available local corpus file through its importer.

Corpora are the local clones under ../downloads/ (not committed). Run:
    python tools/scorecard.py [--limit N]
"""

import argparse
import datetime as dt
import importlib
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pysrc"))

from agentdef.registry import IMPORTERS  # noqa: E402
from agentdef.validation.validate import validate  # noqa: E402

CORPORA = [
    ("claude", "awesome-claude-code-subagents-main/categories/*/*.md"),
    ("claude", "awesome-claude-agents-main/**/*.md"),
    ("copilot", "awesome-copilot-main/agents/*.md"),
    ("copilotstudio", "awesome-copilot-studio-agents-main/agents/*/*.md"),
]


def run(limit: int | None) -> str:
    downloads = ROOT.parent / "downloads"
    rows = []
    total = 0
    for fw, pattern in CORPORA:
        files = sorted(p for p in downloads.glob(pattern) if p.name.lower() != "readme.md")
        if limit:
            files = files[:limit]
        if not files:
            continue
        spec = IMPORTERS[fw]
        fn = getattr(importlib.import_module(spec.module), spec.entrypoint)
        crashed = invalid = 0
        mapped = inferred = dropped = 0
        for f in files:
            with tempfile.TemporaryDirectory() as td:
                try:
                    out = fn(str(f), str(Path(td) / "a"))
                except Exception:
                    crashed += 1
                    continue
                if not validate(str(out)).valid:
                    invalid += 1
                    continue
                report = (out / "IMPORT_REPORT.md").read_text(encoding="utf-8")
                mapped += len(re.findall(r"^- ", report.split("## Mapped")[-1].split("##")[0], re.M)) if "## Mapped" in report else report.count("\n- ")
                inferred += report.count("[inferred]") + (len(re.findall(r"^- ", report.split("## Inferred")[-1].split("##")[0], re.M)) if "## Inferred" in report else 0)
                dropped += (len(re.findall(r"^- ", report.split("## Dropped")[-1].split("##")[0], re.M)) if "## Dropped" in report else 0)
        ok = len(files) - crashed - invalid
        total += len(files)
        rows.append((fw, pattern.split("/")[0], len(files), ok, crashed, invalid, mapped, inferred, dropped))

    lines = [
        "# AgentDef Importer Scorecard",
        "",
        f"Generated {dt.date.today().isoformat()} by `tools/scorecard.py` from the local corpus clones in `downloads/` (not committed).",
        "",
        "| Importer | Corpus | Files | Valid out | Crashes | Invalid | Mapped items | Inferred | Dropped |",
        "| -------- | ------ | ----- | --------- | ------- | ------- | ------------ | -------- | ------- |",
    ]
    for fw, corpus, n, ok, crashed, invalid, m, i, d in rows:
        lines.append(f"| {fw} | {corpus} | {n} | {ok} | {crashed} | {invalid} | {m} | {i} | {d} |")
    lines += ["", f"**Total files: {total}.** A crash or invalid output anywhere is a release blocker.", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="cap files per corpus (CI smoke)")
    args = ap.parse_args()
    md = run(args.limit)
    out = ROOT / "docs" / "scorecard.md"
    out.write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
