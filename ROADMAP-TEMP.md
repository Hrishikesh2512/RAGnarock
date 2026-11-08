# RAGnarock — Maintainer Roadmap (TEMPORARY)

> **DELETE THIS FILE BEFORE THE EVENT.**
> It contains internal sequencing, unshipped gaps, and maintainer-only notes.
> The permanent document is `AGENTS.md`; the specification is
> `docs/architecture.md`. Nothing here should be linked from `README.md`.

**Status:** 2026-11-08 · Spec: `docs/architecture.md` v1.1 · Audience: maintainers

---

## 1. Where we are

The scaffold is complete and runs end to end. No product features exist yet.

| Area | State |
|---|---|
| Spec | `docs/architecture.md` v1.1 — local = Docker Compose, hosted = AWS EC2 |
| Backend deps | Python 3.12.13 via uv, 93 packages, CPU-only torch |
| Backend skeleton | `create_app()`, `/health`, `/version`, settings, logging, DB session, Alembic |
| Database | `alembic_version` only; no models, no migrations |
| Frontend deps | React 19.3, Vite 8.3, TS 5.9.3, Tailwind 4.3, Vitest 5.1, Playwright 1.65 |
| Frontend shell | Router, QueryClient, placeholder home, error boundary. No API client |
| Containers | Dev stack and prod stack both built and smoke-tested |
| CI/CD | **Nothing.** No workflows, no branch protection, no CODEOWNERS |
| Contributor docs | **Nothing.** No README, CONTRIBUTING, issue templates, issue manifest |
| Hosted deploy | **Not done.** No AWS instance, no runbook, no backup job |

Verified on 2026-11-08: `pytest` 6 passed, `ruff`/`mypy` clean, `npm run build`
105.66 kB gzip, dev stack healthy on `:5173`/`:8000`, prod stack healthy on
`:80`/`:443` with CSP headers and SPA fallback.

---

## 2. Definition of done for the event

