# AgentDef for VS Code (v0)

- `manifest.yaml` / `tools/mcp.yaml`: completion + diagnostics from the
  AgentDef JSON Schemas (through redhat.vscode-yaml).
- `agent.md`: warning when the required Role section is missing.
- Commands: **AgentDef: Validate / Sync / Adapt** (shell out to the
  `agentdef` CLI — `pip install agentdef`).

## Development / packaging (maintainer steps, need npm + network)

```bash
npm install -g @vscode/vsce
vsce package          # -> agentdef-vscode-0.1.0.vsix
code --install-extension agentdef-vscode-0.1.0.vsix
```

Integration tests (@vscode/test-electron) and the Marketplace listing are
tracked in TASKS.md P4.4; the manual verification checklist:
1. Open a folder with an AgentDef agent -> manifest.yaml gets schema hints.
2. Delete the Role section from agent.md -> warning appears; restore -> gone.
3. Run each command from the palette; terminal shows CLI output.
