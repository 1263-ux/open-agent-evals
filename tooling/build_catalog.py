#!/usr/bin/env python3
"""Build catalog.yaml — the machine-readable index of reusable assets.

The catalog is the cross-repository contract. An orchestrator (or a CI gate)
reads this file at a pinned git ref and never parses pack internals, so the
pack schemas stay free to change. Keep the catalog thin: identity, status,
applicability hints, gate definitions and paths to evidence.

Usage:
    python tooling/build_catalog.py            # write catalog.yaml
    python tooling/build_catalog.py --check    # fail if catalog.yaml is stale
"""
import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog.yaml"


def load_yaml(path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def rel(path):
    return path.relative_to(ROOT).as_posix()


def mapping(value):
    return value if isinstance(value, dict) else {}


def pack_entry(path):
    pack = load_yaml(path)
    base = path.parent
    rubric_ref = mapping(mapping(pack.get("evaluation")).get("rubric"))
    rubric_path = base / rubric_ref["path"] if rubric_ref.get("path") else None
    rubric = load_yaml(rubric_path) if rubric_path and rubric_path.is_file() else {}

    hard_gates = []
    for dim in rubric.get("dimensions") or []:
        if not dim.get("hard_gate"):
            continue
        anchors = mapping(dim.get("anchors"))
        hard_gates.append(
            {
                "id": dim.get("id"),
                "tool": dim.get("tool"),
                "pass": anchors.get("3", anchors.get(3)),
            }
        )
    if not hard_gates:
        for expr in rubric.get("hard_gates") or []:
            name, _, threshold = str(expr).partition(">=")
            hard_gates.append(
                {
                    "id": name.strip(),
                    "tool": None,
                    "pass": f">= {threshold.strip()}" if threshold else str(expr).strip(),
                }
            )

    fixtures = []
    for item in mapping(pack.get("inputs")).get("fixtures") or []:
        if isinstance(item, str):
            candidate = base / item
            bundled = "/" in item and candidate.exists()
            if bundled:
                fixtures.append(
                    {"id": Path(item.rstrip("/")).name, "bundled": True, "path": rel(candidate)}
                )
            else:
                fixtures.append({"bundled": False, "note": item})
        elif isinstance(item, dict):
            entry = {
                "id": item.get("id"),
                "bundled": bool(item.get("bundled")),
            }
            if item.get("path"):
                entry["path"] = (base / item["path"]).relative_to(ROOT).as_posix()
            for key in ("language", "license"):
                if item.get(key):
                    entry[key] = item[key]
            fixtures.append(entry)

    evaluator = mapping(mapping(pack.get("evaluation")).get("evaluator"))
    provenance = mapping(pack.get("provenance"))
    return {
        "kind": "evaluation-pack",
        "id": pack.get("id"),
        "version": pack.get("version"),
        "status": pack.get("status"),
        "domain": pack.get("domain"),
        "language": pack.get("language"),
        "title": pack.get("title"),
        "summary": pack.get("summary"),
        "path": rel(path),
        "instructions": (
            rel(base / mapping(pack.get("execution")).get("instructions"))
            if mapping(pack.get("execution")).get("instructions")
            and (base / mapping(pack.get("execution"))["instructions"]).is_file()
            else None
        ),
        "rubric": {
            "path": rel(rubric_path) if rubric_path and rubric_path.is_file() else None,
            "version": rubric.get("rubric_version"),
        },
        "hard_gates": hard_gates,
        "fixtures": fixtures,
        "evaluator": {
            "modes": evaluator.get("modes") or [],
            "independence_required": bool(evaluator.get("independence_required")),
        },
        "provenance": {
            "created_at": provenance.get("created_at"),
            "owners": provenance.get("owners") or [],
            "license_review": provenance.get("license_review"),
        },
    }


def experiment_entry(path):
    record = load_yaml(path)
    evaluation = mapping(record.get("evaluation"))
    results = mapping(record.get("results"))
    reproducibility = mapping(record.get("reproducibility"))
    return {
        "kind": "experiment-record",
        "id": record.get("id"),
        "title": record.get("title"),
        "date": record.get("date"),
        "type": record.get("type"),
        "status": record.get("status"),
        "pack_id": evaluation.get("pack_id"),
        "pack_version": evaluation.get("pack_version"),
        "conclusion": results.get("conclusion"),
        "confidence": results.get("confidence"),
        "replay_status": reproducibility.get("replay_status"),
        "path": rel(path),
    }


def method_entry(path):
    method = load_yaml(path)
    applicability = mapping(method.get("applicability"))
    evidence = mapping(method.get("evidence"))
    return {
        "kind": "method-asset",
        "id": method.get("id"),
        "version": method.get("version"),
        "status": method.get("status"),
        "domain": method.get("domain"),
        "title": method.get("title"),
        "summary": method.get("summary"),
        "applicability": {
            "suitable_for": applicability.get("suitable_for") or [],
            "unsuitable_for": applicability.get("unsuitable_for") or [],
        },
        "evidence": {
            "experiment_records": evidence.get("experiment_records") or [],
            "strength": evidence.get("strength"),
        },
        "path": rel(path),
    }


def profile_entry(path):
    profile = load_yaml(path)
    subject = mapping(profile.get("subject"))
    scope = mapping(profile.get("scope"))
    maintenance = mapping(profile.get("maintenance"))
    return {
        "kind": "capability-profile",
        "id": profile.get("id"),
        "subject": {
            "model": subject.get("model"),
            "model_version": subject.get("model_version"),
            "host": subject.get("host"),
        },
        "status": maintenance.get("status"),
        "task_domains": scope.get("task_domains") or [],
        "task_conditions": scope.get("task_conditions") or [],
        "path": rel(path),
    }


def build():
    assets = []
    for path in sorted(ROOT.glob("domains/*/*/pack.yaml")):
        assets.append(pack_entry(path))
    for path in sorted(ROOT.glob("experiments/*/experiment.yaml")):
        assets.append(experiment_entry(path))
    for path in sorted(ROOT.glob("methods/**/method.yaml")):
        assets.append(method_entry(path))
    for path in sorted(ROOT.glob("models/*/profile.yaml")):
        assets.append(profile_entry(path))
    assets.sort(key=lambda item: (item["kind"], str(item["id"])))
    return {"schema_version": "1", "generated_by": "tooling/build_catalog.py", "assets": assets}


def render(catalog):
    return yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False, width=100, default_flow_style=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if catalog.yaml is out of date")
    args = parser.parse_args(argv)

    rendered = render(build())
    if args.check:
        current = CATALOG.read_text(encoding="utf-8") if CATALOG.is_file() else ""
        if current != rendered:
            print("catalog.yaml is stale; run: python tooling/build_catalog.py", file=sys.stderr)
            return 1
        print("catalog.yaml is up to date")
        return 0

    CATALOG.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {rel(CATALOG)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
