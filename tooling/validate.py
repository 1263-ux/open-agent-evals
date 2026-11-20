#!/usr/bin/env python3
"""Validate asset files and the generated catalog.

Checks field presence, identifier uniqueness, referential integrity (rubric
tools, fixtures, experiment evidence) and catalog freshness. The YAML files in
specifications/ are field conventions, not schemas; this script is the part
that actually enforces them.

Usage:
    python tooling/validate.py
"""
import re
import sys
from pathlib import Path

import yaml

import build_catalog

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+")
PACK_STATUS = {"draft", "active", "maintained", "deprecated"}
METHOD_STATUS = {"proposed", "experimental", "verified", "recommended", "deprecated"}

errors = []
warnings = []


def error(path, message):
    errors.append(f"{path.relative_to(ROOT).as_posix()}: {message}")


def warn(path, message):
    warnings.append(f"{path.relative_to(ROOT).as_posix()}: {message}")


def load(path):
    try:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        error(path, f"YAML parse failed: {exc}")
        return None
    if not isinstance(data, dict):
        error(path, "top level is not a mapping")
        return None
    return data


def require(path, data, keys):
    for key in keys:
        value = data.get(key)
        if key not in data or value in (None, "", [], {}):
            error(path, f"missing or empty field: {key}")


def check_pack(path, data):
    require(
        path,
        data,
        [
            "schema_version",
            "kind",
            "id",
            "title",
            "domain",
            "version",
            "status",
            "language",
            "summary",
            "task",
            "evaluation",
            "provenance",
        ],
    )
    if data.get("kind") != "evaluation-pack":
        error(path, f"kind is {data.get('kind')!r}, expected 'evaluation-pack'")
    if data.get("status") not in PACK_STATUS:
        error(path, f"status {data.get('status')!r} not in {sorted(PACK_STATUS)}")
    if not SEMVER.match(str(data.get("version") or "")):
        error(path, f"version {data.get('version')!r} is not semver")

    base = path.parent
    evaluation = data.get("evaluation") or {}
    rubric_ref = evaluation.get("rubric") or {}
    rubric_path = base / rubric_ref["path"] if rubric_ref.get("path") else None
    if not rubric_path:
        error(path, "evaluation.rubric.path missing")
    elif not rubric_path.is_file():
        error(path, f"rubric file not found: {rubric_ref['path']}")
    else:
        rubric = load(rubric_path)
        if rubric:
            if rubric.get("rubric_version") != rubric_ref.get("version"):
                error(
                    path,
                    f"evaluation.rubric.version {rubric_ref.get('version')!r} "
                    f"!= rubric file rubric_version {rubric.get('rubric_version')!r}",
                )
            if not rubric.get("dimensions"):
                error(rubric_path, "no dimensions")
            for dim in rubric.get("dimensions") or []:
                if not dim.get("hard_gate"):
                    continue
                tool = dim.get("tool")
                if isinstance(tool, str) and tool.endswith(".py") and not (base / tool).is_file():
                    error(path, f"hard gate {dim.get('id')} tool not found: {tool}")
                anchors = dim.get("anchors") or {}
                if not anchors.get(3) and not anchors.get("3"):
                    error(rubric_path, f"hard gate {dim.get('id')} has no anchor 3")

    if not evaluation.get("hard_constraints"):
        error(path, "evaluation.hard_constraints is empty")
    if not evaluation.get("failure_conditions"):
        error(path, "evaluation.failure_conditions is empty")

    for tool in (data.get("execution") or {}).get("tools") or []:
        if isinstance(tool, str) and tool.endswith(".py") and not (base / tool).is_file():
            error(path, f"execution tool not found: {tool}")

    for item in (data.get("inputs") or {}).get("fixtures") or []:
        if isinstance(item, str):
            if "/" not in item:
                if data.get("status") != "draft":
                    warn(path, f"fixture is a placeholder in a non-draft pack: {item}")
                continue
            if not (base / item).exists():
                error(path, f"fixture path not found: {item}")
        elif isinstance(item, dict):
            if item.get("bundled") and item.get("path") and not (base / item["path"]).exists():
                error(path, f"bundled fixture path not found: {item['path']}")
            if isinstance(item.get("bundled"), bool) and item["bundled"] and not item.get("license"):
                warn(path, f"bundled fixture {item.get('id')!r} has no license field")


