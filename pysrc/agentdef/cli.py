#!/usr/bin/env python3
"""agentdef — command-line interface for the AgentDef toolkit.

Subcommands:
    agentdef validate <agent-dir>
    agentdef adapt <framework> <agent-dir> [--output FILE]
    agentdef import <framework> <source-file> --output <agent-dir> [--name NAME]
    agentdef list
"""

from __future__ import annotations

import argparse
import importlib
import sys

from agentdef.registry import ADAPTERS, IMPORTERS


def cmd_validate(args: argparse.Namespace) -> int:
    from agentdef.validation.validate import validate

    result = validate(args.agent_dir)
    print(result.summary())
    return 0 if result.valid else 1


def cmd_adapt(args: argparse.Namespace) -> int:
    spec = ADAPTERS[args.framework]
    mod = importlib.import_module(spec.module)
    agent = mod.AgentDef(args.agent_dir)
    result = mod.generate(agent)
    mod.write_output(result, args.output)
    if args.output:
        print(f"Wrote {spec.output_name} -> {args.output}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    spec = IMPORTERS[args.framework]
    mod = importlib.import_module(spec.module)
    import_fn = getattr(mod, spec.entrypoint)

    kwargs = {"name": args.name} if args.name else {}
    if args.framework == "copilot" and args.instructions_dir:
        kwargs["instructions_dir"] = args.instructions_dir

    out = import_fn(args.source, args.output, **kwargs)
    print(f"Imported AgentDef agent written to: {out}")
    print(f"Import report: {out / 'IMPORT_REPORT.md'}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    from agentdef.init import init_agent

    try:
        root = init_agent(
            args.directory,
            name=args.name,
            role=None,
            frameworks=args.frameworks.split(",") if args.frameworks else None,
            yes=args.yes,
        )
    except (FileExistsError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(f"Created AgentDef agent at {root}")
    print("Next: agentdef validate " + str(root))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    from agentdef.sync import SyncError, sync

    try:
        changed, same = sync(args.agent_dir, check=args.check)
    except SyncError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    for path in same:
        print(f"up to date: {path}")
    for path in changed:
        print(("STALE: " if args.check else "wrote: ") + path)
    if args.check and changed:
        print(f"{len(changed)} output(s) out of sync — run `agentdef sync` and commit.", file=sys.stderr)
        return 1
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    print("Adapters (AgentDef -> framework file):")
    for fw, spec in ADAPTERS.items():
        print(f"  {fw:<14} -> {spec.output_name}")
    print("\nImporters (framework file -> AgentDef):")
    for fw, spec in IMPORTERS.items():
        print(f"  {fw:<14} <- {spec.source_desc}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentdef",
        description="Validate, adapt, and import portable AI agent definitions.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate an AgentDef agent directory.")
    p_validate.add_argument("agent_dir", help="Path to the AgentDef agent directory.")
    p_validate.set_defaults(func=cmd_validate)

    p_adapt = sub.add_parser("adapt", help="Generate a framework-specific file from an AgentDef agent.")
    p_adapt.add_argument("framework", choices=sorted(ADAPTERS), help="Target framework.")
    p_adapt.add_argument("agent_dir", help="Path to the AgentDef agent directory.")
    p_adapt.add_argument("--output", "-o", default=None, help="Output file path (default: stdout).")
    p_adapt.set_defaults(func=cmd_adapt)

    p_import = sub.add_parser("import", help="Import a framework-specific agent file into AgentDef.")
    p_import.add_argument("framework", choices=sorted(IMPORTERS), help="Source framework.")
    p_import.add_argument("source", help="Path to the framework-specific source file.")
    p_import.add_argument("--output", "-o", required=True, help="Output AgentDef directory.")
    p_import.add_argument("--name", default=None, help="Override the inferred agent name.")
    p_import.add_argument(
        "--instructions-dir",
        default=None,
        help="(copilot only) Path to .github/instructions/ with path-scoped *.instructions.md files.",
    )
    p_import.set_defaults(func=cmd_import)

    p_init = sub.add_parser("init", help="Scaffold a new AgentDef agent directory.")
    p_init.add_argument("directory", help="Directory to create the agent in.")
    p_init.add_argument("--name", default=None, help="Agent name (default: directory name).")
    p_init.add_argument("--frameworks", default=None, help="Comma-separated sync targets (e.g. claude,copilot).")
    p_init.add_argument("--yes", "-y", action="store_true", help="Non-interactive; accept defaults.")
    p_init.set_defaults(func=cmd_init)

    p_sync = sub.add_parser("sync", help="Regenerate all framework files configured under 'sync' in manifest.yaml.")
    p_sync.add_argument("agent_dir", help="Path to the AgentDef agent directory.")
    p_sync.add_argument("--check", action="store_true", help="Write nothing; exit 1 if any output is stale.")
    p_sync.set_defaults(func=cmd_sync)

    p_list = sub.add_parser("list", help="List available adapter and importer frameworks.")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
