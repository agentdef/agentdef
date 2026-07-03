#!/usr/bin/env python3
"""Import a Microsoft 365 Copilot declarative agent manifest
(declarativeAgent.json, schema v1.0-1.7) into a conformant AgentDef
directory.

The forward adapter is agentdef/adapters/m365copilot (added in Phase 3),
so this pair round-trips: declarative agent manifest <-> AgentDef.

Reference: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-manifest-1.7

Usage:
    python import.py <path-to-declarativeAgent.json> --output <agent-directory>
"""

import argparse
import json
import sys
from pathlib import Path

from agentdef.importers._common import AgentDefWriter, ImportReport, find_persona_sentence

# Known capability `name` values -> human-readable description, used to
# render tools/<capability>.md without inventing content beyond what the
# schema already documents.
CAPABILITY_DESCRIPTIONS = {
    "WebSearch": "Lets the agent search the web for grounding information.",
    "OneDriveAndSharePoint": "Lets the agent search the user's OneDrive and SharePoint content.",
    "GraphConnectors": "Lets the agent search selected Microsoft Graph (Copilot) connectors.",
    "GraphicArt": "Lets the agent generate images from text input.",
    "CodeInterpreter": "Lets the agent generate and execute Python code (math, data analysis, visualization).",
    "Dataverse": "Lets the agent search tables in Microsoft Dataverse.",
    "TeamsMessages": "Lets the agent search Microsoft Teams channels, meetings, and chats.",
    "Email": "Lets the agent search the user's (or a shared) mailbox.",
    "People": "Lets the agent search for information about people in the organization.",
    "ScenarioModels": "Lets the agent use task-specific models.",
    "Meetings": "Lets the agent search for information about meetings.",
    "EmbeddedKnowledge": "Lets the agent use files packaged locally with the agent.",
}


def _render_capability(cap: dict) -> str:
    name = cap.get("name", "UnknownCapability")
    desc = CAPABILITY_DESCRIPTIONS.get(name, "Declarative agent capability.")
    lines = [f"# {name}", "", desc, "", "## Raw capability definition", "", "```json", json.dumps(cap, indent=2), "```"]
    return "\n".join(lines)


def _render_action(action: dict) -> str:
    action_id = action.get("id", "action")
    lines = [f"# Action: {action_id}", ""]
    if "file" in action:
        lines.append(f"References plugin manifest file: `{action['file']}`")
    else:
        lines.append("Inlined plugin manifest:")
        lines += ["", "```json", json.dumps(action, indent=2), "```"]
    return "\n".join(lines)


