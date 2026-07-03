# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in AgentDef (the CLI, adapters,
importers, or validator), please report it privately by email to
**humbert.costas@gmail.com** with the subject line `[agentdef security]`.

Please include: a description of the issue, steps to reproduce, the affected
version (`agentdef --version` / commit hash), and any suggested fix.

You should receive an acknowledgement within 72 hours. Please do not open a
public issue for security reports until a fix is released.

## Scope notes

AgentDef's importers parse untrusted markdown/JSON files. Parsing is
deterministic (no code execution from imported content), but bugs that cause
a crafted agent file to write outside the chosen `--output` directory, or to
execute content, are in scope and considered high severity.
