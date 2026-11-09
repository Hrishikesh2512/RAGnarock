#!/usr/bin/env python3
"""Validate the event issue manifest before publishing.

Run from the repository root:

    python3 scripts/validate_issues.py
    python3 scripts/validate_issues.py --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "planning" / "issues.yml"
EXPECTED_TOTAL = 150
EXPECTED_PER_SET = 50
SET_SLUGS = {"set-1", "set-2", "set-3"}
DIFFICULTIES = {"beginner", "intermediate", "advanced"}
AREAS = {"docs", "backend", "frontend", "infra", "test", "design", "accessibility"}
TITLE_PREFIXES = ("docs:", "test:", "backend:", "frontend:", "infra:", "design:", "ci:")

errors: list[str] = []
warnings: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load() -> dict:
    if not MANIFEST.exists():
        error(f"manifest not found: {MANIFEST}")
        return {}
    try:
        data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        error(f"invalid YAML: {exc}")
        return {}
    if not isinstance(data, dict):
        error("manifest must be a mapping with an `issues` key")
        return {}
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    data = load()
    issues = data.get("issues", [])
    if not isinstance(issues, list):
        error("`issues` must be a list")
        issues = []

    if data.get("total_issues") != EXPECTED_TOTAL:
        error(f"total_issues must be {EXPECTED_TOTAL}, got {data.get('total_issues')!r}")
    if len(issues) != EXPECTED_TOTAL:
        error(f"expected {EXPECTED_TOTAL} issues, found {len(issues)}")

    set_counts = Counter()
    ids: dict[str, dict] = {}
    titles: dict[str, str] = {}
    file_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for index, issue in enumerate(issues, start=1):
        label = issue.get("id") or f"issue #{index}"
        if not isinstance(issue, dict):
            error(f"{label}: issue must be a mapping")
            continue

        issue_id = issue.get("id")
        if not isinstance(issue_id, str) or not re.fullmatch(r"set[123]-\d{2}", issue_id):
            error(f"{label}: id must look like set1-01")
        elif issue_id in ids:
            error(f"{issue_id}: duplicate id")
        else:
            ids[issue_id] = issue

        set_no = issue.get("set_number")
        set_slug = issue.get("set")
        if set_no not in (1, 2, 3):
            error(f"{label}: set_number must be 1, 2, or 3")
        if set_slug not in SET_SLUGS:
            error(f"{label}: set must be one of {sorted(SET_SLUGS)}")
        if set_no in (1, 2, 3) and set_slug != f"set-{set_no}":
            error(f"{label}: set {set_slug} does not match set_number {set_no}")
        if set_no in (1, 2, 3):
            set_counts[set_slug] += 1

        title = issue.get("title")
        if not isinstance(title, str) or len(title) < 12:
            error(f"{label}: title is missing or too short")
        elif not title.startswith(TITLE_PREFIXES):
            error(f"{label}: title must start with one of {', '.join(TITLE_PREFIXES)}")
        elif title in titles:
            error(f"{label}: duplicate title (also {titles[title]})")
        else:
            titles[title] = issue_id

        area = issue.get("area")
        if area not in AREAS:
            error(f"{label}: area must be one of {sorted(AREAS)}")
        difficulty = issue.get("difficulty")
        if difficulty not in DIFFICULTIES:
            error(f"{label}: difficulty must be one of {sorted(DIFFICULTIES)}")
        minutes = issue.get("estimated_time_minutes")
        if not isinstance(minutes, int) or not 10 <= minutes <= 240:
            error(f"{label}: estimated_time_minutes must be an integer between 10 and 240")

        labels = issue.get("labels")
        if not isinstance(labels, list) or not labels:
            error(f"{label}: labels must be a non-empty list")
        else:
            if set_slug not in labels:
                error(f"{label}: labels must include {set_slug}")
            if f"difficulty:{difficulty}" not in labels:
                error(f"{label}: labels must include difficulty:{difficulty}")
            if area not in labels:
                error(f"{label}: labels must include area {area}")
            if difficulty == "beginner" and "good first issue" not in labels:
                warn(f"{label}: beginner issue is not labelled `good first issue`")

        no_code = isinstance(labels, list) and "no-code" in labels
        if no_code:
            raw_files = issue.get("files_to_touch", [])
            if isinstance(raw_files, list):
                for path in raw_files:
                    if isinstance(path, str) and path.rsplit(".", 1)[-1] in {
                        "py",
                        "ts",
                        "tsx",
                        "js",
                        "jsx",
                    }:
                        error(f"{label}: no-code issue touches a code file: {path}")

        files = issue.get("files_to_touch")
        new_files = issue.get("new_files", [])
        if not isinstance(files, list) or not files:
            error(f"{label}: files_to_touch must be a non-empty list")
            files = []
        if not isinstance(new_files, list):
            error(f"{label}: new_files must be a list")
            new_files = []
        for path in files:
            if not isinstance(path, str) or not path:
                error(f"{label}: invalid file path {path!r}")
                continue
            if path not in new_files and not (ROOT / path).exists():
                error(f"{label}: file does not exist and is not listed in new_files: {path}")
            if set_slug:
                file_counts[set_slug][path] += 1
        for path in new_files:
            if path not in files:
                error(f"{label}: new_files entry is not in files_to_touch: {path}")
            if (ROOT / path).exists():
                error(f"{label}: new_files entry already exists: {path}")

        steps = issue.get("steps")
        if not isinstance(steps, list) or len(steps) < 3:
            error(f"{label}: steps must contain at least 3 items")
        elif any(not isinstance(step, str) or len(step) < 10 for step in steps):
            error(f"{label}: every step must be a useful string")

        for field in ("description", "acceptance_test", "definition_of_done"):
            value = issue.get(field)
            if not isinstance(value, str) or len(value.strip()) < 20:
                error(f"{label}: {field} is missing or too short")

        depends_on = issue.get("depends_on", [])
        if not isinstance(depends_on, list):
            error(f"{label}: depends_on must be a list")
            depends_on = []
        for dependency in depends_on:
            if dependency == issue_id:
                error(f"{label}: issue depends on itself")
            elif dependency not in ids and not any(i.get("id") == dependency for i in issues):
                error(f"{label}: dependency does not exist: {dependency}")

    if set_counts != Counter({"set-1": 50, "set-2": 50, "set-3": 50}):
        error(f"each set must contain {EXPECTED_PER_SET} issues, got {dict(set_counts)}")

    for issue in issues:
        for dependency in issue.get("depends_on", []):
            dep = ids.get(dependency)
            if dep and dep.get("set_number", 0) > issue.get("set_number", 0):
                error(
                    f"{issue.get('id')}: depends on {dependency} from a later set; "
                    "dependencies must be in the same or an earlier set"
                )

    for set_slug, counts in file_counts.items():
        for path, count in counts.items():
            if count > 2:
                warn(f"{set_slug}: {path} is touched by {count} issues; expect merge conflicts")

    # Summary
    print("Manifest:", MANIFEST.relative_to(ROOT))
    print(f"Issues: {len(issues)}")
    for set_slug in ("set-1", "set-2", "set-3"):
        set_issues = [i for i in issues if i.get("set") == set_slug]
        minutes = sum(i.get("estimated_time_minutes", 0) for i in set_issues)
        print(
            f"  {set_slug}: {len(set_issues)} issues, "
            f"{minutes} estimated contributor-minutes"
        )
    print("Areas:", dict(Counter(i.get("area") for i in issues)))
    print("Difficulty:", dict(Counter(i.get("difficulty") for i in issues)))

    if warnings:
        print("\nWarnings:")
        for message in warnings:
            print(f"  - {message}")
    if errors:
        print("\nErrors:", file=sys.stderr)
        for message in errors:
            print(f"  - {message}", file=sys.stderr)
        return 1
    if args.strict and warnings:
        print("\nStrict mode: warnings are errors.", file=sys.stderr)
        return 1
    print("\nOK: manifest is ready to publish.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
