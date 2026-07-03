"""`agentdef init` (P4.1): scaffold a new, valid AgentDef agent.

Interactive by default; `--yes` accepts defaults for scripts/CI.
"""

from __future__ import annotations

from pathlib import Path

from agentdef.registry import ADAPTERS

AGENT_MD = """# {title}

## Role
{role}

## Objectives
- Describe the first concrete objective
- Describe the second concrete objective

## Style
- concise
- precise
"""

CORE_MD = """# Core Instructions

- State the agent's non-negotiable behavioral rules here.
- One rule per bullet; keep them testable.
"""

README = """# {title}

An AgentDef agent. Validate with `agentdef validate .`; generate framework
files with `agentdef sync .` (targets in manifest.yaml).
"""


def _ask(prompt: str, default: str, yes: bool) -> str:
    if yes:
        return default
    answer = input(f"{prompt} [{default}]: ").strip()
    return answer or default


def init_agent(directory: str, name: str | None = None, role: str | None = None,
               frameworks: list[str] | None = None, yes: bool = False) -> Path:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    if (root / "manifest.yaml").exists():
        raise FileExistsError(f"{root} already contains a manifest.yaml")

    name = name or _ask("Agent name (kebab-case)", root.resolve().name, yes)
    role = role or _ask("One-line role", "A helpful, specialized assistant.", yes)
    if frameworks is None:
        raw = _ask(f"Sync targets, comma-separated ({', '.join(sorted(ADAPTERS))}; empty for none)",
                   "claude,copilot", yes)
        frameworks = [f.strip() for f in raw.split(",") if f.strip()]
    unknown = [f for f in frameworks if f not in ADAPTERS]
    if unknown:
        raise ValueError(f"unknown frameworks: {', '.join(unknown)}")

    title = name.replace("-", " ").replace("_", " ").title()
    (root / "instructions").mkdir(exist_ok=True)
    (root / "agent.md").write_text(AGENT_MD.format(title=title, role=role), encoding="utf-8")
    (root / "instructions" / "core.md").write_text(CORE_MD, encoding="utf-8")
    (root / "README.md").write_text(README.format(title=title), encoding="utf-8")

    manifest = [f"name: {name}", "", "spec_version: '0.5'", "", "instructions:", "  - instructions/core.md"]
    if frameworks:
        manifest += ["", "sync:"]
        for fw in frameworks:
            manifest += [f"  - framework: {fw}", f"    output: framework/{fw}/{ADAPTERS[fw].output_name}"]
    (root / "manifest.yaml").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    return root
