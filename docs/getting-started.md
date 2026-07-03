# Getting Started with AgentDef

This guide walks you through creating your first AgentDef agent, validating it, and generating framework-specific output.

## Prerequisites

- Python 3.11+
- `pip install pyyaml jsonschema`

Every command below has a raw-script form and an equivalent `agentdef` CLI form (`pip install -e .` from this directory first). This guide uses the raw scripts since they need no install step; see the [README](https://github.com/agentdef/agentdef/blob/main/README.md#cli) for the CLI.

## 1. Copy the Starter Template

```bash
cp -r templates/starter/ my-agent/
```

You now have:

```
my-agent/
├── agent.md
├── manifest.yaml
└── instructions/
    └── core.md
```

This is the minimal valid AgentDef agent.

## 2. Define Your Agent's Identity

Edit `agent.md` to describe who your agent is:

```markdown
# Customer Support Agent

## Role
You are a customer support agent for a SaaS product. You help users troubleshoot issues, answer questions about features, and escalate complex problems.

## Objectives
- Resolve user issues quickly
- Maintain a friendly, professional tone
- Escalate when unable to resolve

## Communication Style
- empathetic
- clear
- solution-oriented

## Avoid
- technical jargon with non-technical users
- making promises about timelines
- guessing when unsure
```

## 3. Set the Manifest

Edit `manifest.yaml` to declare what modules your agent uses:

```yaml
name: customer-support

instructions:
  - instructions/core.md
```

The `name` field must be lowercase with hyphens or underscores. The `instructions` list must include at least one file.

## 4. Write Core Instructions

Edit `instructions/core.md` with the behavioral rules:

```markdown
# Core Instructions

You handle incoming support requests from users of the product.

## Processing Rules
- Greet the user and acknowledge their issue
- Ask clarifying questions before jumping to solutions
- Check the knowledge base before responding
- If unsure, say so and offer to escalate

## Tone
Friendly and professional. Match the user's level of technical detail.
```

## 5. Validate

Run the validator to check your agent:

```bash
agentdef validate my-agent/
```

Expected output:

```
PASS: /path/to/my-agent
```

If anything is wrong, the validator will tell you exactly what's missing or invalid.

## 6. Add More Modules (Optional)

As your agent grows, add skills, workflows, and other modules:

```bash
mkdir -p my-agent/skills/troubleshooting
mkdir -p my-agent/workflows
```

Create `my-agent/skills/troubleshooting/SKILL.md`:

```markdown
# Troubleshooting Skill

## Purpose
Diagnose and resolve common product issues.

## Inputs
- user description of the problem
- error messages or screenshots

## Outputs
- diagnosis
- step-by-step resolution
- escalation recommendation if unresolved
```

Update `manifest.yaml`:

```yaml
name: customer-support

instructions:
  - instructions/core.md

skills:
  - skills/troubleshooting
```

## 7. Generate Framework Output

Use an adapter to produce framework-specific files:

```bash
# For Claude
agentdef adapt claude my-agent/ --output CLAUDE.md

# For OpenAI
agentdef adapt openai my-agent/ --output AGENTS.md

# For Cursor
agentdef adapt cursor my-agent/ --output cursor-rules.md

# For Copilot
agentdef adapt copilot my-agent/ --output .github/copilot-instructions.md

# For LangGraph
agentdef adapt langgraph my-agent/ --output graph.py
```

## 8. Iterate

The typical workflow is:

1. Edit your AgentDef files
2. Validate: `agentdef validate my-agent/`
3. Generate: `agentdef adapt <framework> my-agent/`
4. Test with your target framework
5. Repeat

## Already Have an Agent in Another Framework?

If you're starting from an existing `CLAUDE.md`, `.github/copilot-instructions.md`, a Microsoft 365 Copilot `declarativeAgent.json`, or a Copilot Studio agent file, you don't need to author an AgentDef agent from scratch — use an importer to convert it automatically:

```bash
agentdef import claude CLAUDE.md --output my-agent/
```

This writes a conformant AgentDef directory plus an `IMPORT_REPORT.md` documenting what mapped cleanly, what was inferred, and what was dropped. Validate the result the same way as a hand-written agent (step 5 above). See [importers/](../importers/) for all four supported source frameworks.

## Explore the Codebase Visually

This repo also ships an interactive knowledge-graph dashboard of its own architecture — see the [Dashboard Tour](dashboard-tour.md) for how to run it and a two-minute guided path through the adapters/importers structure.

## Next Steps

- Read the [full specification](https://github.com/agentdef/agentdef/blob/main/spec/SPEC.md) for every field and module type
- Browse the [examples](../examples/) for complete, realistic agents
- Check the [FAQ](faq.md) for common questions
- See [comparisons.md](comparisons.md) for how AgentDef relates to other frameworks and adapter-based tools
