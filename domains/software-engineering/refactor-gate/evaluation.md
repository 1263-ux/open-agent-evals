# Evaluation protocol — CLI refactor gate

## 1. Freeze the baseline

```bash
BASE=<upstream sha>
git checkout --detach "$BASE"

python tools/cli_tree.py --repo <repo>/cli > evidence/command-tree-before.txt
<cli> --help                      > evidence/help-root-before.txt
<cli> <group> --help              > evidence/help-<group>-before.txt    # every group that will move
pytest <suite> --junitxml=records/baseline.xml
git show "$BASE":path/to/module.py > /tmp/base-module.py
```

Rules that make the baseline usable:

- same interpreter, same pytest command, same working directory as the post-change run;
- `PYTHONPATH` puts the source root **before** site-packages, and the run prints
  `python -c "import pkg; print(pkg.__file__)"` so the provenance of the imported code is on record;
- the pre-split file is exported from git, never copied from a working tree.

## 2. Apply one slice

Move one command group. Keep bodies identical. Re-register the group. Do not fix anything else.

## 3. Run the five gates

### Gate 1 — command tree

```bash
python tools/cli_tree.py --repo <repo>/cli > evidence/command-tree-after.txt
diff <(sort evidence/command-tree-before.txt) <(sort evidence/command-tree-after.txt)
```

Pass: empty diff. The tree is read from Typer's `registered_commands` / `registered_groups`, so it reflects
the external surface, not file layout.

### Gate 2 — help text

```bash
<cli> <group> --help > evidence/help-<group>-after.txt
cmp evidence/help-<group>-before.txt evidence/help-<group>-after.txt
```

Pass: byte-identical. Do not normalise whitespace before diffing — normalising is how an option-order or
default-rendering change slips through.

### Gate 3 — failure set

```bash
pytest <suite> --junitxml=records/after.xml
python tools/junit_diff.py records/baseline.xml records/after.xml
```

Pass: `after-only failures (NEW) = 0`. `FIXED` entries are allowed but must be explained — a structural
slice should not fix anything, so a `FIXED` entry usually means the environment changed between runs.

Never pass or fail on the failure *count*.

### Gate 4 — body equivalence

```bash
python tools/block_equivalence.py /tmp/base-module.py cli/pkg/group_cli.py fn_a fn_b ...
```

Pass: `not verbatim: 0`. The comparison covers arguments, return annotation, docstring and every body
statement via `ast.dump`, so reindentation is not a false positive and a one-character edit is not a false
negative.

Deliberate delegation shims (`def _emit_json(data): from .cli import _emit_json as emit; return emit(data)`)
are **not** moved functions. List them separately; do not count them as verbatim.

### Gate 5 — static resolution

```bash
python tools/module_globals.py --repo <repo>/cli pkg.cli pkg.group_cli pkg.other_cli ...
```

Pass: `undefined global names: 0`.

The module list must be the full set of refactored modules, not just the newest one. Shrinking the list
silently shrinks coverage, which is exactly what this gate exists to prevent.

## 4. Record

Write one experiment record per slice series. For each slice store:

- `cli_py_lines_before` / `cli_py_lines_after`
- command tree entries and diff lines
- help invocations and diff bytes
- failure set: NEW ids, FIXED ids, totals for both runs
- functions checked / identical, shims listed
- undefined global names

Add an explicit `deviations` entry whenever two slices were measured under different conditions. Slices
measured under different `PYTHONPATH` or interpreter settings are **not** comparable with each other, even
when both individually pass.

## 5. Independence

`GOVERNANCE.md` requires the evaluator to be independent of the author. A record produced by the person who
wrote the refactor is evidence, not verification: mark `confidence` accordingly and list independent replay
as a known gap until someone else reproduces the gates.
