"""Static check: every LOAD_GLOBAL in a module's own functions must resolve.

Why this gate exists: the command tree, the --help text and the pytest failure
set all only exercise code that actually runs. A name dropped during a module
move stays invisible on one platform when the branch using it never executes
(the reference case: `import shlex` was lost in a POSIX-only branch and every
runtime gate still passed on Windows). This scan reads bytecode, so it covers
every branch regardless of platform.

Usage:
    python module_globals.py --repo /path/to/cli knowledge_studio.cli knowledge_studio.hooks ...

`--repo` is the directory that contains the importable package (e.g. `<repo>/cli`).
Exit code is 0 only when no undefined global name is found.
"""
import argparse
import builtins
import dis
import importlib
import sys
from pathlib import Path


def check(module_name):
    module = importlib.import_module(module_name)
    namespace = vars(module)
    seen = set()
    problems = []
    for obj in list(namespace.values()):
        code = getattr(obj, "__code__", None)
        if code is None or getattr(obj, "__module__", None) != module_name:
            continue
        for ins in dis.get_instructions(code):
            if ins.opname != "LOAD_GLOBAL":
                continue
            target = ins.argval
            if target in namespace or hasattr(builtins, target) or target in seen:
                continue
            seen.add(target)
            line = ins.positions.lineno if ins.positions else "?"
            problems.append((module_name, obj.__name__, line, target))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Directory that contains the importable package")
    parser.add_argument("modules", nargs="+", help="Dotted module names to scan")
    args = parser.parse_args(argv)

    sys.path.insert(0, str(Path(args.repo).resolve()))
    found = []
    for name in args.modules:
        found.extend(check(name))
    for module_name, func, line, target in found:
        print(f"{module_name}:{func}:{line} -> {target}")
    print("undefined global names:", len(found))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
