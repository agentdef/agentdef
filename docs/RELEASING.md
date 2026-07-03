# Releasing AgentDef

Manual steps that require the maintainer's accounts (GitHub push, PyPI
upload). Everything else — code, tests, CI workflows, community files —
is already in the repo. Companion to TASKS.md P1.5–P1.7 and
[STATUS.md](STATUS.md).

## 0. One-time: publish the repo (P1.6)

The public repo root should be THIS directory (`agentdef/`), not its parent
working folder (which holds `downloads/`, `extras/`, and scratch). From the
parent checkout:

Pre-flight, from `agentdef/`:

```bash
python -m pytest tests -q  # expect: 239 passed
```

```bash
# Option A (recommended): fresh history for the public repo root
cd agentdef
git init -b main
git add -A
# Content audit BEFORE the first commit:
git ls-files | wc -l    # expect ~380; thousands means .gitignore isn't applying
git ls-files | grep -iE "node_modules|RUNBOOK|PUBLISHING|registration-guide|\.understand"  # expect: nothing
git commit -m "AgentDef v0.2.0 — initial public commit"
git remote add origin git@github.com:agentdef/agentdef.git
git push -u origin main
# (the agentdef/agentdef repo already exists — private, from registration day;
#  if GitHub initialized it with any file, pull --allow-unrelated-histories
#  or recreate it empty first)

# Option B: preserve full history — git filter-repo --subdirectory-filter agentdef
# (needs git-filter-repo installed; rewrites history so agentdef/ becomes root)
```

Then in GitHub repo settings — in this order:

1. Make the repo public.
2. Watch the first **CI** run (Actions tab; the matrix has never executed
   remotely). Fix on a branch if any cell is red — likely Windows/CRLF.
3. Once green: branch protection on `main` — require the CI checks to pass
   before merge, and require a pull request.
4. Verify the gate with a deliberate red PR (break one golden file in
   `adapters/tests/golden/`), confirm merge is blocked, close the PR.
5. Settings → Environments → create `pypi` (used by release.yml).
6. Settings → Pages → Source: **GitHub Actions** (used by pages.yml, which
   deploys the docs site + the architecture dashboard to
   `https://agentdef.github.io/agentdef/`).

## 1. One-time: PyPI Trusted Publishing

PyPI → project `agentdef` → Settings → Publishing → Add publisher:
org `agentdef`, repo `agentdef`, workflow `release.yml`, environment `pypi`.
After this, releases need no API tokens.

## 2. Each release (P1.7)

1. Cut CHANGELOG: move "Unreleased" items under a new `## 0.2.0 — YYYY-MM-DD`
   (leave a fresh empty `## Unreleased` above it).
2. Bump `version` in `pyproject.toml` AND `pysrc/agentdef/__init__.py` (keep
   in sync). For the first release both already say `0.2.0` — just confirm.
3. Commit, then tag and push:
   ```bash
   git tag v0.2.0
   git push && git push --tags
   ```
4. release.yml builds sdist+wheel and publishes to PyPI via Trusted Publishing.
5. Verify from a clean machine:
   ```bash
   pip install agentdef        # must resolve to 0.2.0, not the 0.0.1 placeholder
   agentdef list               # 8 adapters / 9 importers
   agentdef init smoke --yes && agentdef validate smoke && agentdef sync smoke
   pip download agentdef --no-deps -d w && python -m zipfile -l w/agentdef-0.2.0*.whl | grep -cE "adapters|importers|validation"   # > 0
   ```
6. Create a GitHub Release from the tag, pasting the CHANGELOG section.

## TestPyPI dry-run (optional but recommended for the first release)

```bash
pip install build twine
python -m build --outdir dist
twine upload -r testpypi dist/*
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple agentdef
```

## Known local quirk (not relevant in CI)

Building the wheel *inside this FUSE-mounted working folder* can fail on
`build/` cleanup (`Operation not permitted`). CI and normal filesystems are
unaffected; locally, copy `pysrc pyproject.toml README.md LICENSE` to a temp
dir and build there.
