"""Dump a Typer app's command tree as sorted "a b c" lines.

Gate 1 of the refactor gate: moving a command group into its own module must not
change the externally visible command surface. The tree is read from the Typer
objects (registered_commands / registered_groups), so it is independent of how
the modules are laid out on disk.

Usage:
    python cli_tree.py --repo /path/to/repo [--module knowledge_studio.cli]
                       [--python /path/to/python]

`--repo` must contain the importable package root (e.g. `<repo>/cli`). The
script re-execs itself under `--python` when one is given, so the caller does
not need to pre-set PYTHONPATH.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path


def walk(instance, prefix=""):
    for cmd in getattr(instance, "registered_commands", []):
        name = cmd.name or (cmd.callback.__name__.replace("_", "-") if cmd.callback else None)
        if name:
            yield f"{prefix} {name}".strip()
    for group in getattr(instance, "registered_groups", []):
        sub = group.typer_instance
        name = group.name or (sub.info.name if sub and sub.info else None)
        if not name:
            continue
        full = f"{prefix} {name}".strip()
        yield full
        yield from walk(sub, full)


def dump(package_root: Path, module_name: str) -> str:
    sys.path.insert(0, str(package_root))
    import importlib

    app = importlib.import_module(module_name).app
    return "\n".join(sorted(set(walk(app))))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Directory that contains the importable package")
    parser.add_argument("--module", default="knowledge_studio.cli")
    parser.add_argument("--python", default=None, help="Interpreter to re-exec under")
    args = parser.parse_args(argv)

    package_root = Path(args.repo).resolve()
    if args.python and Path(sys.executable).resolve() != Path(args.python).resolve():
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(package_root)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
        )
        proc = subprocess.run(
            [args.python, str(Path(__file__).resolve()), "--repo", str(package_root), "--module", args.module],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return proc.returncode

    print(dump(package_root, args.module))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
