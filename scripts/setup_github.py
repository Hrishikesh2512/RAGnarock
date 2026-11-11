#!/usr/bin/env python3
"""Create the labels and milestones used by the event issue manifest.

Usage:
    python3 scripts/setup_github.py --dry-run
    python3 scripts/setup_github.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LABELS: dict[str, tuple[str, str]] = {
    "good first issue": ("7057ff", "Good for newcomers to the event"),
    "no-code": ("c2e0c6", "No programming required; docs, config, or design work"),
    "backend": ("1f6feb", "FastAPI, database, RAG, and provider code"),
    "frontend": ("a371f7", "React, TypeScript, Vite, and UI code"),
    "infra": ("fbca04", "Docker, CI, deployment, and repository tooling"),
    "docs": ("0075ca", "Documentation and guides"),
    "test": ("5319e7", "Automated tests and test coverage"),
    "design": ("d876e3", "Design system, UX copy, and accessibility"),
    "accessibility": ("0e8a16", "Keyboard, screen reader, and contrast improvements"),
    "ci": ("cccccc", "GitHub Actions and automation"),
    "set-1": ("c5def5", "Set 1 - Starter"),
    "set-2": ("bfd4f2", "Set 2 - Backend"),
    "set-3": ("d4c5f9", "Set 3 - Frontend & Design"),
    "difficulty:beginner": ("0e8a16", "About 20-60 minutes; some reading required"),
    "difficulty:intermediate": ("fbca04", "About 1-2 hours; read the linked source first"),
    "difficulty:advanced": ("b60205", "Multi-file change or significant context required"),
}

MILESTONES: dict[str, str] = {
    "Set 1 - Starter": "Docs, focused tests, and tiny tooling fixes.",
    "Set 2 - Backend": "Small backend helpers, tests, and integrations.",
    "Set 3 - Frontend & Design": "Reusable React components, hooks, utilities, and design notes.",
}


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, check=check, cwd=ROOT)


def repo_name() -> str:
    result = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], check=False)
    if result.returncode != 0:
        print("Could not determine the repository. Run `gh auth status` first.", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(1)
    return result.stdout.strip()


def ensure_labels(repo: str, dry_run: bool) -> None:
    for name, (color, description) in LABELS.items():
        if dry_run:
            print(f"[DRY RUN] label {name} -> #{color}")
            continue
        result = run(
            [
                "gh",
                "label",
                "create",
                name,
                "--color",
                color,
                "--description",
                description,
                "--force",
                "--repo",
                repo,
            ],
            check=False,
        )
        if result.returncode != 0:
            print(f"Failed to create label {name}: {result.stderr.strip()}", file=sys.stderr)
            raise SystemExit(1)
        print(f"Label ready: {name}")


def existing_milestones(repo: str) -> dict[str, int]:
    result = run(["gh", "api", f"repos/{repo}/milestones", "--paginate"], check=False)
    if result.returncode != 0:
        print(f"Failed to list milestones: {result.stderr.strip()}", file=sys.stderr)
        raise SystemExit(1)
    items = json.loads(result.stdout or "[]")
    return {item["title"]: item["number"] for item in items}


def ensure_milestones(repo: str, dry_run: bool) -> None:
    existing = {} if dry_run else existing_milestones(repo)
    for title, description in MILESTONES.items():
        if title in existing:
            print(f"Milestone ready: {title}")
            continue
        if dry_run:
            print(f"[DRY RUN] milestone {title}")
            continue
        result = run(
            [
                "gh",
                "api",
                "-X",
                "POST",
                f"repos/{repo}/milestones",
                "-f",
                f"title={title}",
                "-f",
                f"description={description}",
                "-f",
                "state=open",
            ],
            check=False,
        )
        if result.returncode != 0:
            print(f"Failed to create milestone {title}: {result.stderr.strip()}", file=sys.stderr)
            raise SystemExit(1)
        print(f"Milestone created: {title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create event labels and milestones.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing GitHub")
    args = parser.parse_args()

    if not args.dry_run:
        status = run(["gh", "auth", "status"], check=False)
        if status.returncode != 0:
            print("GitHub CLI is not authenticated. Run `gh auth login`.", file=sys.stderr)
            return 1

    repo = "OWNER/REPO" if args.dry_run else repo_name()
    print(f"Repository: {repo}\n")
    ensure_labels(repo, args.dry_run)
    print()
    ensure_milestones(repo, args.dry_run)
    print("\nDone. Next: python3 scripts/validate_issues.py && python3 scripts/publish_issues.py --dry-run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
