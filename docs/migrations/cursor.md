# Move your Cursor rules to AgentDef in 5 minutes

Works for cursor-rules.md, legacy .cursorrules, and .mdc rules (globs/alwaysApply preserved as x-cursor).

```bash
pip install agentdef

# 1. Import — everything unrecognized lands in instructions/core.md,
#    nothing is dropped silently:
agentdef import cursor .cursor/rules/api.mdc --output ./my-agent

# 2. Read what happened (mapped / inferred / dropped, item by item):
cat ./my-agent/IMPORT_REPORT.md

# 3. Verify:
agentdef validate ./my-agent

# 4. Generate your original file back — plus any other framework:
agentdef adapt cursor ./my-agent --output .cursor/rules/api.mdc
agentdef adapt copilot ./my-agent --output .github/copilot-instructions.md
```

From here, add a `sync:` block to `manifest.yaml` and run `agentdef sync`
whenever the canonical definition changes ([README](../getting-started.md)).
