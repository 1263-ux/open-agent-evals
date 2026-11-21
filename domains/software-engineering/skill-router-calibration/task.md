# Task — local Skill routing under a fixed fixture

## What is being evaluated

A deterministic, local router that receives the user prompt and an index of installed Skills,
and returns up to two candidate Skills to mount. The question is not whether the router is
clever; it is whether it picks the right Skill when one exists, and stays silent when none does.

Two failure modes matter, and they are not symmetric:

- **A miss** wastes a capability the user already installed.
- **A false positive** puts an unrelated Skill into the prompt, where its rules can contradict
  the actual task. This is the more expensive error, so negatives are scored separately.

## Inputs the evaluator supplies

| Input | Notes |
| --- | --- |
| `fixtures/skills/` | 12 Skills copied into a temporary project; the machine's installed Skills are never read |
| `fixtures/prompts.yaml` | 18 cases (11 positive, 7 negative) with Chinese and/or English prompts |
| `tools/run_router_eval.py` | Copies the fixture, indexes it with the router under test, prints every verdict |
| A router checkout | `--aaw /path/to/Adaptive-Agent-Workflow`; record its commit |

`fixtures/bilingual-triggers.yaml` is a separate remedy run, not part of the base comparison:
it adds declared triggers to three Skills to measure the documented fix for cross-language
routing.

## How the result is judged

Record the per-prompt table and the summary counts. Report:

- top-1 and top-2 hit rate over positive prompts, per language;
- false positives over negative prompts, per language;
- every miss by name, and every wrong Skill returned.

Do not merge the hit rate and the false-positive rate into one number. `rubric.yaml` v0.1
requires replayability as the only hard gate.

## Known traps (observed while building this fixture)

- **Cross-language routing does not exist.** A Chinese prompt shares no token with an
  English-only description. Either the Skill declares Chinese `triggers` or it cannot match.
- **One description word is not enough.** Two description words, a name word, a `trigger`, or
  a name mention route; one generic description word does not.
- **Substring matching produces confident nonsense.** An unanchored `cli` trigger fires on
  `click`; an unanchored `vision` name fires on `television`.
- **Frontmatter dialects matter.** `description: >-` is valid YAML. A parser that stores the
  literal `>-` removes the Skill from routing without an error.
- **The fixture is small and authored here.** It measures regressions and failure modes; it is
  not an estimate of routing quality on the open ecosystem.
