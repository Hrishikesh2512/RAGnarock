# RAGnarok - Architecture

| | |
|---|---|
| **Status** | Accepted |
| **Version** | 1.2 |
| **Date** | 2026-11-08 |
| **Maintainers** | NodeDotAI |
| **License** | MIT |

---

## Table of contents

1. [Purpose and scope](#1-purpose-and-scope)
2. [Goals and non-goals](#2-goals-and-non-goals)
3. [Design principles](#3-design-principles)
4. [System context](#4-system-context)
5. [Deployment topologies](#5-deployment-topologies)
6. [Component architecture](#6-component-architecture)
7. [Data model](#7-data-model)
8. [RAG pipeline](#8-rag-pipeline)
9. [Provider abstractions](#9-provider-abstractions)
10. [Credential and secret model](#10-credential-and-secret-model)
11. [API surface](#11-api-surface)
12. [Configuration reference](#12-configuration-reference)
13. [Security architecture](#13-security-architecture)
14. [Failure modes and degradation](#14-failure-modes-and-degradation)
15. [Performance targets](#15-performance-targets)
16. [Testing strategy](#16-testing-strategy)
17. [Observability](#17-observability)
18. [Repository layout](#18-repository-layout)
19. [Decision log](#19-decision-log)
20. [Roadmap](#20-roadmap)
21. [Open questions](#21-open-questions)

---

## 1. Purpose and scope

RAGnarok is an open-source, contributor-friendly Retrieval-Augmented Generation system. It is designed as a **complete, runnable application** - frontend, backend, database, ingestion pipeline, containerization, and CI - rather than a notebook or a framework demo.

The project serves two audiences simultaneously:

- **Learners.** Git Together contributors, and other people learning the codebase, who should be able to change a real RAG implementation without a framework in the way.
- **Users.** Anyone who wants to upload their own documents and ask questions about them, either locally or through a public demo.

This document describes the architecture that both audiences run. There is **one codebase** and one compose file for the API stack; local development and the hosted demo differ only in configuration and in where the SPA is served (§5.2).

---

## 2. Goals and non-goals

### 2.1 Goals

| ID | Goal |
|---|---|
| G1 | Clone-to-running in under 10 minutes with a single command. |
| G2 | A complete RAG pipeline - parse, chunk, embed, store, retrieve, generate with citations - implemented in readable application code. |
| G3 | 150+ contributors can work in parallel on 150+ atomic issues with minimal merge conflicts. |
| G4 | Green CI with **zero repository secrets** for contributors and fork PRs. |
| G5 | The full stack runs online - SPA on a static host, API and database on a single commodity VM - functionally, not as a static mock. |
| G6 | No vendor lock-in: every external dependency sits behind an interface. |
| G7 | User credentials are never persisted by the server. |

### 2.2 Non-goals (v0.1)

| ID | Non-goal | Rationale |
|---|---|---|
| N1 | Multi-org tenancy, SSO, OAuth | Adds auth surface without teaching RAG. |
| N2 | Horizontal scaling | The reference deployment is a single node. |
| N3 | GPU inference | Code must run on CPU-only infrastructure. |
| N4 | Agentic tool use, web browsing | Out of scope until retrieval quality is solved. |
| N5 | Cloud-managed parsers, OCR APIs, managed vector databases | Incompatible with the credential model (§10). |
| N6 | Framework orchestration (LangChain, LlamaIndex) | The pipeline is the curriculum. |

---

## 3. Design principles

1. **Postgres is the source of truth.** Documents, chunk text, metadata, and pipeline state live in Postgres. The vector index is derived data and can always be rebuilt.
2. **Derived state is disposable.** Any index, cache, or artifact can be regenerated from the database with `just reindex`.
3. **Credentials flow inward, never outward.** Model keys are supplied per request and discarded. Nothing is written to logs, the database, or error trackers.
4. **Interfaces at every boundary.** `VectorStore`, `StorageBackend`, `EmbeddingProvider`, `LLMProvider`, `Parser`, `Chunker`. Swapping an implementation is a configuration change.
5. **Keyless by default.** The application is useful before the user supplies any credential.
6. **One artifact, two environments.** Local and production use the same API images and the same compose file. The SPA is the single exception: Vite builds it locally, Vercel builds it for the hosted demo.
7. **Small files, single responsibility.** One route module, parser, or component per file - this is what makes atomic issue decomposition possible.

---

## 4. System context

```mermaid
flowchart LR
    user["User<br/>(browser)"]
    ui["React SPA"]
    api["FastAPI service"]
    db[("PostgreSQL 17<br/>+ pgvector")]
    fs[("Local volume<br/>uploads")]
    llm["LLM provider<br/>OpenRouter / Ollama"]
    emb["Embedding model<br/>bge-small (local CPU)"]

    user --> ui
    ui -->|"HTTPS / SSE"| api
    api --> db
    api --> fs
    api -->|"chat completion<br/>BYOK"| llm
    api -->|"document + query<br/>embeddings"| emb
```

The embedding model is **in-process** and server-owned. The LLM provider is **remote and user-owned**. This asymmetry is deliberate and is explained in §10.

---

## 5. Deployment topologies

RAGnarok supports exactly two environments:

| Environment | Orchestration | Runs on | Purpose |
|---|---|---|---|
| **Local** | Docker Compose | Each contributor's machine | Development, testing, personal use |
| **Hosted** | Vercel (SPA) + Docker Compose (`prod` profile) | Vercel's edge, plus a single AWS EC2 instance for the API | The public demo linked from the README |

The API, database, and reverse proxy use the same images and compose file in both environments; only configuration differs. The SPA is the one deliberate exception: development serves it from the Vite dev server, the hosted demo serves it from Vercel (D13). Provider-specific runbooks live in `infra/deploy/`; provisioning, credentials, and operational procedure are deliberately out of scope for this document.

### 5.1 Local development (primary)

Every contributor runs the entire stack on their own machine. There is no shared state between contributors.

```
┌─────────────────────── contributor laptop ───────────────────────┐
│                                                                  │
│  docker compose up                                               │
│  ├── web        (node)      :5173  ── HMR                        │
│  ├── api        (python)    :8000                                │
│  └── db         (postgres)  :5432  [internal only]               │
│                                                                  │
│  named volumes: ragnarok_pgdata, ragnarok_uploads              │
└──────────────────────────────────────────────────────────────────┘
```

Characteristics:

- Hot reload for both `web` and `api`.
- Postgres port is **not published** by default; it is reachable only inside the compose network. A `debug` profile publishes it for GUI clients.
- `LLM_PROVIDER=fake` makes the entire stack runnable with no external key.
- `AUTH_DISABLED=true` short-circuits authentication to a seeded local user.

### 5.2 Reference deployment (hosted demo)

The SPA is served by Vercel; the API, database, and edge proxy run the `prod` compose profile on a single AWS EC2 instance (D13).

```
Internet
   │
   ├──►  <app>.vercel.app            Vercel: static React build, CDN, previews
   │        │
   │        │  fetch + SSE, cross-origin, X-Provider-Key
   │        ▼
   └──►  api.<host>  ──►  EC2 Elastic IP
                             │
                             ▼
                        Caddy (automatic TLS, API only)
                            ├── /api/*    → api:8000
                            ├── /health   → api:8000/health
                            └── /version  → api:8000/version
                             │
                             ├── api     (python, keyless embeddings)
                             ├── db      (postgres + pgvector, persistent volume)
                             └── uploads (persistent volume, nightly pg_dump + archive)
```

| Property | Value |
|---|---|
| Compute | AWS EC2 `t4g.medium` - Graviton (ARM64), 2 vCPU / 4 GB; the **only deployer-funded resource** |
| Architecture | `linux/arm64` for the API images; the SPA is built by Vercel |
| Storage | 30 GB gp3 root volume; persistent volumes for Postgres data and uploads |
| HTTPS | Caddy automatic certificates on the API host; Vercel-managed certificates on the SPA host |
| Frontend delivery | Vercel builds `frontend/` on every push: a production URL, immutable asset URLs, and a preview deployment per pull request. `frontend/vercel.json` rewrites every path to `/index.html` so client-side deep links work. |
| Vercel plan | Hobby - free, non-commercial use only. Includes 100 GB fast data transfer, 1,000,000 CDN requests, and 100 deployments per day; preview deployments count toward the daily deployment allowance. |
| Build settings | Root directory `frontend`, build command `npm run build`, output directory `dist`, and the Node version declared in `frontend/package.json` (`>=22`). |
| Origin policy | Cross-origin. The API accepts only the exact origins in `ALLOWED_ORIGINS`; a wildcard is never valid, and CORS is not an authorization boundary. |
| Session transport | Bearer tokens in the `Authorization` header; the hosted demo does not use third-party cookies (§13.4). |
| Availability monitoring | GitHub Actions cron polls `/health` every 6 hours |
| Durability | Nightly `pg_dump` + upload archive to object storage |
| Runbooks | `infra/deploy/aws-ec2.md`, `infra/deploy/vercel.md` |

Graviton is ARM64, so the hosted API consumes the same `linux/arm64` images CI publishes. The SPA has its own build path (Vercel), which is the deliberate exception to §3 principle 6.

**Why the API stays on one VM.** Self-hosting Postgres removes a second managed dependency, and the API deployment is the *same* compose file contributors run, so the backend has no second runtime shape to maintain. The SPA does not need that parity: static assets belong on a CDN, and Vercel provides the free `<app>.vercel.app` URL plus a preview deployment per pull request. Serverless is still ruled out for the API specifically: no persistent disk for uploads, `BackgroundTasks` die with the response (§6.3), and the image exceeds practical bundle limits.

**Why the browser calls the API directly.** Vercel can proxy `/api/*` with an external rewrite, but streaming Server-Sent Events through a CDN proxy is not guaranteed to stay incremental, and it adds a second failure domain between the user and the token stream. The SPA therefore calls the API origin directly and CORS is mandatory.

**The price is CORS.** Every cross-origin call needs an exact allowlist on the API, a preflight that permits `Authorization`, `Content-Type`, and `X-Provider-Key`, `Vary: Origin` on cacheable responses, and `Retry-After` exposure so §14 rate-limit messaging survives. CORS is not authentication: every endpoint still verifies the bearer token, and mutations additionally check `Origin` (§13.5). None of this is optional once the SPA leaves the origin.

**Free-tier budget.** The reference demo is designed to run without paid managed services:

- **SPA:** Vercel Hobby, free for personal, non-commercial projects. It includes enough bandwidth and requests for a demo, but it is a fair-use offer: Vercel may pause or remove a Hobby deployment, and a commercial deployment requires a paid plan. The static build is portable to any static host, which is the exit path if Hobby is no longer suitable.
- **API, database, uploads:** one EC2 Graviton instance. It is the only billable component; there is no managed database, cache, queue, or observability service. AWS includes 100 GB of data transfer out per month, far above demo traffic.
- **TLS and CI:** Let's Encrypt certificates via Caddy, GitHub Actions for public repositories, and GHCR for public images are free.

No prices, credits, or billing details are committed: hosting economics belong to deployers, per invariant 10 in this document.

### 5.3 Alternative: managed platform

If a single VM is unsuitable, the stack maps onto a managed platform without application changes:

| Concern | Reference | Alternative |
|---|---|---|
| Compute | AWS EC2 + compose | Managed container platform (e.g. Cloud Run, ECS Fargate) |
| Database | Self-hosted Postgres | Managed PostgreSQL with pgvector (e.g. Neon, RDS) |
| Storage | Local volume | S3-compatible object storage |
| Frontend | Vercel static SPA + CDN | Caddy same-origin build (no CORS) |

This path is supported by the interfaces in §9 and requires no application code changes.

---

## 6. Component architecture

### 6.1 Frontend

**React 19 + TypeScript + Vite + Tailwind CSS.**

| Concern | Choice |
|---|---|
| Data fetching | TanStack Query |
| Routing | React Router |
| API client | Generated from the FastAPI OpenAPI schema |
| Streaming | `fetch` + `ReadableStream` over Server-Sent Events |
| Component tests | Vitest + Testing Library |
| End-to-end | Playwright |
| Hosting | Static build on Vercel; API origin from `VITE_API_BASE_URL` at build time |

The generated client is a hard requirement: it allows frontend and backend contributors to work in parallel without coordinating on request shapes.

Key screens: document library with ingestion status, chat with streamed answers and inline citations, a sources panel, and a **retrieval inspector** that exposes top-k chunks, similarity scores, and context-budget trimming for the last query.

### 6.2 Backend

**Python 3.12 + FastAPI.**

| Concern | Choice | Note |
|---|---|---|
| ORM | SQLAlchemy 2.0, **synchronous** | Simpler for contributors; blocking work runs in a thread pool |
| Driver | psycopg 3 | |
| Migrations | Alembic | Required from the first commit |
| Validation | Pydantic v2 | |
| Settings | pydantic-settings | 12-factor, `.env` driven |
| Background work | FastAPI `BackgroundTasks` + status column | No broker in v0.1 |
| Logging | `structlog`, JSON in prod | Redaction filter installed at startup |

Synchronous SQLAlchemy is an intentional trade-off. The workload is I/O bound on the database and CPU bound on embeddings, and async sessions are a common source of silent bugs for new contributors. Blocking calls (embedding, parsing) are dispatched to a worker thread.

### 6.3 Background ingestion

Ingestion is a job with explicit, observable states rather than a synchronous request:

```
uploaded → parsing → chunking → embedding → indexed
                                      └──► failed (error_message)
```

The frontend polls `GET /documents/{id}` and renders status. `BackgroundTasks` is documented as single-process and non-durable; the `JobQueue` interface leaves room for Arq, Dramatiq, or Celery in a later release without touching call sites.

**Why not a broker in v0.1:** Redis and a worker container triple the setup surface for contributors and add two more failure modes to the demo, for a workload that a single node handles comfortably.

---

## 7. Data model

```mermaid
erDiagram
    users ||--o{ workspaces : owns
    workspaces ||--o{ documents : contains
    workspaces ||--o{ conversations : contains
    documents ||--o{ chunks : "is split into"
    conversations ||--o{ messages : contains
    messages ||--o{ message_citations : cites
    chunks ||--o{ message_citations : "referenced by"

    users {
        uuid id PK
        text email UK
        text password_hash
        text kind "user | guest"
        timestamptz created_at
    }
    workspaces {
        uuid id PK
        uuid user_id FK
        text name
        text embedding_model
        int embedding_dim
        timestamptz created_at
    }
    documents {
        uuid id PK
        uuid workspace_id FK
        text filename
        text content_type
        bigint size_bytes
        text storage_key
        text status
        text error_message
        text checksum_sha256
        timestamptz created_at
        timestamptz indexed_at
    }
    chunks {
        uuid id PK
        uuid document_id FK
        int ordinal
        text content
        int token_count
        jsonb metadata "page, heading, offset"
        vector embedding "384"
        timestamptz created_at
    }
    conversations {
        uuid id PK
        uuid workspace_id FK
        text title
        timestamptz created_at
    }
    messages {
        uuid id PK
        uuid conversation_id FK
        text role "user | assistant"
        text content
        text model
        int latency_ms
        timestamptz created_at
    }
    message_citations {
        uuid id PK
        uuid message_id FK
        uuid chunk_id FK
        float score
        int rank
    }
```

### 7.1 Notes

- **Chunk text lives in Postgres, not only in the vector index.** Citations are rendered without a vector-store round trip, and the index is fully rebuildable.
- `chunks.embedding` is `vector(384)` with an HNSW index using cosine distance. The dimension is fixed by `EMBEDDING_MODEL`; a mismatch is a startup error, not a runtime surprise.
- `workspaces.embedding_model` is written at creation. Mixing models within a workspace is rejected.
- `users.kind = 'guest'` supports anonymous demo sessions with a TTL purge (§13.4).
- `documents.checksum_sha256` enables idempotent re-upload and duplicate detection.

### 7.2 Indexing

| Index | Purpose |
|---|---|
| `chunks USING hnsw (embedding vector_cosine_ops)` | Approximate nearest neighbour search |
| `chunks (document_id)` | Citation joins, document deletion |
| `documents (workspace_id, status)` | Library listing, status polling |
| `documents (checksum_sha256)` | Duplicate detection |
| `users (email)` unique | Authentication |

---

## 8. RAG pipeline

### 8.1 Ingestion

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant S as Storage
    participant W as Worker (BackgroundTasks)
    participant E as Embedder
    participant D as Postgres/pgvector

    C->>A: POST /api/documents (multipart)
    A->>A: validate size, type, extension
    A->>S: write file (storage_key)
    A->>D: INSERT document (status=uploaded)
    A-->>C: 202 Accepted {id, status}
    A->>W: enqueue ingest(document_id)

    W->>D: status=parsing
    W->>S: read file
    W->>W: parse → blocks with metadata
    W->>D: status=chunking
    W->>W: chunk blocks (target 800 chars, 150 overlap)
    W->>D: status=embedding
    W->>E: embed batches of 32
    E-->>W: vectors (384-d)
    W->>D: INSERT chunks (+vectors)
    W->>D: status=indexed, indexed_at=now()
```

Failure at any stage sets `status=failed` and stores a bounded `error_message`. Partial chunks are deleted before the failure is recorded, so `indexed` always means fully indexed.

### 8.2 Query

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant E as Embedder
    participant D as Postgres/pgvector
    participant L as LLM (BYOK)

    C->>A: POST /api/chat {question, conversation_id}
    Note over C,A: X-Provider-Key header
    A->>E: embed(question)
    E-->>A: query vector (384-d)
    A->>D: SELECT ... ORDER BY embedding <=> $1 LIMIT k
    D-->>A: chunks + scores
    A->>A: filter by threshold, dedupe, trim to context budget
    A->>A: build prompt + citation map
    A->>L: stream completion (user key)
    L-->>A: tokens
    A-->>C: SSE token stream
    A->>D: persist message + citations
```

### 8.3 Parameters (defaults)

| Parameter | Default | Rationale |
|---|---|---|
| Chunk size | 800 characters | Fits a paragraph; leaves room for several chunks in context |
| Chunk overlap | 150 characters | Preserves sentence continuity across boundaries |
| Top-k retrieved | 8 | Balances recall against context cost |
| Minimum score | 0.30 cosine similarity | Filters clearly irrelevant chunks |
| Context budget | 6,000 tokens | Leaves headroom in most mid-size model contexts |
| Retrieved chunks in prompt | ≤ 8, ranked by score | Deterministic ordering for reproducible citations |

### 8.4 Prompting

The prompt is assembled in code, not in a template language, so contributors can read it end to end. It contains: a system instruction to answer only from context, numbered context blocks with document and page metadata, the user question, and an instruction to cite block numbers. Citations returned by the model are mapped back to `chunk_id` and persisted.

If retrieval yields nothing above the threshold, the API returns a grounded "not found in your documents" response without calling the LLM.

---

## 9. Provider abstractions

Every boundary is a small Protocol (or abstract base class) with at least two implementations: a real one and a fake.

```python
class EmbeddingProvider(Protocol):
    model: str
    dim: int
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...

class LLMProvider(Protocol):
    def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
    ) -> Iterator[Token]: ...

class VectorStore(Protocol):
    def upsert(self, chunks: list[ChunkRecord]) -> None: ...
    def search(self, vector: list[float], *, k: int, filters: Filters) -> list[ScoredChunk]: ...
    def delete_by_document(self, document_id: UUID) -> None: ...

class StorageBackend(Protocol):
    def put(self, key: str, data: BinaryIO) -> None: ...
    def get(self, key: str) -> BinaryIO: ...
    def delete(self, key: str) -> None: ...

class Parser(Protocol):
    supported_types: frozenset[str]
    def parse(self, data: BinaryIO) -> list[Block]: ...

class Chunker(Protocol):
    def chunk(self, blocks: list[Block]) -> list[Chunk]: ...
```

### 9.1 Implementations

| Interface | v0.1 | Later |
|---|---|---|
| `EmbeddingProvider` | `local` (sentence-transformers, CPU), `fake` | `openrouter`, `ollama` |
| `LLMProvider` | `openrouter`, `ollama`, `fake` | OpenAI-compatible, Gemini |
| `VectorStore` | `pgvector` | `qdrant` |
| `StorageBackend` | `local` | `s3` |
| `Parser` | `pdf`, `docx`, `markdown`, `text`, `html` | `csv`, `pptx`, `epub` |
| `Chunker` | `recursive`, `markdown` | `single`, `semantic` |
| `JobQueue` | `background_tasks` | `arq`, `dramatiq` |

### 9.2 Dependency shapes

The two credential models produce two different dependency shapes, and the asymmetry is enforced by types:

```python
# Server-owned singleton. No request context. Never accepts a credential.
def get_embedder() -> EmbeddingProvider: ...

# Request-scoped, credential-aware.
async def get_llm(request: Request) -> LLMProvider: ...
```

`get_embedder()` is module-scoped and loaded once at startup. It takes no `Request`. This is the single most important structural invariant in the codebase: it makes it impossible to accidentally pipe a user credential into the embedding path, and thereby impossible to index documents with a model the query path cannot reproduce.

---

## 10. Credential and secret model

### 10.1 The rule

> **If a step runs outside an HTTP request, it can never be BYOK.**

Ingestion runs after the upload response has returned, in a background task. There is no request to carry a key. Therefore every stage on the ingestion path must have a keyless, server-owned implementation.

A second constraint forces the same conclusion: query embeddings must come from the **same model** as document embeddings. Different models mean different dimensions and different vector spaces, so cross-model similarity is meaningless. A per-user embedding model would invalidate the index for every user.

### 10.2 Three credential tiers

| Tier | Definition | Applies to |
|---|---|---|
| **0 - keyless** | No credential of any kind | Parsing, chunking, embeddings, pgvector, prompt assembly, auth |
| **1 - BYOK** | Supplied by the user per request, used, discarded | Chat completion; later, reranking and web search |
| **2 - infrastructure** | Held by maintainers, in environment or CI secrets | SSH deploy key, Cloudflare token, backup target, GHCR |

There is **no tier for a maintainer-held model key.** RAGnarok never ships or stores a model provider key.

### 10.3 BYOK flow

```
Browser                         API                          Provider
  │                              │                              │
  │  POST /api/chat              │                              │
  │  X-Provider-Key: sk-or-...   │                              │
  ├─────────────────────────────►│                              │
  │                              │  read header                 │
  │                              │  build provider (ephemeral)  │
  │                              ├─────────────────────────────►│
  │                              │◄────── token stream ─────────┤
  │◄───── SSE tokens ────────────┤                              │
  │                              │  discard key                 │
  │                              │  never persist, never log    │
```

| Property | Implementation |
|---|---|
| Storage | `sessionStorage` in the browser; cleared when the tab closes |
| Transport | HTTPS only, custom header - never a query parameter |
| Server handling | Request-scoped only; not cached, not queued, not stored |
| Logging | Redaction filter strips `authorization` and `x-provider-key` |
| Error surfaces | Key never appears in responses, stack traces, or telemetry |
| Verification | A canary test asserts the key appears in zero log records (§16) |

### 10.4 Consequences

The credential model forbids a class of dependencies. These are **rejected by design**, not merely deferred:

- Cloud document parsers and OCR APIs (ingestion path, keyed).
- Managed vector databases (ingestion path, keyed).
- Hosted rerankers used during ingestion.
- Any provider-side feature requiring a server-held model key.

If scanned-PDF support is required, it is provided by a local OCR engine (Tesseract or Docling), not a hosted API.

---

## 11. API surface

Base path: `/api`. All endpoints are versioned implicitly by the application release; the OpenAPI schema is the contract.

| Method | Path | Auth | Key | Description |
|---|---|---|---|---|
| `GET` | `/health` | none | none | Liveness + DB readiness |
| `GET` | `/version` | none | none | Build SHA, model names |
| `POST` | `/auth/register` | none | none | Create account |
| `POST` | `/auth/login` | none | none | JWT pair |
| `POST` | `/auth/refresh` | none | none | Rotate access token |
| `GET` | `/auth/me` | JWT | none | Current user |
| `GET` | `/workspaces` | JWT | none | List workspaces |
| `POST` | `/workspaces` | JWT | none | Create workspace |
| `POST` | `/documents` | JWT | none | Multipart upload → `202` |
| `GET` | `/documents` | JWT | none | List with status |
| `GET` | `/documents/{id}` | JWT | none | Detail + status |
| `DELETE` | `/documents/{id}` | JWT | none | Cascade delete chunks |
| `GET` | `/documents/{id}/chunks` | JWT | none | Chunk inspector |
| `POST` | `/documents/{id}/reindex` | JWT | none | Re-run ingestion |
| `POST` | `/search` | JWT | none | Retrieval-only, no generation |
| `POST` | `/chat` | JWT | **BYOK** | JSON answer + citations |
| `GET` | `/conversations` | JWT | none | List |
| `GET` | `/conversations/{id}` | JWT | none | Messages + citations |

v1 implements `health`, `version`, `auth/register`, `auth/login`, `auth/me`, all
document rows except `reindex`, `search`, and `chat`. `auth/refresh`, workspaces,
reindex, and conversations are planned; chat returns one JSON response rather
than an SSE stream in v1.

Notes:

- `POST /search` returns ranked chunks and scores without generation. It powers the retrieval inspector, works without a key, and is the primary tool for debugging retrieval quality.
- `POST /chat` returns `401` with an explicit `provider_key_required` error code when no key is supplied, and the frontend renders guidance rather than a generic failure.
- Errors follow a single envelope: `{ "error": { "code": str, "message": str, "details": object | null } }`.
- The hosted SPA is cross-origin. API responses carry CORS headers only for an allowlisted origin; `OPTIONS` preflight permits `Authorization`, `Content-Type`, and `X-Provider-Key`; `Retry-After` is exposed. CORS never substitutes for token validation.

---

## 12. Configuration reference

All backend configuration is environment-based, validated at startup by pydantic-settings, and documented in `.env.example`; frontend build-time variables are supplied by the hosting project. Invalid configuration fails fast with an actionable message.

### 12.1 Core

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development` \| `production` \| `test` |
| `API_BASE_URL` | `http://localhost:8000` | Public base URL |
| `LOG_LEVEL` | `INFO` | |
| `LOG_FORMAT` | `console` | `console` \| `json` |

### 12.2 Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://ragnarok:ragnarok@db:5432/ragnarok` | Must not point at a remote host outside the demo |

### 12.3 Storage

| Variable | Default | Description |
|---|---|---|
| `STORAGE_BACKEND` | `local` | `local` \| `s3` |
| `STORAGE_PATH` | `/data/uploads` | Used when `local` |
| `MAX_UPLOAD_MB` | `10` | Enforced before reading the body |
| `ALLOWED_MIME_TYPES` | `text/plain,text/markdown` | |

### 12.4 Embeddings

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_PROVIDER` | `local` | `local` \| `openrouter` \| `fake` |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | 384 dimensions |
| `EMBEDDING_DIM` | `384` | Validated against the loaded model |
| `EMBEDDING_BATCH_SIZE` | `32` | |

### 12.5 Generation

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openrouter` | `openrouter` \| `ollama` \| `fake`; dev compose forces `fake`, prod compose forces `openrouter` |
| `LLM_MODEL` | `openrouter/auto` | |
| `LLM_TEMPERATURE` | `0.2` | |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | |
| `ALLOW_SERVER_LLM_KEY` | `false` | Enables a server-side key for the demo only |

### 12.6 Retrieval

| Variable | Default | Description |
|---|---|---|
| `RETRIEVAL_TOP_K` | `8` | |
| `RETRIEVAL_MIN_SCORE` | `0.30` | |
| `CONTEXT_MAX_TOKENS` | `6000` | |

### 12.7 Auth and sessions

| Variable | Default | Description |
|---|---|---|
| `AUTH_DISABLED` | `true` | Local development only |
| `JWT_SECRET` | - | Required when `AUTH_DISABLED=false` |
| `JWT_EXPIRE_MINUTES` | `60` | |
| `GUEST_SESSION_TTL_HOURS` | `168` | 7-day purge window |
| `MAX_DOCS_PER_SESSION` | `5` | |

### 12.8 Rate limiting

| Variable | Default | Description |
|---|---|---|
| `RATE_LIMIT_CHAT_PER_MIN` | `10` | Per session |
| `RATE_LIMIT_UPLOAD_PER_MIN` | `3` | Per session |

### 12.9 Hosted SPA and CORS

| Variable | Default | Description |
|---|---|---|
| `ALLOWED_ORIGINS` | *(empty)* | Comma-separated exact browser origins allowed to call the API. Required when `APP_ENV=production`; production sets the Vercel production origin, and preview deployments are visual-only unless their origin is added. Never `*`. |
| `VITE_API_BASE_URL` | `/api` | Frontend build-time API base. `/api` locally (Vite proxy); `https://api.<host>/api` on Vercel. Not read by `Settings`. |

`ALLOWED_ORIGINS` is an allowlist, not an authentication mechanism. A request from an unlisted origin receives no CORS headers; state-changing endpoints also reject a mismatched `Origin`.

---

## 13. Security architecture

### 13.1 Credential handling

- Redaction filter installed on the root logger at startup, before any handler is attached.
- Access log middleware strips `authorization`, `x-provider-key`, and `cookie` before emission.
- Caddy is configured **not** to log request headers.
- No telemetry SDK is enabled by default; if added, `send_default_pii=false` and breadcrumbs disabled.
- Canary test: a request carrying a known sentinel key must produce zero matching log records.

### 13.2 Upload handling

- Size limit enforced before the body is read.
- MIME type and extension both validated; the parser is selected by content type, not filename alone.
- Storage keys are generated server-side UUIDs; user-supplied filenames are never used as paths (prevents traversal).
- Parsing runs in a worker thread with a per-document timeout.
- Archive bombs and deeply nested structures are rejected at the parser boundary.

### 13.3 Authentication

- Argon2id password hashing.
- Short-lived access tokens, rotating refresh tokens.
- All resource queries scoped by `workspace.user_id`; ownership is enforced in the repository layer, not the route handler.
- `AUTH_DISABLED=true` is rejected when `APP_ENV=production`.

### 13.4 Guest sessions (public demo)

- Local same-origin runs may use an httpOnly, `SameSite=Lax`, `Secure` session cookie.
- The hosted demo is **cross-site**: `<app>.vercel.app` and the API host are different registrable domains, and Safari's ITP and Firefox's Total Cookie Protection block third-party cookies even with `SameSite=None`. Hosted guest sessions therefore use a signed bearer token returned by the API and held in `sessionStorage`; requests carry it in the `Authorization` header. The provider key is never persisted.
- A synthetic `users` row with `kind='guest'` and one workspace is created per session.
- Nightly job purges guest users, and cascades remove documents, chunks, and uploads.
- The UI states plainly that uploads are stored on the demo server and deleted after 7 days.

Hosted sessions are bearer-token based regardless of domain layout; cookie sessions are reserved for local same-origin runs.

### 13.5 Application

- CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, HSTS. Caddy sets them on API responses; Vercel sets the SPA's headers in `frontend/vercel.json`, where `connect-src` names the API origin.
- Mutating endpoints reject requests whose `Origin` is not in `ALLOWED_ORIGINS`, in addition to token validation.
- Server-side rate limits on chat and upload per session, in addition to any edge limiting.
- Dependency and container scanning in CI.
- Branch protection with required checks; no direct pushes to `main`.

---

## 14. Failure modes and degradation

| Condition | Behaviour | User-visible result |
|---|---|---|
| No `X-Provider-Key` on `/chat` | No provider call | `401 provider_key_required` with setup guidance |
| Provider returns 429 | Pass through `Retry-After` | "Rate limited, retry in Ns" |
| Provider returns 5xx | One retry with jitter, then fail | `502 provider_unavailable` |
| Key rejected (401 from provider) | Do not retry | `401 invalid_provider_key` with "check your key" |
| Retrieval returns nothing above threshold | Skip LLM call entirely | Grounded "not found in your documents" |
| Embedding model dimension ≠ config | Startup fails | Container exits with explicit message |
| Postgres unavailable | Healthcheck fails, `503` | "Service unavailable" |
| Upload exceeds limit | Rejected before read | `413 payload_too_large` |
| Parse timeout | Job fails, partial chunks removed | Document shows `failed` with reason |
| Provider slow / stream stalls | Idle timeout, SSE closed | Partial answer retained, marked incomplete |
| Guest TTL expired | Session recreated empty | No data loss for the user; demo resets |
| Request from an origin not in `ALLOWED_ORIGINS` | No CORS headers; mutations rejected | Browser blocks the call; server logs the origin |
| Guest token missing or invalid | New guest session issued | Demo resets to an empty workspace |

**Principle:** degraded behaviour is always *legible*. No endpoint returns a bare 500 when a specific, actionable error exists.

---

## 15. Performance targets

Measured on the reference 2-vCPU ARM VM.

| Metric | Target |
|---|---|
| Cold start (container → first request served) | < 10 s |
| Embedding model load (once, at startup) | < 8 s |
| Chunk embedding throughput | ≥ 40 chunks/s |
| Ingestion, 20-page PDF | < 25 s |
| Retrieval latency (p95, 10k chunks) | < 150 ms |
| Time to first token | < 2 s (provider-dependent) |
| Frontend initial load (gzipped) | < 250 KB |

Retrieval performance relies on the HNSW index; without it, brute-force cosine scan dominates at roughly 10k chunks.

---

## 16. Testing strategy

| Layer | Tool | Scope | Runtime |
|---|---|---|---|
| Unit | pytest | Parsers, chunkers, prompt assembly, redaction, config validation | < 10 s |
| Integration | pytest + compose Postgres | Repositories, migrations, pgvector search | < 60 s |
| Contract | pytest + OpenAPI snapshot | Request/response schema stability | < 5 s |
| Frontend unit | Vitest + Testing Library | Components, hooks, formatting | < 30 s |
| End-to-end | Playwright | Upload → index → ask → citations | < 3 min |
| Canary | pytest | Credentials never appear in logs | < 1 s |

### 16.1 Fake providers

`LLM_PROVIDER=fake` and `EMBEDDING_PROVIDER=fake` are first-class, not test-only hacks:

- Deterministic, hash-based embeddings with the correct dimension (stable ordering in tests).
- Scriptable LLM responses, including streaming and citations.
- Enable **zero-secret CI**, so fork PRs and first-time contributors run the full suite without configuration.

This is the property that makes 150 contributors tractable: no contributor needs a credential to get a green build.

### 16.2 Migration discipline

CI asserts that:

- `alembic heads` returns exactly one head.
- `alembic upgrade head` succeeds from an empty database.
- `downgrade -1 && upgrade head` round-trips.

---

## 17. Observability

| Concern | v0.1 |
|---|---|
| Logging | Structured JSON, request ID propagated from `X-Request-ID` or generated |
| Metrics | `/health` and `/version`; no metrics backend |
| Tracing | Disabled by default; OpenTelemetry stub behind a flag |
| RAG inspection | `GET /documents/{id}/chunks` and `POST /search` are the debugging surface |

The retrieval endpoints double as the observability story: they expose exactly what the pipeline saw, without a separate tracing stack. Adding a hosted tracing backend later is a provider behind a flag, not an architectural change.

---

## 18. Repository layout

```
ragnarok/
├── .github/
│   ├── workflows/          ci-api.yml, ci-web.yml, docker.yml, nightly.yml
│   ├── ISSUE_TEMPLATE/
│   └── CODEOWNERS
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   ├── errors.py
│   │   │   └── routes/     auth.py, documents.py, chat.py, search.py,
│   │   │                   conversations.py, workspaces.py, health.py
│   │   ├── core/           config.py, security.py, logging.py, redaction.py
│   │   ├── db/             session.py, base.py, models/, repositories/
│   │   ├── parsers/        base.py, pdf.py, docx.py, markdown.py, text.py,
│   │   │                   html.py, registry.py
│   │   ├── chunking/       base.py, recursive.py, markdown.py, registry.py
│   │   ├── embeddings/     base.py, local.py, openrouter.py, fake.py
│   │   ├── llm/            base.py, openrouter.py, ollama.py, fake.py
│   │   ├── vector/         base.py, pgvector.py
│   │   ├── storage/        base.py, local.py, s3.py
│   │   ├── ingestion/      pipeline.py, jobs.py, status.py
│   │   ├── rag/            retriever.py, context.py, prompt.py, citations.py
│   │   └── schemas/
│   ├── alembic/versions/
│   ├── tests/              unit/, integration/, e2e/, canary/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/            router.tsx, providers.tsx
│   │   ├── api/            generated/, client.ts, streaming.ts
│   │   ├── components/     ui/, chat/, documents/, sources/
│   │   ├── features/       chat/, documents/, settings/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── pages/
│   ├── tests/
│   ├── Dockerfile
│   ├── vercel.json        SPA rewrite + security headers
│   └── package.json
├── infra/
│   ├── compose.yml         # base: db, api, web
│   ├── compose.prod.yml    # prod profile: db, api, caddy (API-only edge)
│   ├── Caddyfile
│   └── deploy/             aws-ec2.md, vercel.md
├── planning/
│   └── issues.yml          # issue manifest → scripts/publish_issues.py
├── scripts/                publish_issues.py, seed.py, backup.sh
├── docs/                   architecture.md, adr/, onboarding/
├── justfile
├── docker-compose.yml → infra/compose.yml
├── .env.example
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE
```

The layout is deliberately flat rather than a monorepo workspace. Two applications, one infra directory, no workspace tooling to explain.

---

## 19. Decision log

| # | Decision | Alternatives considered | Rationale | Consequence |
|---|---|---|---|---|
| D1 | Postgres is the source of truth; vectors are derived | Qdrant as primary store | Index is rebuildable; citations need text anyway; one backup story | Re-embedding costs on model change |
| D2 | pgvector in v0.1, Qdrant in v0.2 | Qdrant from day one | One datastore for contributors; faster onboarding | `VectorStore` interface required from day one |
| D3 | Local embeddings (bge-small, CPU) | Remote embeddings via OpenRouter | Keyless ingestion; identical doc/query model; works with no account | CPU cost on the reference VM; fixed 384 dimensions |
| D4 | BYOK for generation only | Server-held key; server-side encrypted key storage | No key liability; no shared credential to abuse; aligns with open-source norms | First-time demo visitor cannot generate without a key |
| D5 | Synchronous SQLAlchemy | Async SQLAlchemy | Fewer concurrency bugs for contributors | Blocking work must be threaded explicitly |
| D6 | `BackgroundTasks` for ingestion | Celery, Arq, Dramatiq | No broker, no extra container | Not durable; documented; `JobQueue` interface reserved |
| D7 | Single AWS EC2 Graviton VM for the API and database | Managed container platform + managed Postgres | Dev/prod parity, one compose file, same ARM64 images as CI, one billable resource | Single point of failure; manual ops; the SPA is hosted separately (D13) |
| D8 | Frontend served same-origin by Caddy *(superseded by D13)* | Vercel / Cloudflare Pages | No CORS, no cross-site cookies, one TLS setup | No CDN; frontend rebuild deploys with the stack. Caddy remains the local and fallback SPA host. |
| D9 | Generated TypeScript client from OpenAPI | Hand-written client | Frontend and backend PRs never block each other | Requires schema stability in CI |
| D10 | No LangChain / LlamaIndex | Framework orchestration | The pipeline is the teaching material; stable dependencies | More code to own (~300 lines) |
| D11 | Fake providers as production code | Test-only mocks | Zero-secret CI; 150 contributors without credentials | Fake implementations must track real interfaces |
| D12 | Atomic issue decomposition with pre-written skipped tests | Contributors write tests and implementations | Tests become the specification; PRs are reviewable | ~40 hours of maintainer scaffolding per 150 issues |
| D13 | Vercel Hobby hosts the SPA; the API and database stay on the EC2 VM | Caddy same-origin (D8); Cloudflare Pages; serverless API | Free CDN, per-PR previews, and no API runtime split; the static build is the only second build path | Cross-origin CORS and preflight; bearer guest sessions instead of third-party cookies; Hobby is non-commercial and may be suspended; `frontend/vercel.json` SPA rewrite required |

---

## 20. Roadmap

### v0.1 - Walking skeleton

Document upload (PDF, DOCX, Markdown, text, HTML), ingestion with status, pgvector retrieval, streamed answers with citations, retrieval inspector, local auth, compose, CI, reference deployment. This walking skeleton is the baseline for the 150 Git Together contributor issues. Later roadmap items are not required to finish an issue.

### v0.2 - Retrieval quality

Qdrant as an alternative `VectorStore`. Hybrid search (Postgres `tsvector` + vectors) with reciprocal rank fusion. Local cross-encoder reranking. Chunking strategy selection per document.

### v0.3 - Evaluation

Golden-question fixtures, recall@k and answer-grounding metrics, a CI report on retrieval regressions. This is the feature that distinguishes a teaching repository from a demo.

### v0.4 - Scale and operations

Durable job queue, S3 storage backend, tracing backend, multi-workspace sharing.

---

## 21. Open questions

| # | Question | Owner | Blocks |
|---|---|---|---|
| Q1 | Does the public demo issue guest sessions or require email signup? | Maintainers | §13.4 |
| Q2 | Should a strictly rate-limited server key be offered for first-touch demos? | Maintainers | §10.2 |
| Q3 | Which default LLM model is used for the demo? | Maintainers | §12.5 |
| Q5 | Backup retention window and restore-drill cadence | Maintainers | §5.2 |

Q4 (CDN vs. same-origin) is closed by D13: the hosted SPA is served from Vercel's CDN.

---

*This document is the authoritative description of system structure. Changes to any decision marked Accepted require an ADR in `docs/adr/` before implementation.*
