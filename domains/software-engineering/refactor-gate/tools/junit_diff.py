"""Diff two pytest junit files by failing-test set (not by failure count).

Usage:
    python records/streamline/tools/junit_diff.py base.xml after.xml

Prints per-run totals plus the symmetric difference. `identical: True` is the
only result that proves a refactor added no regression; comparing the raw
number of failures hides environment drift (symlink privileges, WMI, bash).
"""
import sys
import xml.etree.ElementTree as ET


def failures(path):
    root = ET.parse(path).getroot()
    out = set()
    counts = {}
    for suite in root:
        for key in ("tests", "failures", "errors", "skipped"):
            counts[key] = counts.get(key, 0) + int(suite.get(key) or 0)
        for case in suite:
            if any(child.tag in ("failure", "error") for child in case):
                out.add(f"{case.get('classname')}::{case.get('name')}")
    return counts, out


def main(base_path, after_path):
    base_counts, base = failures(base_path)
    after_counts, after = failures(after_path)
    print("base :", base_counts)
    print("after:", after_counts)
    fixed = sorted(base - after)
    new = sorted(after - base)
    print(f"base-only failures (fixed/absent) = {len(fixed)}")
    for name in fixed:
        print("  FIXED/ABSENT", name)
    print(f"after-only failures (NEW) = {len(new)}")
    for name in new:
        print("  NEW", name)
    print("identical:", base == after)
    return 0 if not new else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
