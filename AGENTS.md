# AGENTS.md

Guidance for AI coding agents working in this repository. Humans are welcome to
read it too. Read `docs/architecture.md` before making non-trivial changes; it is
the authoritative specification.

---

## 1. What this project is

RAGnarock is an open-source retrieval-augmented generation application built for
a large group of junior contributors (~150 during a launch event). It must stay
small, boring, and easy to explain. Two applications, one infrastructure
directory, no workspace tooling.

- **Backend:** Python 3.12, FastAPI, synchronous SQLAlchemy 2.x, psycopg 3, Alembic, Postgres + pgvector.
- **Frontend:** React 19, TypeScript 5.9, Vite, Tailwind CSS 4, TanStack Query, React Router.
- **Runtime:** Docker Compose everywhere. Local stack for contributors; the same
  images and compose file with the `prod` profile for the hosted AWS EC2 VM
  (`linux/arm64`, Graviton).
- **Product rule:** model keys are BYOK per request; embeddings are local and keyless.

## 2. Current state (2026-11-08)

The scaffold is complete. **No product features are implemented yet.**

| Exists | Does not exist yet |
|---|---|
| `backend/app/main.py` with `/health` and `/version` | Any document, chat, search, or auth endpoint |
| Settings, structlog setup, DB engine/session, Alembic wiring | ORM models or a first migration |
| Frontend router, QueryClient, placeholder home, error boundary | API client, components, feature pages |
| Dev and prod compose stacks, Caddy, Dockerfiles | CI workflows, deployment runbook, issue manifest |
| Backend unit tests (6) | Frontend tests, e2e tests |

Do not assume a feature exists because the architecture describes it. Check the
tree first. The maintainer plan lives in `ROADMAP-TEMP.md`, which is deleted
before the event; do not depend on it permanently.

## 3. Repository map

```
backend/
  app/main.py              app factory, lifespan, docs at /api/docs
  app/api/router.py        api_router, prefix /api — add feature routers here
  app/api/routes/health.py GET /health and GET /version (root, unauthenticated)
  app/core/config.py       pydantic-settings; the only source of configuration
  app/core/logging.py      structlog setup (console or JSON)
  app/db/base.py           DeclarativeBase + constraint naming convention
  app/db/session.py        sync engine, SessionLocal, get_db()
  alembic/                 migrations; versions/ is empty by design
  tests/                   pytest, 6 tests today

frontend/
  src/main.tsx             StrictMode → providers → router
  src/app/router.tsx       createBrowserRouter
  src/app/providers.tsx    QueryClientProvider
  src/pages/               route-level components
  vite.config.ts           @ alias, /api dev proxy, Vitest config
  eslint.config.js         flat config, ignores src/api/generated

infra/
  compose.yml              dev stack: db, api, web (+ debug profile)
  compose.prod.yml         prod stack: db, api, edge; only edge publishes ports
  Dockerfile               node build → Caddy, context is the repo root
  Caddyfile                SPA + /api/* + /health + /version, security headers

docker-compose.yml         root entry point; includes infra/compose.yml
.env.example               every variable from architecture §12
```

## 4. Commands

Run from the stated directory.

### Backend (`backend/`)

```bash
uv sync --extra dev          # install/refresh the locked environment
uv run pytest                # tests
uv run ruff check .          # lint
uv run ruff format .         # format
uv run mypy app              # type-check
uv run alembic upgrade head  # migrate (needs Postgres)
uv run alembic upgrade head --sql   # inspect SQL without a database
uv run uvicorn app.main:app --reload
```

### Frontend (`frontend/`)

```bash
npm ci                       # reproducible install
npm run dev                  # Vite on :5173
npm run build                # tsc --noEmit && vite build
npm run lint
npm run typecheck
npm test                     # Vitest (no tests yet)
npm run e2e                  # Playwright
npm run api:types            # regenerate src/api/generated/schema.d.ts
```

### Containers (repository root)

