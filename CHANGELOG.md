# Changelog

## 0.2.0-draft — 2026-11-21
- Add `catalog.yaml`: a machine-readable index of every pack, experiment record, method and capability profile. It is the cross-repository contract; consumers read it at a pinned Git ref and never parse pack internals.
- Add `tooling/build_catalog.py` and `tooling/validate.py`: field presence, identifier uniqueness, rubric/tool/fixture/evidence referential integrity, experiment-to-pack version resolution (including superseded versions listed in `provenance.change_log`), and catalog freshness.
- Add CI (`Asset checks`) running the validator on every push and pull request. The YAML files in `specifications/` remain field conventions; the validator is what enforces them.
- Add `LICENSE-CODE` (MIT, executable code) and `LICENSE-CONTENT` (CC BY 4.0, documentation, packs, rubrics, records, templates and authored fixtures).
- Fix `maintenance-task/pack.yaml`: `evaluation.rubric.version` said `0.2` while the rubric file declared `0.1`.
- Add `methods/` and `reports/` placeholders so the documented structure matches the tree.

## 0.1.1-draft — 2026-11-14
- Align Method Card specification and template fields, including maintenance metadata.
- Clarify that YAML specification files are human-readable field conventions, not formal machine-validation schemas.
- Add a runnable Java 17 / Maven maintenance task fixture with a known failing baseline and acceptance rubric.
- Add the missing game Evaluation Pack manifest while explicitly keeping its rubric uncalibrated.
- Clarify Public visibility versus copyright/license permissions.
- Link the companion Adaptive Agent Workflow repository in both project READMEs.
- No controlled model/workflow comparison has been completed yet.

## 0.1.0-draft — 2026-11-14
- Initialize Evaluation / Method / Experiment / Capability Profile asset models.
- Add evaluation protocol, governance and method promotion rules.
- Add initial domain evaluation pack drafts.
