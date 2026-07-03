# Move your copilot-instructions.md to AgentDef in 5 minutes

Works for repo instructions and *.agent.md custom agents.

```bash
pip install agentdef

# 1. Import — everything unrecognized lands in instructions/core.md,
#    nothing is dropped silently:
agentdef import copilot .github/copilot-instructions.md --output ./my-agent

# 2. Read what happened (mapped / inferred / dropped, item by item):
cat ./my-agent/IMPORT_REPORT.md

# 3. Verify:
agentdef validate ./my-agent

# 4. Generate your original file back — plus any other framework:
agentdef adapt copilot ./my-agent --output .github/copilot-instructions.md
agentdef adapt copilot ./my-agent --output .github/copilot-instructions.md
```

From here, add a `sync:` block to `manifest.yaml` and run `agentdef sync`
whenever the canonical definition changes ([README](../getting-started.md)).
