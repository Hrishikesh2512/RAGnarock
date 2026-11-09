# RAGnarok developer commands.
#
# `just` is optional. Every recipe maps to a command documented in
# docs/event-setup.md and docs/event-guide.md.

# List the available recipes.
default:
    @just --list

# Install backend and frontend dependencies.
setup:
    cd backend && uv sync --extra dev
    cd frontend && npm ci

# Run the database-free backend tests and the frontend tests.
test:
    cd backend && uv run pytest -m "not integration"
    cd frontend && npm test

# Run both linters.
lint:
    cd backend && uv run ruff check .
    cd frontend && npm run lint

# Format the backend and auto-fix frontend lint issues.
fmt:
    cd backend && uv run ruff format .
    cd frontend && npm run lint -- --fix

# Type-check both applications.
typecheck:
    cd backend && uv run mypy app
    cd frontend && npm run typecheck

# Verify the frontend production build.
build:
    cd frontend && npm run build

# Validate the 150-issue event manifest.
validate-issues:
    python3 scripts/validate_issues.py --strict

# Regenerate docs/event-issue-index.md from the manifest.
render-index:
    python3 scripts/render_issue_index.py

# Create the event labels and milestones.
setup-github:
    python3 scripts/setup_github.py

# Preview one set without publishing. Usage: just publish-dry-run 1
publish-dry-run set_no="1":
    python3 scripts/publish_issues.py --set {{set_no}} --dry-run

# Publish one set. Usage: just publish 1
publish set_no="1":
    python3 scripts/publish_issues.py --set {{set_no}}
