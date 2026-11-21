"""Prove a moved block is verbatim: compare function bodies between two files.

Usage:
    python records/streamline/tools/block_equivalence.py BASE_FILE NEW_FILE NAME...

BASE_FILE is the pre-split file (e.g. `git show HEAD:cli/knowledge_studio/cli.py`),
NEW_FILE is the module the functions moved to. Decorators are compared
separately (only the command name/group is allowed to change), because a moved
root command gets re-registered as `app.command()(fn)`.

Exit code is 0 only when every requested function exists in both files with an
identical body, identical arguments, identical returns and identical docstring.
"""
import ast
import sys
from pathlib import Path


def load(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found[node.name] = node
    return found


def fingerprint(node):
    body = [ast.dump(stmt, annotate_fields=True, include_attributes=False) for stmt in node.body]
    args = ast.dump(node.args, annotate_fields=True, include_attributes=False)
    returns = ast.dump(node.returns, annotate_fields=True, include_attributes=False) if node.returns else ""
    return (args, returns, tuple(body))


def decorators(node):
    return [ast.unparse(d) for d in node.decorator_list]


def main(base_path, new_path, names):
    base = load(base_path)
    new = load(new_path)
    failures = 0
    for name in names:
        if name not in base:
            print(f"MISSING in base: {name}")
            failures += 1
            continue
        if name not in new:
            print(f"MISSING in new:  {name}")
            failures += 1
            continue
        same = fingerprint(base[name]) == fingerprint(new[name])
        if not same:
            failures += 1
        print(f"{'IDENTICAL' if same else 'DIFFERS  '} {name:28s} base_decor={decorators(base[name])} new_decor={decorators(new[name])}")
    print(f"functions checked: {len(names)}, not verbatim: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3:]))
