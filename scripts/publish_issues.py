#!/usr/bin/env python3
"""Publish issues from planning/issues.yml to GitHub using the ``gh`` CLI.

Examples:
    python scripts/setup_github.py --dry-run
    python scripts/setup_github.py
    python scripts/publish_issues.py --set 1 --dry-run
    python scripts/publish_issues.py --set 1
    python scripts/publish_issues.py --area frontend --limit 5
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install it with: pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "planning" / "issues.yml"
REPO_URL = "https://github.com/bit-nodedotai/RAGnarok"


def run_gh(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        check=check,
        cwd=ROOT,
    )


def load_issues(path: Path) -> list[dict]:
    if not path.exists():
        print(f"Manifest not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    issues = data.get("issues", []) if isinstance(data, dict) else []
    if not isinstance(issues, list):
        print("Manifest must contain an `issues` list.", file=sys.stderr)
        raise SystemExit(1)
    return issues


def normalize_set(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned in {"1", "set-1", "set1"}:
        return "set-1"
    if cleaned in {"2", "set-2", "set2"}:
        return "set-2"
    if cleaned in {"3", "set-3", "set3"}:
        return "set-3"
    raise argparse.ArgumentTypeError("set must be 1, 2, 3, set-1, set-2, or set-3")


def existing_titles() -> set[str]:
    result = run_gh(
        ["issue", "list", "--state", "all", "--limit", "1000", "--json", "title"],
        check=False,
    )
    if result.returncode != 0:
        print(
            "Could not read existing issues. Run `gh auth status` and try again.\n"
            + result.stderr.strip(),
            file=sys.stderr,
        )
        raise SystemExit(1)
    return {item["title"] for item in json.loads(result.stdout or "[]")}


def check_labels(issues: list[dict]) -> None:
    result = run_gh(["label", "list", "--limit", "200", "--json", "name"], check=False)
    if result.returncode != 0:
        print("Could not read labels from GitHub.", file=sys.stderr)
        raise SystemExit(1)
    existing = {item["name"] for item in json.loads(result.stdout or "[]")}
    required = sorted({label for issue in issues for label in issue.get("labels", [])})
    missing = [label for label in required if label not in existing]
    if missing:
        print("Missing labels: " + ", ".join(missing), file=sys.stderr)
        print("Run `python3 scripts/setup_github.py` first.", file=sys.stderr)
        raise SystemExit(1)


def build_body(issue: dict) -> str:
    files = "\n".join(f"- `{path}`" for path in issue.get("files_to_touch", []))
    steps = "\n".join(
        f"{index}. {step}" for index, step in enumerate(issue.get("steps", []), start=1)
    )
    new_files = issue.get("new_files", [])
    new_note = ""
    if new_files:
        new_note = "\nThis issue creates new files: " + ", ".join(f"`{path}`" for path in new_files)

    no_code_note = ""
    if "no-code" in issue.get("labels", []):
        no_code_note = (
            "\n> **No-code track.** You do not need to write code for this issue. "
            "You will edit Markdown, YAML, CSS, or a config file. Read "
            "[the no-code track guide]"
            f"({REPO_URL}/blob/main/docs/event-no-code-track.md) before you start.\n"
        )

    return f"""## Goal

{issue.get('description', '').strip()}

## Event set

- **Set:** {issue.get('set_name', '')} (`{issue.get('set', '')}`)
- **Difficulty:** {issue.get('difficulty', '')}
- **Estimated time:** {issue.get('estimated_time', '')}
- **Area:** {issue.get('area', '')}
- **Track:** {issue.get('track', 'standard')}
{no_code_note}
## Files to touch

{files}{new_note}

## Steps

{steps}

## Acceptance test

Run this from the repository root:

```bash
{issue.get('acceptance_test', '')}
```

## Definition of done

{issue.get('definition_of_done', '')}

## Before you start

This issue is contributor work for **Git Together**. You are not being asked to deploy or operate the project.

- Read the [Git Together guide]({REPO_URL}/blob/main/docs/event-guide.md) and the [GitHub workflow]({REPO_URL}/blob/main/docs/event-github-workflow.md).
- Comment on this issue and wait until a mentor assigns it to you.
- Work on **one issue at a time**. Change only the files listed above.
- Stuck? Check the [troubleshooting guide]({REPO_URL}/blob/main/docs/event-troubleshooting.md).
"""


def publish(issue: dict, *, dry_run: bool, show_body: bool) -> bool:
    title = issue["title"]
    body = build_body(issue)
    labels = issue.get("labels", [])
    milestone = issue.get("milestone", "")

    if dry_run:
        print(f"[DRY RUN] {issue['id']} - {title}")
        print(
            f"  set={issue.get('set')} area={issue.get('area')} "
            f"difficulty={issue.get('difficulty')} time={issue.get('estimated_time')}"
        )
        print(f"  labels: {', '.join(labels)}")
        print(f"  milestone: {milestone}")
        if show_body:
            print("\n" + body + "\n" + "-" * 72)
        return True

    cmd = ["issue", "create", "--title", title, "--body", body]
    for label in labels:
        cmd.extend(["--label", label])
    if milestone:
        cmd.extend(["--milestone", milestone])

    result = run_gh(cmd, check=False)
    if result.returncode == 0:
        print(f"Published: {result.stdout.strip()} - {title}")
        return True
    print(f"Failed: {title}\n{result.stderr.strip()}", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish event issues to GitHub.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to issues.yml")
    parser.add_argument("--set", type=normalize_set, help="Only publish one set (1, 2, or 3)")
    parser.add_argument("--area", help="Only publish one area (docs, backend, frontend, ...)")
    parser.add_argument("--difficulty", help="Only publish one difficulty")
    parser.add_argument("--limit", type=int, help="Publish at most this many issues")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be published")
    parser.add_argument("--show-body", action="store_true", help="Print the full issue body in dry-run mode")
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Publish even when an issue with the same title already exists",
    )
    args = parser.parse_args()

    issues = load_issues(args.manifest)
    if args.set:
        issues = [issue for issue in issues if issue.get("set") == args.set]
    if args.area:
        issues = [issue for issue in issues if issue.get("area") == args.area]
    if args.difficulty:
        issues = [issue for issue in issues if issue.get("difficulty") == args.difficulty]
    if args.limit is not None:
        issues = issues[: args.limit]

    if not issues:
        print("No issues matched the filters.", file=sys.stderr)
        return 1

    if not args.dry_run:
        check_labels(issues)
        if not args.no_dedupe:
            known = existing_titles()
            before = len(issues)
            issues = [issue for issue in issues if issue["title"] not in known]
            skipped = before - len(issues)
            if skipped:
                print(f"Skipping {skipped} issue(s) whose title already exists.")

    published = 0
    failed = 0
    for issue in issues:
        if publish(issue, dry_run=args.dry_run, show_body=args.show_body):
            published += 1
        else:
            failed += 1

    action = "Would publish" if args.dry_run else "Published"
    print(f"\n{action} {published} issue(s); {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
