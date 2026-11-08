#!/usr/bin/env python3
"""Publish issues from planning/issues.yml to GitHub using the gh CLI.

Usage:
    python scripts/publish_issues.py --dry-run
    python scripts/publish_issues.py --milestone M1
    python scripts/publish_issues.py --all
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install it with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_issues(manifest_path: Path) -> list[dict]:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("issues", [])


def publish_issue(issue: dict, dry_run: bool = False) -> None:
    title = issue["title"]
    milestone = issue.get("milestone", "")
    labels = issue.get("labels", [])
    spec_section = issue.get("spec_section", "")
    acceptance_test = issue.get("acceptance_test", "")
    files_to_touch = issue.get("files_to_touch", [])
    description = issue.get("description", "").strip()

    body = f"""### Description
{description}

### Specification Reference
Section `{spec_section}` in [docs/architecture.md](docs/architecture.md).

### Acceptance Test
Run the test command:
```bash
{acceptance_test}
```

### Files to Touch
""" + "\n".join(f"- `{f}`" for f in files_to_touch)

    if dry_run:
        print(f"[DRY RUN] Would publish: {title}")
        print(f"  Labels: {', '.join(labels)}")
        print(f"  Milestone: {milestone}\n")
        return

    cmd = ["gh", "issue", "create", "--title", title, "--body", body]
    for label in labels:
        cmd.extend(["--label", label])
    if milestone:
        cmd.extend(["--milestone", milestone])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Published: {title} -> {result.stdout.strip()}")
    else:
        print(f"Error publishing '{title}': {result.stderr.strip()}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish RAGnarock issues to GitHub.")
    parser.add_argument("--dry-run", action="store_true", help="Print issues without publishing")
    parser.add_argument("--milestone", help="Filter by milestone (e.g. M1, M2)")
    parser.add_argument("--label", help="Filter by label (e.g. 'good first issue')")
    parser.add_argument("--manifest", default="planning/issues.yml", help="Path to manifest")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    issues = load_issues(manifest_path)
    count = 0
    for issue in issues:
        if args.milestone and issue.get("milestone") != args.milestone:
            continue
        if args.label and args.label not in issue.get("labels", []):
            continue

        publish_issue(issue, dry_run=args.dry_run)
        count += 1

    print(f"Done. Processed {count} issues.")


if __name__ == "__main__":
    main()

