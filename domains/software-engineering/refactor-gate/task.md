# Task — CLI module extraction without behaviour change

## What is being evaluated

An Agent (or a human) claims: *"I split this monolithic CLI module into per-group modules. Nothing
observable changed."*

The gate does not score how tidy the new layout is. It scores whether the claim is **checkable** and
**true**. A split that reads beautifully but drops one `import` in a platform-specific branch is a failed
slice, because the CLI will crash on that platform and no runtime test on the evaluator's OS will say so.

## Inputs the evaluator supplies

| Input | Notes |
| --- | --- |
| Repository at its upstream baseline | Must be a clean checkout; the baseline is not negotiable |
| The command to run the full test suite | Same command must be used before and after |
| The interpreter to use | Same binary before and after; record its version |
| A list of command groups to move | One group per slice |

The evaluator must capture the baseline **before** the refactor starts: command tree, help text for each
group that will move, and one full JUnit XML. A baseline reconstructed afterwards is not accepted — it can
be, and in practice has been, quietly adjusted to match the new code.

## Slices

1. Pick one command group. Move it into its own module together with the Typer instance that owns it.
2. Keep every function body byte-for-byte identical. If a name is needed from the old module, either import
   it or add an explicit delegation shim that is clearly not a moved function.
3. Re-register the group in the original module (`app.add_typer(new_module.app, name="...")`, or
   `new_module.register(app)` for root-level commands).
4. Run the five gates on this slice. Record the result.
5. Only then start the next slice.

Do not combine a structural slice with a behaviour fix. When a structural slice exposes a real defect
(that is a normal outcome), the fix becomes its own slice with its own evidence, and the record must say
which gate caught it.

## Deliverables

- Source tree with the new module(s) and the registration change.
- `evidence/command-tree-before.txt`, `evidence/command-tree-after.txt`
- `evidence/help-<group>-before.txt`, `evidence/help-<group>-after.txt` for every moved group
- Baseline and post-change JUnit XML (referenced, not necessarily copied)
- Gate output for all five gates

## How the result is judged

`rubric.yaml` v0.2. All five hard gates must reach 3. `slice_isolation` is advisory and only moves
confidence.

Report the numbers plainly:

- command tree entries before / after, and diff line count;
- help bytes before / after per group;
- failure set: `NEW` count and the exact ids; `FIXED` count and the exact ids;
- functions checked / identical;
- undefined global names.

## Known traps (observed, not hypothetical)

- **A failure count is not evidence.** The same commit produced 14, 16, 40 and 5 failures on the same
  machine across a day because of symlink privileges, WMI availability and shell differences. Only the
  failure *set* is comparable.
- **Test order can hide a defect.** A suite that scaffolds assets in an earlier test can make a later test
  pass that fails when run alone. When a gate fails, re-run the relevant test file in isolation before
  believing the full-suite result.
- **Bytecode scan is the only gate that sees unexecuted branches.** A module moved on Windows passed the
  command tree, the help diff and the full suite while missing `import shlex` in a POSIX-only path.
- **A pre-split snapshot must come from git**, not from the working copy: `git show <base>:<path> > base.py`.
- **Installed copies shadow the source tree.** If the package is also installed into site-packages, the
  interpreter can import the old code and every gate will look clean against the wrong module. Put the
  source root first on `PYTHONPATH` and assert it by printing `module.__file__`.