def check_experiment(path, data, pack_versions):
    require(path, data, ["schema_version", "kind", "id", "title", "date", "type", "status", "evaluation", "results"])
    if data.get("kind") != "experiment-record":
        error(path, f"kind is {data.get('kind')!r}, expected 'experiment-record'")
    evaluation = data.get("evaluation") or {}
    pack_id = evaluation.get("pack_id")
    if not pack_id:
        error(path, "evaluation.pack_id missing")
    elif pack_id not in pack_versions:
        error(path, f"evaluation.pack_id {pack_id!r} does not match any pack")
    elif evaluation.get("pack_version") not in pack_versions[pack_id]:
        # A historical record may name a superseded version, but the pack must
        # still account for it in provenance.change_log.
        error(
            path,
            f"evaluation.pack_version {evaluation.get('pack_version')!r} "
            f"not among {sorted(pack_versions[pack_id])} (current version or change_log)",
        )
    if not (data.get("results") or {}).get("conclusion"):
        error(path, "results.conclusion missing")

    evidence = data.get("evidence") or {}
    for key in ("raw_data", "logs"):
        for item in evidence.get(key) or []:
            if not isinstance(item, str) or "/" not in item:
                continue
            if not (path.parent / item).is_file():
                error(path, f"evidence.{key} path not found: {item}")


def check_method(path, data):
    require(path, data, ["schema_version", "kind", "id", "title", "version", "status", "domain", "summary"])
    if data.get("kind") not in {"method-card", "method-asset"}:
        error(path, f"kind is {data.get('kind')!r}, expected 'method-card'")
    if data.get("status") not in METHOD_STATUS:
        error(path, f"status {data.get('status')!r} not in {sorted(METHOD_STATUS)}")
    evidence = data.get("evidence") or {}
    if not evidence.get("experiment_records"):
        warn(path, "method has no experiment records; it cannot exceed 'proposed'")


def check_profile(path, data):
    require(path, data, ["schema_version", "kind", "id", "subject", "scope"])
    if data.get("kind") != "capability-profile":
        error(path, f"kind is {data.get('kind')!r}, expected 'capability-profile'")


def main():
    seen_ids = {}
    pack_versions = {}

    for path in sorted(ROOT.glob("domains/*/*/pack.yaml")):
        data = load(path)
        if not data:
            continue
        check_pack(path, data)
        asset_id = data.get("id")
        if asset_id in seen_ids:
            error(path, f"duplicate id {asset_id!r} (also {seen_ids[asset_id]})")
        else:
            seen_ids[asset_id] = path.relative_to(ROOT).as_posix()
        known = {data.get("version")}
        for entry in (data.get("provenance") or {}).get("change_log") or []:
            match = SEMVER.match(str(entry))
            if match:
                known.add(match.group(0))
        pack_versions.setdefault(asset_id, set()).update(known)

    for path in sorted(ROOT.glob("experiments/*/experiment.yaml")):
        data = load(path)
        if data:
            check_experiment(path, data, pack_versions)
            asset_id = data.get("id")
            if asset_id in seen_ids:
                error(path, f"duplicate id {asset_id!r} (also {seen_ids[asset_id]})")
            else:
                seen_ids[asset_id] = path.relative_to(ROOT).as_posix()

    for path in sorted(ROOT.glob("methods/**/method.yaml")):
        data = load(path)
        if data:
            check_method(path, data)
            asset_id = data.get("id")
            if asset_id in seen_ids:
                error(path, f"duplicate id {asset_id!r} (also {seen_ids[asset_id]})")
            else:
                seen_ids[asset_id] = path.relative_to(ROOT).as_posix()

    for path in sorted(ROOT.glob("models/*/profile.yaml")):
        data = load(path)
        if data:
            check_profile(path, data)

    for path in sorted(ROOT.glob("specifications/*.yaml")):
        data = load(path)
        if data:
            require(path, data, ["schema_version", "kind"])

    for path in sorted(ROOT.glob("templates/**/*.yaml")):
        load(path)

    rendered = build_catalog.render(build_catalog.build())
    catalog_path = ROOT / "catalog.yaml"
    current = catalog_path.read_text(encoding="utf-8") if catalog_path.is_file() else ""
    if current != rendered:
        error(catalog_path, "catalog is stale; run: python tooling/build_catalog.py")

    for line in warnings:
        print(f"WARN  {line}")
    for line in errors:
        print(f"ERROR {line}")
    packs = len(list(ROOT.glob("domains/*/*/pack.yaml")))
    experiments = len(list(ROOT.glob("experiments/*/experiment.yaml")))
    print(f"checked {packs} packs, {experiments} experiment records: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
