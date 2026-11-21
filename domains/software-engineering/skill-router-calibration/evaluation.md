# Evaluation instructions

## 1. Pin the router under test

```bash
cd /path/to/Adaptive-Agent-Workflow
git rev-parse HEAD
```

To compare two versions, use a worktree for the older one instead of editing the checkout:

```bash
git worktree add /tmp/aaw-old <commit>
```

## 2. Run

From this pack directory:

```bash
python tools/run_router_eval.py --aaw /tmp/aaw-old --label "before"
python tools/run_router_eval.py --aaw /path/to/Adaptive-Agent-Workflow --label "after"
python tools/run_router_eval.py --aaw /path/to/Adaptive-Agent-Workflow \
    --bilingual-triggers --label "after + declared triggers"
```

The script copies `fixtures/skills/` into a temporary project, indexes it with `include_home=False`,
and prints one line per prompt:

```text
zh refactor        HIT1  ['refactor-gate'] [8]
en neg-click       ok    [] []
```

Then the summary:

```text
zh: top1 8/11 | top2 8/11 | negative FP 0/4
en: top1 8/10 | top2 8/10 | negative FP 0/6
all: top1 16/21 | top2 16/21 | negative FP 0/10
```

## 3. Record

Save the full output as evidence. Record the router commit, the fixture revision, the
interpreter version and the machine, then fill an experiment record (`templates/experiment-record/`).

## Reading the result

- `HIT1` — the expected Skill is rank 1.
- `HIT2` — the expected Skill is rank 2 only.
- `MISS` — the expected Skill is absent, including when a wrong Skill is rank 1.
- `FP` — a negative prompt returned at least one Skill.
- `ok` — a negative prompt returned nothing.

The remedy run changes the fixture on purpose. Do not present it as a like-for-like
improvement of the router; state that it measures declared triggers.
