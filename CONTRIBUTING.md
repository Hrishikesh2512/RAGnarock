# Contributing to RAGnarock

Thank you for your interest in contributing to **RAGnarock**! We are committed to building an approachable, educational, and high-performance open-source RAG application for developers and learners worldwide.

This guide outlines our project standards, contribution policies, and local development workflows. Please take a few moments to review it before getting started.

---

## Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please ensure interactions across issues, pull requests, and discussions remain welcoming, professional, and constructive.

---

## Issue Assignment & Claiming Policy

To ensure fairness and equal opportunity across our ~150 junior contributors, we enforce the following rules:

1. **One Issue at a Time:**
   * Contributors may only be assigned to **one active issue** at any given time.
   * Finish and merge your current pull request before requesting another issue.
2. **Claiming an Issue:**
   * To work on an issue, comment on the issue ticket expressing your interest.
   * Maintainers will assign the issue to you with the `assigned` label.
   * Do not open a pull request for an issue assigned to someone else.
3. **Activity & Auto-Unassign Policy:**
   * If there is no pull request or status update within **48 hours** of assignment, the issue will be unassigned and returned to the contributor pool to prevent issue hoarding.

---

## Architectural Invariants (Must Read)

Before introducing changes, ensure your implementation adheres to our core invariants (see [AGENTS.md](AGENTS.md) and [docs/architecture.md](docs/architecture.md)):

* **PostgreSQL is the source of truth:** Documents, chunk text, and embeddings live in PostgreSQL with `pgvector`. Vectors are derived data and always rebuildable.
* **No black-box framework abstractions:** We explicitly do **not** use LangChain, LlamaIndex, Celery, or Redis. The pipeline itself is the curriculum.
* **Synchronous SQLAlchemy:** Never introduce `asyncpg` or async session wrappers. Blocking work runs in explicit worker threads.
* **BYOK (Bring Your Own Key):** Model keys are provided per-request in the UI (`X-Provider-Key`), kept only in browser memory, and never persisted or logged by the server.
* **Server-side keyless embeddings:** Embeddings are generated locally on CPU via `BAAI/bge-small-en-v1.5` (384 dimensions).

---

## Git Workflow & Conventions

### Branch Naming Convention

Create feature branches using the following structure:
```text
<type>/<issue-number>-<short-description>
```

Examples:
* `feat/12-add-pdf-parser`
* `fix/45-cors-preflight-origin`
* `docs/3-update-readme-badges`
* `refactor/88-chunker-registry`

### Commit Message Guidelines (Conventional Commits)

We enforce the [Conventional Commits](https://www.conventionalcommits.org/) specification:

| Prefix | Description | Example |
| :--- | :--- | :--- |
| `feat:` | A new user-facing feature or capability | `feat: add PDF document parser using pypdf` |
| `fix:` | A bug fix or regression repair | `fix: resolve markdown upload MIME detection on Windows` |
| `docs:` | Documentation changes only | `docs: add self-hosting instructions` |
| `refactor:` | Code restructuring without changing behavior | `refactor: extract pgvector queries to VectorStore protocol` |
| `test:` | Adding or updating automated tests | `test: add unit tests for content-type normalization` |
| `infra:` | CI/CD, Docker, or tooling updates | `infra: update Docker multi-arch workflow for ARM64` |

---

## Local Development & Testing

### 1. Environment Setup

Clone your fork and navigate into the repository:
```bash
git clone https://github.com/<your-username>/RAGnarock.git
cd RAGnarock
```

### 2. Backend Verification (`backend/`)

The backend requires **Python 3.12** and **uv**:
```bash
cd backend
uv sync --extra dev          # Install locked dependencies into .venv
uv run alembic upgrade head  # Apply migrations (requires Postgres)
uv run pytest                # Run database-free unit test suite
uv run ruff check .          # Linting
uv run ruff format --check . # Format verification
uv run mypy app              # Strict type checking
```

### 3. Frontend Verification (`frontend/`)

The frontend requires **Node.js >= 22**:
```bash
cd frontend
npm ci                       # Reproducible dependency install
npm run lint                 # ESLint check
npm run typecheck            # TypeScript compiler check
npm test                     # Vitest component test suite
npm run build                # Production build check
```

---

## Pull Request Submission Checklist

When opening a pull request, please ensure the following:

- [ ] The PR references the issue number it closes (e.g. `Closes #42`).
- [ ] The change is small, atomic, and focused (ideally under 400 lines of diff).
- [ ] Backend tests pass and code is formatted (`uv run pytest`, `uv run ruff check .`, `uv run mypy app`).
- [ ] Frontend tests pass and types are clean (`npm run lint`, `npm run typecheck`, `npm test`, `npm run build`).
- [ ] Any new configuration settings are documented in `app/core/config.py`, `.env.example`, and `docs/architecture.md`.
- [ ] No secrets, local credentials, `.env` files, or build artifacts are included.

Thank you for helping make RAGnarock great!
