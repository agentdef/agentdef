"""Registry of AgentDef adapters and importers.

Single source of truth for which frameworks the toolkit speaks. New
adapters/importers register here; the CLI, docs generators, and tests all
consume this table instead of discovering directories at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdapterSpec:
    framework: str
    module: str            # dotted module path with generate(agent) + main()
    output_name: str       # canonical output filename
    description: str


@dataclass(frozen=True)
class ImporterSpec:
    framework: str
    module: str            # dotted module path
    entrypoint: str        # function (source, output, **kwargs) -> Path
    source_desc: str


ADAPTERS: dict[str, AdapterSpec] = {
    s.framework: s
    for s in [
        AdapterSpec("claude", "agentdef.adapters.claude.generate", "CLAUDE.md", "Claude / Claude Code project instructions"),
        AdapterSpec("openai", "agentdef.adapters.openai.generate", "AGENTS.md", "OpenAI AGENTS.md convention"),
        AdapterSpec("cursor", "agentdef.adapters.cursor.generate", "cursor-rules.md", "Cursor editor rules"),
        AdapterSpec("copilot", "agentdef.adapters.copilot.generate", "copilot-instructions.md", "GitHub Copilot repository instructions"),
        AdapterSpec("langgraph", "agentdef.adapters.langgraph.generate", "graph.py", "LangGraph graph scaffold"),
        AdapterSpec("m365copilot", "agentdef.adapters.m365copilot.generate", "declarativeAgent.json", "Microsoft 365 Copilot declarative agent manifest"),
        AdapterSpec("assistants", "agentdef.adapters.assistants.generate", "assistant.json", "OpenAI Assistants API create payload"),
        AdapterSpec("crewai", "agentdef.adapters.crewai.generate", "crew.yaml", "CrewAI agents/tasks YAML config"),
    ]
}

IMPORTERS: dict[str, ImporterSpec] = {
    s.framework: s
    for s in [
        ImporterSpec("claude", "agentdef.importers.claude.importer", "import_claude_md", "CLAUDE.md or a Claude Code subagent .md file"),
        ImporterSpec("copilot", "agentdef.importers.copilot.importer", "import_copilot", ".github/copilot-instructions.md or a *.agent.md custom agent"),
        ImporterSpec("m365copilot", "agentdef.importers.m365copilot.importer", "import_m365copilot", "declarativeAgent.json"),
        ImporterSpec("copilotstudio", "agentdef.importers.copilotstudio.importer", "import_copilotstudio", "a Copilot Studio agent .md file"),
        ImporterSpec("cursor", "agentdef.importers.cursor.importer", "import_cursor", "cursor-rules.md, .cursorrules, or a .cursor/rules/*.mdc file"),
        ImporterSpec("openai", "agentdef.importers.openai.importer", "import_openai", "an AGENTS.md file (agents.md convention)"),
        ImporterSpec("generic", "agentdef.importers.generic.importer", "import_generic", "any markdown system-prompt/persona file"),
        ImporterSpec("crewai", "agentdef.importers.crewai.importer", "import_crewai", "CrewAI crew.yaml or config/agents.yaml"),
        ImporterSpec("letta", "agentdef.importers.letta.importer", "import_letta", "a Letta Agent File (.af, behavior subset)"),
    ]
}
