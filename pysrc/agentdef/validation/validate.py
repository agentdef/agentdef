#!/usr/bin/env python3
"""AgentDef validator — structure + content validation for AgentDef agents.

Usage:
    python validate.py <agent_directory> [--schema-dir <path>]

Checks:
    1. Required files exist (agent.md, manifest.yaml, instructions/core.md)
    2. manifest.yaml is valid YAML
    3. manifest.yaml conforms to the JSON Schema
    4. All file/directory references in manifest.yaml resolve
    5. agent.md contains a Role section
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema is required. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


class ValidationResult:
    """Collects errors and warnings from validation."""

    def __init__(self, agent_dir: str):
        self.agent_dir = agent_dir
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.codes: list[str] = []  # machine-readable error codes (SPEC.md Appendix D)

    def error(self, msg: str, code: str = "generic") -> None:
        self.errors.append(msg)
        self.codes.append(code)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        if self.errors:
            lines.append(f"FAIL: {self.agent_dir} — {len(self.errors)} error(s)")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
        else:
            lines.append(f"PASS: {self.agent_dir}")
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation steps
# ---------------------------------------------------------------------------

REQUIRED_FILES = [
    "agent.md",
    "manifest.yaml",
    os.path.join("instructions", "core.md"),
]

# Fields in manifest.yaml whose values are file or directory paths
PATH_FIELDS = ["instructions", "workflows", "tools"]
DIR_FIELDS = ["skills"]

# Spec versions this validator implements. Compatibility policy (SPEC.md S13):
# a validator MUST accept manifests without spec_version (implied: oldest
# supported), MUST accept any listed version, and MUST reject unknown ones
# with a clear message rather than guessing.
SUPPORTED_SPEC_VERSIONS = ("0.1", "0.2", "0.5")


def check_spec_version(manifest: dict, result: ValidationResult) -> None:
    """spec_version is optional; when present it must be one we support."""
    sv = manifest.get("spec_version")
    if sv is None:
        return
    if str(sv) not in SUPPORTED_SPEC_VERSIONS:
        result.error(
            f"unsupported spec_version {sv!r}; this validator supports: "
            + ", ".join(SUPPORTED_SPEC_VERSIONS),
            code="unsupported-spec-version",
        )


def check_reference_containment(manifest: dict, agent_dir: Path, result: ValidationResult) -> None:
    """All referenced paths must resolve inside the agent directory (SPEC S10 rule 5)."""
    root = agent_dir.resolve()
    for field in PATH_FIELDS + DIR_FIELDS:
        refs = manifest.get(field, [])
        if not isinstance(refs, list):
            continue  # schema check reports the type error
        for ref in refs:
            if not isinstance(ref, str):
                continue
            target = (agent_dir / ref).resolve()
            if root not in target.parents and target != root:
                result.error(
                    f"manifest.yaml reference escapes the agent directory: {field} -> {ref}",
                    code="reference-escapes-root",
                )


def check_structure(agent_dir: Path, result: ValidationResult) -> None:
    """Check that required files and directories exist."""
    for rel in REQUIRED_FILES:
        if not (agent_dir / rel).exists():
            code = {
                "agent.md": "missing-agent-md",
                "manifest.yaml": "missing-manifest",
            }.get(rel, "missing-core-instructions")
            result.error(f"Missing required file: {rel}", code=code)


def load_manifest(agent_dir: Path, result: ValidationResult) -> dict | None:
    """Parse manifest.yaml and return its contents, or None on failure."""
    manifest_path = agent_dir / "manifest.yaml"
    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        result.error(f"manifest.yaml is not valid YAML: {e}", code="invalid-yaml")
        return None

    if not isinstance(data, dict):
        result.error("manifest.yaml must be a YAML mapping (object)", code="invalid-yaml")
        return None

    return data


def check_schema(manifest: dict, schema_dir: Path, result: ValidationResult) -> None:
    """Validate manifest against the JSON Schema."""
    schema_path = schema_dir / "manifest.schema.json"
    if not schema_path.exists():
        result.warn(f"Schema not found at {schema_path}, skipping schema validation")
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=manifest, schema=schema)
    except jsonschema.ValidationError as e:
        result.error(f"manifest.yaml schema violation: {e.message}", code="schema-violation")


def check_references(manifest: dict, agent_dir: Path, result: ValidationResult) -> None:
    """Verify that all paths declared in manifest resolve to existing files or dirs."""
    for field in PATH_FIELDS:
        refs = manifest.get(field, [])
        if not isinstance(refs, list):
            continue  # schema check reports the type error
        for ref in refs:
            target = agent_dir / ref
            if not target.exists():
                result.error(f"manifest.yaml references missing file: {field} → {ref}", code="missing-reference")

    for field in DIR_FIELDS:
        refs = manifest.get(field, [])
        if not isinstance(refs, list):
            continue  # schema check reports the type error
        for ref in refs:
            target = agent_dir / ref
            if not target.exists():
                result.error(f"manifest.yaml references missing directory: {field} → {ref}", code="missing-reference")
            elif not target.is_dir():
                result.warn(f"manifest.yaml skill reference is a file, expected directory: {field} → {ref}")


def check_agent_md(agent_dir: Path, result: ValidationResult) -> None:
    """Verify agent.md contains a Role section."""
    agent_path = agent_dir / "agent.md"
    if not agent_path.exists():
        return  # Already caught by structure check

    content = agent_path.read_text(encoding="utf-8")
    if not re.search(r"^##?\s+Role", content, re.MULTILINE | re.IGNORECASE):
        result.error("agent.md must contain a '## Role' section", code="missing-role")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate(agent_dir: str, schema_dir: str | None = None) -> ValidationResult:
    """Run all validation checks on an agent directory."""
    agent_path = Path(agent_dir).resolve()
    result = ValidationResult(str(agent_path))

    if not agent_path.is_dir():
        result.error(f"Not a directory: {agent_path}")
        return result

    # Resolve schema directory
    if schema_dir:
        schema_path = Path(schema_dir).resolve()
    else:
        # Default: look for schemas/ relative to the repo root (two levels up from validation/)
        schema_path = Path(__file__).resolve().parent.parent / "schemas"

    check_structure(agent_path, result)
    check_agent_md(agent_path, result)

    manifest = load_manifest(agent_path, result)
    if manifest is not None:
        check_schema(manifest, schema_path, result)
        check_spec_version(manifest, result)
        check_reference_containment(manifest, agent_path, result)
        check_references(manifest, agent_path, result)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an AgentDef agent directory.",
        epilog="Example: python validate.py ../examples/twitter-digest",
    )
    parser.add_argument(
        "agent_dirs",
        nargs="+",
        help="Path(s) to agent directories to validate.",
    )
    parser.add_argument(
        "--schema-dir",
        default=None,
        help="Path to the schemas/ directory (default: auto-detected).",
    )
    args = parser.parse_args()

    all_valid = True
    for agent_dir in args.agent_dirs:
        result = validate(agent_dir, args.schema_dir)
        print(result.summary())
        if not result.valid:
            all_valid = False

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
