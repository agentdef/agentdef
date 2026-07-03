"""Shared utilities for AgentDef adapters."""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class AgentDef:
    """Loaded AgentDef agent directory."""

    def __init__(self, agent_dir: str):
        self.root = Path(agent_dir).resolve()
        if not self.root.is_dir():
            raise FileNotFoundError(f"Not a directory: {self.root}")

        self.agent_md = self._read("agent.md")
        self.manifest = self._load_manifest()
        self.name = self.manifest.get("name", self.root.name)
        self.instructions = self._read_list("instructions")
        self.workflows = self._read_list("workflows")
        self.skills = self._read_skills()

    def _read(self, rel_path: str) -> str:
        path = self.root / rel_path
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def _load_manifest(self) -> dict:
        path = self.root / "manifest.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Missing manifest.yaml in {self.root}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _read_list(self, field: str) -> list[tuple[str, str]]:
        """Read files listed under a manifest field. Returns [(path, content)]."""
        entries = []
        for ref in self.manifest.get(field, []):
            content = self._read(ref)
            if content:
                entries.append((ref, content))
        return entries

    def _read_skills(self) -> list[tuple[str, str]]:
        """Read SKILL.md from each skill directory."""
        entries = []
        for ref in self.manifest.get("skills", []):
            skill_path = self.root / ref / "SKILL.md"
            if skill_path.exists():
                entries.append((ref, skill_path.read_text(encoding="utf-8")))
        return entries


def write_output(content: str, output_path: str | None) -> None:
    """Write content to file or stdout."""
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        print(f"Written to {output_path}", file=sys.stderr)
    else:
        print(content)