```bash
docker compose up --build    # dev stack: :5173 and :8000
docker compose down
docker compose --profile debug up    # also publishes Postgres on 127.0.0.1:5432

# Production stack (needs POSTGRES_PASSWORD and JWT_SECRET)
docker compose -f infra/compose.prod.yml up -d --build
```

When smoke-testing the prod stack alongside the dev stack, pass an isolated
project name (`--project-name ragnarock-smoke`) so volumes and containers do not
collide. Tear it down with `down -v`.

## 5. Non-negotiable invariants

These come from `docs/architecture.md` and its decision log. Do not change them
without a maintainer decision and a new decision-log entry.

1. **Postgres is the source of truth.** Vectors are derived and rebuildable.
   pgvector only in v0.1; Qdrant is a v0.2 seam behind `VectorStore`.
2. **No LangChain, LlamaIndex, Celery, Redis, or Qdrant.** The pipeline is the
   teaching material. No broker in v0.1.
3. **Synchronous SQLAlchemy.** Never introduce async sessions, `asyncpg`, or
   `AsyncSession`. Blocking work is dispatched to a thread explicitly.
4. **Python 3.12 exactly** (`backend/.python-version`). Do not bump to 3.13.
5. **TypeScript 5.9.3 exactly.** `typescript-eslint@8` requires `<6.1.0`; TS 7
   breaks linting. Do not upgrade without replacing the lint stack.
6. **BYOK for generation.** Keys arrive per request in `X-Provider-Key`, are
   request-scoped, never stored, never logged. There is no server-side model key
   unless `ALLOW_SERVER_LLM_KEY=true`, which is off by default.
7. **Embeddings are server-side and keyless.** Local `BAAI/bge-small-en-v1.5`,
   384 dimensions, CPU. `EMBEDDING_DIM` is validated against the loaded model.
8. **Same-origin only.** Caddy serves the SPA and proxies `/api`. Do not add CORS
   middleware. Do not introduce a separate frontend origin.
9. **One compose file, two profiles.** Local and hosted must not diverge in
   runtime shape.
10. **No cost, credit, or billing figures in committed files.** The project is
    open source; hosting economics belong to deployers.
11. **`AUTH_DISABLED=true` is rejected in production.** Config already enforces
    this. Do not weaken the validator.

## 6. Backend conventions

- Configuration only through `app.core.config.get_settings()`. Never read
  `os.environ` in application code. New variables go in `Settings`, `.env.example`,
  and architecture §12 in the same change.
- Route modules live in `app/api/routes/` and are mounted on `api_router`
  (`prefix="/api"`). Probes stay at the root and must be added to `infra/Caddyfile`.
- Use `Depends(get_db)` for sessions. Do not create engines or sessions ad hoc.
- Type hints on all public functions. `mypy` runs with `check_untyped_defs`.
- Line length 100. Ruff selects `E,F,I,UP,B,SIM`. FastAPI defaults are exempt from
  B008 via `extend-immutable-calls`.
- Never log secrets or request headers containing credentials. The redaction
  filter is a launch requirement (§13.1), not an optional hardening step.
- Errors follow the specific codes in architecture §14. Do not return bare 500s
  for conditions that have a named failure mode.
- Add models under `app/db/models/`, import them in `app/db/models/__init__.py`,
  and import that package from `alembic/env.py`. Otherwise autogenerate sees
  nothing.
- Migrations are required for every schema change, including the first one.
  Review generated SQL; never edit an applied migration.

## 7. Frontend conventions

- Named exports, function components, no class components.
- Import through the `@/` alias, not deep relative paths.
- One `tsconfig.json` covering `src/` and `vite.config.ts`. Keep `noEmit`; Vite
  does the emitting.
- Tailwind v4: a single `@import "tailwindcss";` in `src/index.css`. Do not add
  `tailwind.config.js`, PostCSS, or autoprefixer.