def import_m365copilot(source_path: str, output_dir: str, name: str | None = None) -> Path:
    src = Path(source_path)
    manifest = json.loads(src.read_text(encoding="utf-8"))

    agent_name = name or manifest.get("name") or src.stem
    description = manifest.get("description", "")
    instructions_text = manifest.get("instructions", "")

    report = ImportReport(
        source=str(src),
        framework=f"Microsoft 365 Copilot (declarative agent manifest {manifest.get('version', '')})",
    )
    writer = AgentDefWriter(output_dir, agent_name, description=description)

    if "name" in manifest:
        report.map("manifest 'name' -> agent.md title / manifest.yaml name")
    if "description" in manifest:
        report.map("manifest 'description' -> agent.md intro / manifest.yaml description")

    # Role: M365 manifests don't separate identity from behavior — both
    # live in the single `instructions` string. Try to pull a persona
    # sentence out of it; otherwise fall back to the description.
    persona = find_persona_sentence(instructions_text)
    if persona:
        writer.set_role(persona)
        report.map("persona sentence within 'instructions' -> agent.md Role")
    elif description:
        writer.set_role(description)
        report.infer("agent.md Role inferred from 'description' (no persona sentence found in 'instructions')")
    elif instructions_text:
        writer.set_role(instructions_text.split(".")[0].strip() + ".")
        report.infer("agent.md Role inferred from the first sentence of 'instructions'")

    if instructions_text:
        writer.add_core_text(instructions_text)
        report.map("'instructions' -> instructions/core.md (full text, including any persona sentence)")
    else:
        report.infer("source manifest had no 'instructions' field; instructions/core.md left as a placeholder")

    for cap in manifest.get("capabilities", []):
        cap_name = cap.get("name", "capability")
        writer.add_tool(cap_name, _render_capability(cap))
    if manifest.get("capabilities"):
        report.map(f"'capabilities' -> tools/ ({len(manifest['capabilities'])} capability object(s))")

    for action in manifest.get("actions", []):
        action_id = action.get("id", "action")
        writer.add_tool(f"action-{action_id}", _render_action(action))
    if manifest.get("actions"):
        report.map(f"'actions' -> tools/ ({len(manifest['actions'])} action/plugin reference(s))")

    starters = manifest.get("conversation_starters", [])
    if starters:
        lines = ["# Conversation Starters", "", "Example prompts the agent advertises to users.", ""]
        for s in starters:
            title = s.get("title", "")
            text = s.get("text", "")
            lines.append(f"- **{title}**: {text}" if title else f"- {text}")
        writer.add_knowledge("conversation-starters.md", "\n".join(lines))
        report.map(f"'conversation_starters' -> knowledge/conversation-starters.md ({len(starters)} item(s))")

    editorial = manifest.get("editorial_answers", {}).get("answers", [])
    if editorial:
        lines = ["# Editorial Answers", "", "Predefined question/answer pairs from the source manifest.", ""]
        for a in editorial:
            lines.append(f"**Q:** {a.get('question', '')}")
            lines.append(f"**A:** {a.get('answer', '')}")
            lines.append("")
        writer.add_knowledge("editorial-answers.md", "\n".join(lines))
        report.map(f"'editorial_answers' -> knowledge/editorial-answers.md ({len(editorial)} pair(s))")

    safety_lines = []
    disclaimer = manifest.get("disclaimer", {}).get("text")
    if disclaimer:
        safety_lines.append(f"## Disclaimer shown to users\n\n{disclaimer}")
        report.map("'disclaimer' -> instructions/safety.md")

    overrides = manifest.get("behavior_overrides", {})
    special = overrides.get("special_instructions", {})
    if special.get("discourage_model_knowledge"):
        safety_lines.append(
            "## Model knowledge\n\nDo not rely on model/world knowledge when generating responses; "
            "ground every answer in retrieved/connected data only."
        )
        report.map("'behavior_overrides.special_instructions.discourage_model_knowledge' -> instructions/safety.md")
    if overrides.get("suggestions", {}).get("disabled"):
        safety_lines.append("## Suggestions\n\nDo not proactively suggest follow-up prompts.")
        report.map("'behavior_overrides.suggestions.disabled' -> instructions/safety.md")

    if safety_lines:
        writer.add_instruction_file("safety.md", "# Safety & Behavior\n\n" + "\n\n".join(safety_lines))

    # Config / orchestration fields with no clean AgentDef target: preserve
    # losslessly as custom runtime fields rather than silently dropping them.
    runtime_extra = {}
    for field in ("worker_agents", "user_overrides", "sensitivity_label", "behavior_overrides"):
        if field in manifest:
            runtime_extra[f"x-m365-{field}"] = manifest[field]
            report.drop(
                f"'{field}' has no portable AgentDef equivalent; preserved verbatim in runtime/config.yaml"
            )
    response_mode = overrides.get("default_response_mode")
    if response_mode:
        runtime_extra["x-m365-default-response-mode"] = response_mode
    if runtime_extra:
        writer.set_runtime(runtime_extra)

    writer.set_extra_manifest({
        "x-imported-from": {
            "framework": "m365-copilot",
            "schema_version": manifest.get("version"),
            "source_file": str(src),
        }
    })

    return writer.write(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import a Microsoft 365 Copilot declarative agent manifest into an AgentDef directory."
    )
    parser.add_argument("source", help="Path to declarativeAgent.json (or equivalent manifest file).")
    parser.add_argument("--output", "-o", required=True, help="Output AgentDef directory.")
    parser.add_argument("--name", default=None, help="Override the inferred agent name.")
    args = parser.parse_args()

    out = import_m365copilot(args.source, args.output, args.name)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")
    print("Next: python validation/validate.py", out)


if __name__ == "__main__":
    main()
