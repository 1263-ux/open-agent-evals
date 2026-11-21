# Tooling

Do not build a general evaluation platform yet. Add small tools only when repeated experiments demonstrate stable needs.

Current tools:

- `build_catalog.py` — regenerates `catalog.yaml` from `domains/*/*/pack.yaml`, `experiments/*/experiment.yaml`, `methods/**/method.yaml` and `models/*/profile.yaml`. `--check` fails when the committed catalog is stale.
- `validate.py` — enforces the field conventions, identifier uniqueness, referential integrity (rubric files, gate tools, fixtures, experiment evidence, experiment-to-pack versions) and catalog freshness. CI runs this on every push and pull request.

Requires PyYAML. After changing any asset, run:

```bash
python tooling/build_catalog.py
python tooling/validate.py
```

Planned, only when a real need appears: result aggregation, regression runner, visualization.
