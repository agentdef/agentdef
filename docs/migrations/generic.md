# Import any prompt file into AgentDef

Works for any markdown system prompt or persona file.

```bash
pip install agentdef

# 1. Import — everything unrecognized lands in instructions/core.md,
#    nothing is dropped silently:
agentdef import generic SYSTEM.md --output ./my-agent

# 2. Read what happened (mapped / inferred / dropped, item by item):
cat ./my-agent/IMPORT_REPORT.md

# 3. Verify:
agentdef validate ./my-agent

# 4. Generate your original file back — plus any other framework:
agentdef adapt generic ./my-agent --output SYSTEM.md
agentdef adapt copilot ./my-agent --output .github/copilot-instructions.md
```

From here, add a `sync:` block to `manifest.yaml` and run `agentdef sync`
whenever the canonical definition changes ([README](../getting-started.md)).
