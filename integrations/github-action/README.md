# AgentDef GitHub Action

Validates AgentDef agents and fails CI when generated framework files drift
from the canonical definition.

```yaml
# .github/workflows/agentdef.yml
on: [push, pull_request]
jobs:
  agentdef:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - uses: agentdef/agentdef/integrations/github-action@main
        with:
          agent-dirs: ".agentdef agents/support-bot"
```

Publishing to the Marketplace as `agentdef/agentdef-action@v1` requires
moving this directory to its own repo (maintainer step; see RELEASING.md).
The P4.2 fixture-repo verification (red on hand-edited drift, green after
`agentdef sync`) also happens post-publish.
