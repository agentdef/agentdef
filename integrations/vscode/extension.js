// AgentDef VS Code extension (v0, P4.4).
// - manifest.yaml completion/diagnostics come from the yamlValidation
//   contribution (via redhat.vscode-yaml).
// - agent.md Role lint: warn when no `# Role`/`## Role` header exists.
// - Commands shell out to the `agentdef` CLI (pip install agentdef).
const vscode = require("vscode");

function agentDirFor(uri) {
  const folder = vscode.workspace.getWorkspaceFolder(uri);
  return folder ? folder.uri.fsPath : require("path").dirname(uri.fsPath);
}

function runCli(args, cwd) {
  const term = vscode.window.createTerminal({ name: "agentdef", cwd });
  term.show();
  term.sendText(`agentdef ${args}`);
}

const ROLE_RE = /^##? {1,3}role\b/im;

function lintAgentMd(doc, collection) {
  if (!doc.fileName.endsWith("agent.md")) return;
  if (ROLE_RE.test(doc.getText())) {
    collection.set(doc.uri, []);
    return;
  }
  const diag = new vscode.Diagnostic(
    new vscode.Range(0, 0, 0, 1),
    "agent.md must contain a '# Role' or '## Role' section (AgentDef conformance rule 1).",
    vscode.DiagnosticSeverity.Warning
  );
  diag.source = "agentdef";
  collection.set(doc.uri, [diag]);
}

function activate(context) {
  const diagnostics = vscode.languages.createDiagnosticCollection("agentdef");
  context.subscriptions.push(diagnostics);
  vscode.workspace.onDidOpenTextDocument((d) => lintAgentMd(d, diagnostics), null, context.subscriptions);
  vscode.workspace.onDidChangeTextDocument((e) => lintAgentMd(e.document, diagnostics), null, context.subscriptions);
  vscode.workspace.textDocuments.forEach((d) => lintAgentMd(d, diagnostics));

  context.subscriptions.push(
    vscode.commands.registerCommand("agentdef.validate", () => {
      const ed = vscode.window.activeTextEditor;
      if (ed) runCli(`validate "${agentDirFor(ed.document.uri)}"`, agentDirFor(ed.document.uri));
    }),
    vscode.commands.registerCommand("agentdef.sync", () => {
      const ed = vscode.window.activeTextEditor;
      if (ed) runCli(`sync "${agentDirFor(ed.document.uri)}"`, agentDirFor(ed.document.uri));
    }),
    vscode.commands.registerCommand("agentdef.adapt", async () => {
      const fw = await vscode.window.showQuickPick(
        ["claude", "openai", "cursor", "copilot", "langgraph", "m365copilot", "assistants", "crewai"],
        { placeHolder: "Target framework" }
      );
      const ed = vscode.window.activeTextEditor;
      if (fw && ed) {
        const dir = agentDirFor(ed.document.uri);
        runCli(`adapt ${fw} "${dir}"`, dir);
      }
    })
  );
}

function deactivate() {}
module.exports = { activate, deactivate };