- Use `import.meta.env` in source; `process.env` is only valid in `vite.config.ts`.
- `src/api/generated/` is generated by `npm run api:types`. Never hand-edit it;
  it is ESLint-ignored on purpose.
- Data fetching goes through TanStack Query hooks, not `useEffect` fetch loops.
- Keep the initial bundle under 250 kB gzip. Check `npm run build` output.
- The `@tanstack/react-query` provider stays in `src/app/providers.tsx`; route
  additions go in `src/app/router.tsx`.

## 8. Infrastructure conventions

- Run compose from the repository root. `docker-compose.yml` uses `include:`;
  paths inside `infra/compose.yml` resolve relative to `infra/`.
- Pass environment inline in compose. Do not add `env_file:` for a file that may
  not exist; compose fails before starting anything.
- Dev API keeps its virtualenv at `/opt/venv`, outside the `/app` bind mount.
  Never mount a volume over `/opt/venv`.
- Dev frontend keeps `node_modules` in a named volume. Re-run `npm ci` inside the
  container (or recreate the volume) after dependency changes.
- Postgres is unpublished by default. Use the `debug` profile for host access.
- Any new public root path must be added to `infra/Caddyfile`; `/api/*` already
  proxies.
- Keep the runtime image non-root, CPU-only, and free of build tooling.
- `torch` must remain a **direct** dependency so `[tool.uv.sources]` applies. If
  it becomes transitive again, uv resolves PyPI's CUDA build (~GBs). CI should
  assert the installed version ends in `+cpu` or reports CPU-only.

## 9. Testing expectations

- Every behaviour change ships with a test. Bug fixes ship with a regression test.
- Pytest uses `pythonpath = ["."]`; run from `backend/`.
- Mark tests that need a database with `@pytest.mark.integration`; keep the default
  suite database-free so contributors can run it anywhere.
- Prefer the FastAPI `TestClient` for route tests. Override dependencies rather
  than reaching into module globals.
- Frontend: Vitest + Testing Library for hooks and components; Playwright only for
  the end-to-end flow.
- A skipped test is an issue, not dead code. Do not delete skipped tests without
  checking `planning/issues.yml`.

## 10. Known gotchas

- `npm audit` reports moderate `minimatch` advisories through ESLint. They are
  dev-only. The only offered fix downgrades to ESLint 9; do not apply it.
- The host `backend/.venv` is a Windows environment and is shadowed inside the
  container by `/opt/venv`. This is expected.
- `uv sync` warns about hardlinks when the cache and workspace are on different
  filesystems. Set `UV_LINK_MODE=copy` to silence it; behaviour is unaffected.
- Alembic `current` fails without a running database; `upgrade head --sql` works
  offline.
- Production config intentionally fails without `JWT_SECRET` and with
  `AUTH_DISABLED=true`.
- Caddy's default `SITE_ADDRESS` is `localhost`, which uses its internal CA. Use
  `http://localhost` for a plain-HTTP local smoke test.
- FastAPI docs live at `/api/docs` and the schema at `/api/openapi.json`, not at
  the conventional root paths.

## 11. Definition of done for a change

- [ ] Behaviour matches `docs/architecture.md`, or the doc is updated in the same change.
- [ ] Tests added or updated; the default suite passes without Postgres.
- [ ] `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy app` clean.
- [ ] `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` clean (frontend changes).
- [ ] New configuration documented in `Settings`, `.env.example`, and §12.
- [ ] New dependencies justified in the PR description; lockfiles committed.
- [ ] No secrets, `.env` files, `node_modules`, `.venv`, or build output committed.
- [ ] New root-level endpoint added to `infra/Caddyfile`.
- [ ] Diff is reviewable by a junior contributor: small, named clearly, no drive-by refactors.

## 12. When to stop and ask

Ask a maintainer before: changing a decision in §19, adding a dependency that
duplicates an existing capability, altering the compose topology, touching auth
or credential handling, changing pinned versions, or rewriting the scaffold.
Open an issue for anything larger than a single reviewable change.
