#!/usr/bin/env python3
"""Score an AAW capability router against the fixed router-calibration set.

Usage:
    python tools/run_router_eval.py --aaw /path/to/Adaptive-Agent-Workflow [--label v0.7.0]
    python tools/run_router_eval.py --aaw ... --bilingual-triggers   # remedy run

The fixture is copied into a temporary project so the run never reads the
machine's installed Skills. `--aaw` selects the router implementation under
test; the fixture and the prompt set stay identical across versions.

Requires PyYAML.
"""
import argparse
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

PACK = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS = PACK / "fixtures" / "skills"
DEFAULT_PROMPTS = PACK / "fixtures" / "prompts.yaml"
DEFAULT_TRIGGERS = PACK / "fixtures" / "bilingual-triggers.yaml"


def load_router(aaw):
    path = Path(aaw) / "skills" / "adaptive-agent-workflow" / "scripts" / "capability_index.py"
    if not path.is_file():
        raise SystemExit(f"capability_index.py not found under {aaw}")
    spec = importlib.util.spec_from_file_location("router_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def patch_triggers(skill_md, extra):
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    merged = False
    for index, line in enumerate(lines):
        if line.startswith("triggers:"):
            existing = [item.strip() for item in line.split(":", 1)[1].strip().strip("[]").split(",") if item.strip()]
            additions = [item for item in extra if item not in existing]
            lines[index] = "triggers: [" + ", ".join(existing + additions) + "]"
            merged = True
            break
    if not merged:
        for index, line in enumerate(lines):
            if line.startswith("name:"):
                lines.insert(index + 1, "triggers: [" + ", ".join(extra) + "]")
                break
    skill_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_project(skills_dir, extra_triggers):
    project = Path(tempfile.mkdtemp(prefix="router-eval-"))
    for skill_dir in sorted(Path(skills_dir).iterdir()):
        if not (skill_dir / "SKILL.md").is_file():
            continue
        shutil.copytree(skill_dir, project / "skills" / skill_dir.name)
    if extra_triggers:
        for name, triggers in extra_triggers.items():
            skill_md = project / "skills" / name / "SKILL.md"
            if skill_md.is_file():
                patch_triggers(skill_md, triggers)
    return project


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aaw", required=True, help="Adaptive-Agent-Workflow checkout to test")
    parser.add_argument("--skills", default=str(DEFAULT_SKILLS))
    parser.add_argument("--prompts", default=str(DEFAULT_PROMPTS))
    parser.add_argument("--bilingual-triggers", action="store_true",
                        help="apply fixtures/bilingual-triggers.yaml before indexing")
    parser.add_argument("--label", default="", help="label printed in the header")
    parser.add_argument("--limit", type=int, default=2)
    args = parser.parse_args()

    router = load_router(args.aaw)
    extra = yaml.safe_load(DEFAULT_TRIGGERS.read_text(encoding="utf-8")) if args.bilingual_triggers else None
    project = build_project(args.skills, extra)
    manifest = router.write_capabilities_index(project, include_home=False)
    cases = yaml.safe_load(Path(args.prompts).read_text(encoding="utf-8"))["cases"]

    print(f"label: {args.label or 'unlabeled'}")
    print(f"router: {Path(args.aaw).resolve()}")
    print(f"skills: {len(manifest['skills'])}; prompts per language: {sum(1 for c in cases for k in ('zh', 'en') if c.get(k))}")
    print()

    stats = {"zh": [0, 0, 0, 0, 0], "en": [0, 0, 0, 0, 0]}  # positives, hit1, hit2, negatives, fp
    for case in cases:
        expected = set(case.get("expected") or [])
        for lang in ("zh", "en"):
            prompt = case.get(lang)
            if not prompt:
                continue
            matches = router.match_skills(prompt, manifest, limit=args.limit)
            names = [match["name"] for match in matches]
            scores = [match["match_score"] for match in matches]
            row = stats[lang]
            if expected:
                row[0] += 1
                if names[:1] and names[0] in expected:
                    row[1] += 1
                if set(names) & expected:
                    row[2] += 1
                verdict = "HIT1" if names[:1] and names[0] in expected else ("HIT2" if set(names) & expected else "MISS")
            else:
                row[3] += 1
                if names:
                    row[4] += 1
                verdict = "FP" if names else "ok"
            print(f"{lang} {case['id']:15s} {verdict:5s} {names} {scores}")
    print()
    grand = [0, 0, 0, 0, 0]
    for lang, row in stats.items():
        grand = [a + b for a, b in zip(grand, row)]
        positives, hit1, hit2, negatives, fp = row
        print(f"{lang}: top1 {hit1}/{positives} | top2 {hit2}/{positives} | negative FP {fp}/{negatives}")
    positives, hit1, hit2, negatives, fp = grand
    print(f"all: top1 {hit1}/{positives} | top2 {hit2}/{positives} | negative FP {fp}/{negatives}")


if __name__ == "__main__":
    main()
