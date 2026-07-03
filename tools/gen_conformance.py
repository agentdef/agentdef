#!/usr/bin/env python3
"""Generate the public conformance corpus (TASKS.md P2.2).

Deterministic: running this script always produces the same corpus. Each
invalid case violates exactly one numbered conformance rule from SPEC.md S10
and declares the validator error code it must trigger. conformance/manifest.json
maps every case to its rule and expected code — third-party validators test
against that mapping, not against our validator's prose messages.

Usage: python tools/gen_conformance.py   (from the repo root)
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "conformance"

AGENT_MD = """# {name}

## Role
{role}

## Objectives
- Demonstrate a conformance case.

## Style
- concise
"""

CORE_MD = "# Core Instructions\n\n- Answer precisely.\n- Cite sources when available.\n"
MANIFEST = "name: {name}\n\ninstructions:\n  - instructions/core.md\n"

CASES: list[dict] = []


def base_agent(
    d: Path,
    name: str,
    *,
    agent_md: bool = True,
    manifest: bool = True,
    core: bool = True,
    instructions_dir: bool = True,
) -> None:
    """Build a base agent, omitting parts a case needs absent.

    Never deletes anything (needed both for determinism and for filesystems
    where the generator lacks delete permission).
    """
    if instructions_dir:
        (d / "instructions").mkdir(parents=True, exist_ok=True)
    if agent_md:
        (d / "agent.md").write_text(AGENT_MD.format(name=name, role="Reference conformance agent."), encoding="utf-8")
    if core and instructions_dir:
        (d / "instructions" / "core.md").write_text(CORE_MD, encoding="utf-8")
    if manifest:
        (d / "manifest.yaml").write_text(MANIFEST.format(name=name), encoding="utf-8")


def case(kind: str, slug: str, rule: int | None, code: str | None, note: str):
    def deco(fn):
        CASES.append({"kind": kind, "slug": slug, "rule": rule, "code": code, "note": note, "build": fn})
        return fn
    return deco


# ---------------- valid cases ----------------

def v(slug, note):
    return case("valid", slug, None, None, note)

@v("minimal", "smallest conforming agent")
def _(d): base_agent(d, "minimal")

@v("spec-version-01", "explicit spec_version 0.1")
def _(d):
    base_agent(d, "sv01"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "spec_version: '0.1'\n")

@v("spec-version-05", "explicit spec_version 0.5")
def _(d):
    base_agent(d, "sv05"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "spec_version: '0.5'\n")

@v("with-skills", "skills directory declared and present")
def _(d):
    base_agent(d, "with-skills")
    (d / "skills" / "summarize").mkdir(parents=True, exist_ok=True)
    (d / "skills" / "summarize" / "SKILL.md").write_text("# Summarize\n\n## Inputs\n- text\n\n## Outputs\n- summary\n")
    mf = d / "manifest.yaml"; mf.write_text(mf.read_text() + "\nskills:\n  - skills/summarize\n")

@v("with-workflows", "workflow file declared and present")
def _(d):
    base_agent(d, "with-workflows")
    (d / "workflows").mkdir(exist_ok=True); (d / "workflows" / "run.md").write_text("# Run\n\n1. Collect\n2. Summarize\n")
    mf = d / "manifest.yaml"; mf.write_text(mf.read_text() + "\nworkflows:\n  - workflows/run.md\n")

@v("with-tools", "tools file declared and present")
def _(d):
    base_agent(d, "with-tools")
    (d / "tools").mkdir(exist_ok=True); (d / "tools" / "search.yaml").write_text("name: search\nkind: http\n")
    mf = d / "manifest.yaml"; mf.write_text(mf.read_text() + "\ntools:\n  - tools/search.yaml\n")

@v("multi-instructions", "several instruction files")
def _(d):
    base_agent(d, "multi")
    (d / "instructions" / "safety.md").write_text("# Safety\n\n- Refuse harmful requests.\n")
    (d / "instructions" / "style.md").write_text("# Style\n\n- Be brief.\n")
    mf = d / "manifest.yaml"
    mf.write_text("name: multi\n\ninstructions:\n  - instructions/core.md\n  - instructions/safety.md\n  - instructions/style.md\n")

@v("custom-directory", "unrecognized directory must be ignored (S11)")
def _(d):
    base_agent(d, "custom-dir")
    (d / "my-extras").mkdir(exist_ok=True); (d / "my-extras" / "notes.md").write_text("scratch\n")

@v("custom-manifest-fields", "x- prefixed custom fields must be accepted (S11)")
def _(d):
    base_agent(d, "custom-fields"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\nx-myorg-tier: gold\nx-myorg-owner: data-team\n")

@v("role-h1", "Role as an H1 header is accepted")
def _(d):
    base_agent(d, "role-h1")
    (d / "agent.md").write_text("# role-h1\n\n# Role\nTop-level role header.\n")

@v("role-lowercase", "role section header is case-insensitive")
def _(d):
    base_agent(d, "role-lower")
    (d / "agent.md").write_text("# role-lower\n\n## role\nlowercase header.\n")

@v("unicode-content", "non-ASCII content everywhere")
def _(d):
    base_agent(d, "unicode")
    (d / "agent.md").write_text("# unicode\n\n## Role\nAgent editorial en català — resums de qualitat, čeština, 日本語.\n")

@v("optional-dirs-present", "knowledge/, memory/, runtime/, evals/ present but undeclared")
def _(d):
    base_agent(d, "optional-dirs")
    for sub in ("knowledge", "memory", "runtime", "evals"):
        (d / sub).mkdir(exist_ok=True); (d / sub / "README.md").write_text(f"{sub} placeholder\n")

@v("description-and-version", "optional schema fields used")
def _(d):
    base_agent(d, "described"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\ndescription: a described agent\nversion: '1.2.3'\n")

@v("capabilities-and-inputs", "capabilities/input_types optional fields")
def _(d):
    base_agent(d, "capable"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\ncapabilities:\n  - summarization\ninput_types:\n  - markdown\n")

@v("nested-instructions", "instruction file in a subdirectory")
def _(d):
    base_agent(d, "nested")
    (d / "instructions" / "domain").mkdir(exist_ok=True)
    (d / "instructions" / "domain" / "finance.md").write_text("# Finance\n\n- Use ISO currency codes.\n")
    mf = d / "manifest.yaml"
    mf.write_text("name: nested\n\ninstructions:\n  - instructions/core.md\n  - instructions/domain/finance.md\n")

@v("readme-present", "README.md alongside required files")
def _(d):
    base_agent(d, "readmed"); (d / "README.md").write_text("# Readme\nHuman docs.\n")

@v("deep-skill-tree", "skill with examples subdirectory")
def _(d):
    base_agent(d, "deep-skill")
    ex = d / "skills" / "classify" / "examples"; ex.mkdir(parents=True, exist_ok=True)
    (d / "skills" / "classify" / "SKILL.md").write_text("# Classify\n")
    (ex / "one.md").write_text("example\n")
    mf = d / "manifest.yaml"; mf.write_text(mf.read_text() + "\nskills:\n  - skills/classify\n")

@v("crlf-line-endings", "CRLF files are fine")
def _(d):
    base_agent(d, "crlf")
    (d / "agent.md").write_bytes(b"# crlf\r\n\r\n## Role\r\nWindows-authored agent.\r\n")

@v("large-core", "large core.md")
def _(d):
    base_agent(d, "large")
    (d / "instructions" / "core.md").write_text("# Core\n\n" + "- Rule line.\n" * 500)

# ---------------- invalid cases ----------------

def i(slug, rule, code, note):
    return case("invalid", slug, rule, code, note)

@i("rule1-agent-md-absent", 1, "missing-agent-md", "no agent.md at root")
def _(d):
    base_agent(d, "x", agent_md=False)

@i("rule1-role-absent", 1, "missing-role", "agent.md without Role section")
def _(d):
    base_agent(d, "x"); (d / "agent.md").write_text("# x\n\n## Objectives\n- none\n")

@i("rule1-role-not-a-header", 1, "missing-role", "the word Role appears only in prose")
def _(d):
    base_agent(d, "x"); (d / "agent.md").write_text("# x\n\nThe Role of this agent is helping.\n")

@i("rule1-role-h3", 1, "missing-role", "### Role (level 3) is not a recognized Role section")
def _(d):
    base_agent(d, "x"); (d / "agent.md").write_text("# x\n\n### Role\ntoo deep\n")

@i("rule2-missing-manifest", 2, "missing-manifest", "no manifest.yaml")
def _(d):
    base_agent(d, "x", manifest=False)

@i("rule2-manifest-not-mapping", 2, "invalid-yaml", "manifest.yaml is a YAML list, not a mapping")
def _(d):
    base_agent(d, "x"); (d / "manifest.yaml").write_text("- just\n- a\n- list\n")

@i("rule2-name-missing", 2, "schema-violation", "manifest lacks required name")
def _(d):
    base_agent(d, "x"); (d / "manifest.yaml").write_text("instructions:\n  - instructions/core.md\n")

@i("rule2-instructions-missing", 2, "schema-violation", "manifest lacks required instructions list")
def _(d):
    base_agent(d, "x"); (d / "manifest.yaml").write_text("name: x\n")

@i("rule2-instructions-empty", 2, "schema-violation", "instructions list is empty")
def _(d):
    base_agent(d, "x"); (d / "manifest.yaml").write_text("name: x\ninstructions: []\n")

@i("rule3-core-missing", 3, "missing-core-instructions", "instructions/core.md absent")
def _(d):
    base_agent(d, "x", core=False)

@i("rule3-no-instructions-dir", 3, "missing-core-instructions", "whole instructions/ dir absent")
def _(d):
    base_agent(d, "x", core=False, instructions_dir=False)
    (d / "manifest.yaml").write_text("name: x\n\ninstructions:\n  - agent.md\n")

@i("rule4-missing-instruction-ref", 4, "missing-reference", "manifest references a nonexistent instruction file")
def _(d):
    base_agent(d, "x")
    (d / "manifest.yaml").write_text("name: x\n\ninstructions:\n  - instructions/core.md\n  - instructions/ghost.md\n")

@i("rule4-missing-workflow-ref", 4, "missing-reference", "manifest references a nonexistent workflow")
def _(d):
    base_agent(d, "x"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\nworkflows:\n  - workflows/ghost.md\n")

@i("rule4-missing-skill-dir", 4, "missing-reference", "manifest references a nonexistent skill directory")
def _(d):
    base_agent(d, "x"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\nskills:\n  - skills/ghost\n")

@i("rule4-missing-tool-ref", 4, "missing-reference", "manifest references a nonexistent tool file")
def _(d):
    base_agent(d, "x"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\ntools:\n  - tools/ghost.yaml\n")

@i("rule5-parent-escape", 5, "reference-escapes-root", "reference climbs out with ../")
def _(d):
    base_agent(d, "x")
    (d / "manifest.yaml").write_text("name: x\n\ninstructions:\n  - instructions/core.md\n  - ../outside.md\n")

@i("rule5-absolute-path", 5, "reference-escapes-root", "reference is an absolute path")
def _(d):
    base_agent(d, "x")
    (d / "manifest.yaml").write_text("name: x\n\ninstructions:\n  - instructions/core.md\n  - /etc/hostname\n")

@i("rule6-name-not-string", 6, "schema-violation", "name has the wrong type")
def _(d):
    base_agent(d, "x")
    (d / "manifest.yaml").write_text("name: [not, a, string]\n\ninstructions:\n  - instructions/core.md\n")

@i("rule6-instructions-not-list", 6, "schema-violation", "instructions is a string, not a list")
def _(d):
    base_agent(d, "x")
    (d / "manifest.yaml").write_text("name: x\n\ninstructions: instructions/core.md\n")

@i("rule6-skills-not-list", 6, "schema-violation", "skills is a mapping, not a list")
def _(d):
    base_agent(d, "x"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\nskills:\n  main: skills/main\n")

@i("rule6-description-not-string", 6, "schema-violation", "description has the wrong type")
def _(d):
    base_agent(d, "x"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\ndescription: 42\n")

@i("rule7-spec-version-unknown", 7, "unsupported-spec-version", "spec_version from the future")
def _(d):
    base_agent(d, "x"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\nspec_version: '99.0'\n")

@i("rule7-spec-version-garbage", 7, "unsupported-spec-version", "spec_version is not a version at all")
def _(d):
    base_agent(d, "x"); mf = d / "manifest.yaml"
    mf.write_text(mf.read_text() + "\nspec_version: banana\n")

@i("rule2-invalid-yaml-syntax", 2, "invalid-yaml", "manifest.yaml is not parseable YAML")
def _(d):
    base_agent(d, "x"); (d / "manifest.yaml").write_text("name: [unclosed\ninstructions:\n  - instructions/core.md\n")

@i("rule1-agent-md-empty", 1, "missing-role", "agent.md exists but is empty")
def _(d):
    base_agent(d, "x"); (d / "agent.md").write_text("")


def main() -> None:
    (OUT / "valid").mkdir(parents=True, exist_ok=True)
    (OUT / "invalid").mkdir(parents=True, exist_ok=True)
    index = []
    for c in CASES:
        d = OUT / c["kind"] / c["slug"]
        d.mkdir(parents=True, exist_ok=True)
        c["build"](d)
        index.append({k: c[k] for k in ("kind", "slug", "rule", "code", "note")})
    (OUT / "manifest.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    nv = sum(1 for c in CASES if c["kind"] == "valid")
    ni = len(CASES) - nv
    print(f"conformance corpus: {nv} valid, {ni} invalid -> {OUT}")


if __name__ == "__main__":
    main()
