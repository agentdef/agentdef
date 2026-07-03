"""`agentdef sync` (P3.10): regenerate every configured framework file from
the canonical AgentDef definition.

Configuration lives in manifest.yaml:

    sync:
      - framework: claude
        output: framework/claude/CLAUDE.md
      - framework: copilot
        output: framework/copilot/copilot-instructions.md

Paths are relative to the agent directory. `sync --check` writes nothing
and exits nonzero when any output is stale (for CI drift checks).
"""

from __future__ import annotations

import importlib
from pathlib import Path

from agentdef.registry import ADAPTERS


class SyncError(Exception):
    pass


def load_targets(agent_dir: Path, manifest: dict) -> list[tuple[str, Path]]:
    raw = manifest.get("sync") or []
    if not isinstance(raw, list):
        raise SyncError("manifest 'sync' must be a list of {framework, output} entries")
    targets = []
    for entry in raw:
        if not isinstance(entry, dict) or "framework" not in entry or "output" not in entry:
            raise SyncError(f"invalid sync entry: {entry!r} (need framework + output)")
        fw = str(entry["framework"])
        if fw not in ADAPTERS:
            raise SyncError(f"unknown sync framework {fw!r}; available: {', '.join(sorted(ADAPTERS))}")
        out = (agent_dir / str(entry["output"])).resolve()
        if agent_dir.resolve() not in out.parents:
            raise SyncError(f"sync output escapes the agent directory: {entry['output']}")
        targets.append((fw, out))
    return targets


def sync(agent_dir: str, check: bool = False) -> tuple[list[str], list[str]]:
    """Returns (written_or_stale, up_to_date) lists of output paths."""
    root = Path(agent_dir)
    first_mod = importlib.import_module(ADAPTERS["claude"].module)
    agent = first_mod.AgentDef(str(root))
    targets = load_targets(root, agent.manifest)
    if not targets:
        raise SyncError("no 'sync' entries in manifest.yaml — nothing to do")

    changed: list[str] = []
    same: list[str] = []
    for fw, out in targets:
        mod = importlib.import_module(ADAPTERS[fw].module)
        generated = mod.generate(mod.AgentDef(str(root)))
        current = out.read_text(encoding="utf-8") if out.exists() else None
        if current == generated:
            same.append(str(out))
            continue
        changed.append(str(out))
        if not check:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(generated, encoding="utf-8")
    return changed, same