1. A clean laptop runs `docker compose up` and completes one real RAG flow.
2. The hosted demo is live on the EC2 VM, same compose file, `prod` profile.
3. CI is green and `main` is protected.
4. **150 atomic issues** are published, at least 30 labelled `good first issue`.
5. `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and onboarding docs exist.
6. Every issue has a failing/skipped test written **before** publication.
7. This file is deleted.

---

## 3. Milestones

Ordered by dependency, not calendar. Do not start a milestone before its
predecessor's exit criteria are met.

### M0 — Freeze the scaffold (≈15 issues)

**Deliverables**

- Commit the current tree; add `README.md` with the three commands that matter.
- `.github/workflows/ci-api.yml`: `ruff check`, `ruff format --check`, `mypy app`, `pytest`.
- `.github/workflows/ci-web.yml`: `npm ci`, `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`.
- `.github/workflows/docker.yml`: build `linux/amd64` + `linux/arm64` images, push to GHCR on tags.
- `.github/workflows/nightly.yml`: scheduled compose smoke test (fake LLM).
- CODEOWNERS, issue templates, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- `planning/issues.yml` manifest + `scripts/publish_issues.py`.
- `justfile` with `up`, `down`, `test`, `lint`, `fmt`, `seed`, `reset`.
- Root `README.md`; badge block. **No cost figures anywhere.**

**Exit criteria:** CI green on `main`; branch protection requires both workflows;
a fresh clone can run the dev stack using only the README.

**Known gap to close here:** `alembic/env.py` reads `Base.metadata` but nothing
imports models yet. When the first model lands, create `app/db/models/__init__.py`
that imports every model module, and import that package from `alembic/env.py`,
otherwise `alembic revision --autogenerate` produces empty migrations.

### M1 — Vertical slice with the fake provider (≈30 issues)

The one flow everything else hangs off:

```
upload .txt → parse → chunk → embed (bge-small) → store in pgvector
question → retrieve top-k → build prompt → fake LLM → stream answer → citations
```

**Deliverables**

- Models + first migration: `users`, `workspaces`, `documents`, `chunks`,
  `conversations`, `messages`, `message_citations`; `vector` extension; HNSW index.
- `VectorStore` protocol + `PgVectorStore` implementation.
- `Embedder` protocol + local bge-small singleton (lazy load, thread-safe).
- `Parser` and `Chunker` registries; `.txt` + Markdown only.
- `LLMProvider` protocol + `FakeProvider` that streams deterministic text.
- Ingestion job with the status machine from §6.3; `BackgroundTasks` runner.
- `POST /api/documents`, `GET /api/documents/{id}`, `POST /api/chat` (SSE).
- Minimal frontend: upload control, status poll, chat transcript, inline citations.
- Integration tests guarded by the `integration` marker, run in CI with a Postgres service.

**Exit criteria:** `docker compose up` on a clean machine, upload a text file, ask
a question, see a grounded answer with citations. **Publish the first 20–30 issues
now**, not before.

### M2 — Real generation (≈20 issues)

- OpenRouter provider with request-scoped `X-Provider-Key`; never persisted.
- Provider error mapping per §14: 401/429/5xx, one retry with jitter, idle timeout.
- SSE streaming contract + client reconnect semantics; partial answer retention.
- Prompt assembly, context trimming to `CONTEXT_MAX_TOKENS`, citations extraction.
- Optional Ollama provider behind the same protocol (dev convenience only).
- Redaction filter + access-log stripping for `authorization`, `x-provider-key`, `cookie`.
- Canary test: sentinel key produces zero log records.

**Exit criteria:** real OpenRouter answer streams with citations; sentinel test green.

### M3 — Auth, sessions, limits (≈20 issues)

- Argon2id register/login, access + rotating refresh tokens.
- Workspace-scoped repositories; ownership enforced below the route layer.
- Guest sessions per §13.4: httpOnly/SameSite=Lax/Secure cookie, 7-day purge.
- Per-session rate limits for chat and upload; 429 with `Retry-After`.
- `AUTH_DISABLED=false` path exercised in CI (config already rejects it in production).

**Exit criteria:** guest can use the demo without an account; limits enforced; purge job tested.

### M4 — Formats and ingestion robustness (≈20 issues)

- PDF, DOCX, HTML parsers; content-type detection, extension cross-check.
- Size limit enforced before body read (`MAX_UPLOAD_MB`), server-generated storage keys.
- Per-document parse timeout, archive-bomb rejection, partial-chunk cleanup on failure.
- Checksum duplicate detection; document delete cascades chunks and stored file.
- Local storage backend + S3-compatible backend behind one interface.

**Exit criteria:** the §13.2 checklist is covered by tests; a 10 MB PDF ingests or fails legibly.

### M5 — Frontend product (≈30 issues)

- Generated client from `/api/openapi.json`; CI check that the schema is current.
- Document library: list, filters, status badges, delete, retry.
- Chat: streaming render, stop, regenerate, error states, provider-key setup dialog.
- Sources panel: chunk preview, score, jump-to-citation.
- Settings: model choice, temperature, retrieval knobs (read-only defaults first).
- Accessibility pass, keyboard navigation, empty/loading/error states.
- Vitest coverage for hooks and pure components; Playwright for upload → answer.

**Exit criteria:** the flow is usable without reading docs; e2e green in CI.

### M6 — Hosted deployment (≈10 issues)

- `infra/deploy/aws-ec2.md`: provisioning, security group, Elastic IP, Docker install,
  compose `prod` profile, TLS, log rotation, upgrade procedure.
- Nightly `pg_dump` + upload archive to object storage; restore drill documented.
- GitHub Actions cron polling `/health` every 6 hours with alerting.
- ARM64 image verification: CI publishes `linux/arm64`; deploy pulls the same tag.
- Secrets: `POSTGRES_PASSWORD`, `JWT_SECRET`, `SITE_ADDRESS`; no provider key on the server.
- Delete or rotate any temporary demo credentials before launch.

**Exit criteria:** public URL serves the SPA and API same-origin; restore from backup rehearsed.

### M7 — Contributor launch (≈5 issues)

- Onboarding doc: clone → `docker compose up` → first issue, under 15 minutes.
- Triage rotation, label taxonomy, `good first issue` set, issue manifest published.
- Publish remaining issues in waves of 20–30; keep ~30 unassigned good-first issues.
- Pin the architecture doc version in the README.
- **Delete `ROADMAP-TEMP.md`.**
- Dry run with 3–5 people who have never seen the repo; fix every papercut.

**Exit criteria:** a new contributor merges a one-file change within a day.

---

## 4. Issue publication rules

- **150 issues on day one** is the target; the unlucky remainder can follow in waves.
- One issue = one reviewable diff, ideally under 400 lines.
- The test exists first and is skipped. The issue says *"make this skipped test
  pass"* — never *"write the test and the code"*.
- Every issue names: files to touch, acceptance test, spec section, and whether it
  is `good first issue`, `backend`, `frontend`, `infra`, `docs`.
- No issue depends on an unmerged branch. If it must, mark it `blocked`.
- Bugs found while scaffolding get issues too; do not silently fix them in unrelated PRs.

Suggested split: M0 15, M1 30, M2 20, M3 20, M4 20, M5 30, M6 10, M7 5.

---

## 5. Risks and open questions

| Risk | Mitigation |
|---|---|
| 150 issues overwhelm reviewers | Wave publication; 20–30 open at a time; CODEOWNERS per area |
| Junior contributors cargo-cult async SQLAlchemy | Sync-only rule in `AGENTS.md`; reject async session PRs |
| CUDA torch sneaks back in | `torch` stays a direct dep with the CPU index; CI asserts `+cpu` |
| Dev/prod drift | One compose file, one image, `prod` profile only changes config |
| BYOK key leakage | Redaction canary test blocks merge; no server key by default |
| ARM64 surprises | CI builds both platforms; hosted runs the published arm64 image |
| Demo abuse | Guest TTL, per-session rate limits, no server key |
| Windows contributors | `CHOKIDAR_USEPOLLING`, named `node_modules` volume, no symlinks |

Open questions (from §19): guest vs email signup (Q1), rate-limited demo key (Q2),
default demo model (Q3), CDN (Q4), backup retention (Q5). Decide before M6.

---

## 6. Pre-event checklist

- [ ] CI green on `main`; branch protection and CODEOWNERS active
- [ ] Hosted demo reachable over HTTPS with a valid certificate
- [ ] `pg_dump` ran at least once and a restore was rehearsed
- [ ] 150 issues published; ≥30 `good first issue`; every one has a skipped test
- [ ] README, CONTRIBUTING, CODE_OF_CONDUCT, onboarding doc merged
- [ ] `docker compose up` verified on Windows, macOS, and Linux
- [ ] No provider key anywhere in the repo, CI logs, or the server
- [ ] No AWS cost, credit, or billing detail in any committed file
- [ ] `ROADMAP-TEMP.md` deleted
- [ ] Dry run with fresh contributors completed

---

## 7. Deliberately deferred until after v0.1

Qdrant, LangChain/LlamaIndex, Celery/Redis, async SQLAlchemy, multi-tenant billing,
SSO, CDN, fine-tuning, hybrid/BM25 search, rerankers, OCR, S3 presigned uploads.
Each has a protocol seam; do not pre-build for them.
