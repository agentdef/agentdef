# Contributing to AgentDef

Thank you for your interest in contributing to AgentDef.

## How to Contribute

### Reporting Issues

Open an issue on GitHub for bugs, unclear spec language, or feature requests. Please include enough context to reproduce the problem or understand the suggestion.

### Proposing Changes

1. Fork the repository.
2. Create a branch from `main`.
3. Make your changes.
4. Run validation: `agentdef validate examples/twitter-digest examples/mission-writer` and tests: `python -m pytest validation/tests importers/tests -v`
5. Submit a pull request with a clear description of what changed and why.

### What We're Looking For

- Spec clarifications and improvements
- New examples that demonstrate real use cases
- Framework adapters and importers for platforms not yet covered
- Validation improvements
- Documentation fixes

### Guidelines

- All content must be in English.
- Examples must be valid AgentDef agents (pass validation).
- Keep changes focused — one concern per pull request.
- Follow the existing file and directory naming conventions.

## Code of Conduct

Be respectful and constructive. We want AgentDef to be a welcoming project for everyone.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
