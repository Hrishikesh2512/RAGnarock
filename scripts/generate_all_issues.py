#!/usr/bin/env python3
"""Generate the complete 150-issue manifest in planning/issues.yml.
Divides work into the 8 roadmap milestones with clear specs, acceptance tests, and labels.
"""

from pathlib import Path
import yaml

M0_ISSUES = [
    {
        "id": "m0-readme-onboarding",
        "milestone": "M0",
        "title": "docs: add getting started walk-through and troubleshooting to README",
        "labels": ["docs", "good first issue"],
        "spec_section": "1",
        "files_to_touch": ["README.md"],
        "acceptance_test": "test -f README.md",
        "description": "Expand root README.md with detailed platform-specific notes (Windows WSL2 vs Docker Desktop) and quick verification guide."
    },
    {
        "id": "m0-contributing-guide-pr-flow",
        "milestone": "M0",
        "title": "docs: add step-by-step fork, branch, and PR guide to CONTRIBUTING.md",
        "labels": ["docs", "good first issue"],
        "spec_section": "18",
        "files_to_touch": ["CONTRIBUTING.md"],
        "acceptance_test": "test -f CONTRIBUTING.md",
        "description": "Add an explicit git branching and rebase guide in CONTRIBUTING.md aimed at first-time open-source contributors."
    },
    {
        "id": "m0-justfile-recipes",
        "milestone": "M0",
        "title": "infra: add database reset and seed recipes to justfile",
        "labels": ["infra", "good first issue"],
        "spec_section": "18",
        "files_to_touch": ["justfile"],
        "acceptance_test": "just --list",
        "description": "Add a 'seed' recipe to justfile that inserts a test document and runs ingestion."
    },
    {
        "id": "m0-ci-workflow-timeout",
        "milestone": "M0",
        "title": "ci: enforce strict 10-minute job timeouts on all GitHub Actions workflows",
        "labels": ["infra"],
        "spec_section": "16",
        "files_to_touch": [".github/workflows/ci-api.yml", ".github/workflows/ci-web.yml"],
        "acceptance_test": "grep -r 'timeout-minutes' .github/workflows/",
        "description": "Add timeout-minutes: 10 to every job in ci-api.yml and ci-web.yml to prevent hanging runners."
    },
    {
        "id": "m0-dependabot-config",
        "milestone": "M0",
        "title": "ci: add Dependabot configuration for GitHub Actions and pip/npm",
        "labels": ["infra", "good first issue"],
        "spec_section": "16",
        "files_to_touch": [".github/dependabot.yml"],
        "acceptance_test": "test -f .github/dependabot.yml",
        "description": "Configure Dependabot to check weekly for GitHub Actions, backend python packages, and frontend npm packages."
    },
    {
        "id": "m0-ruff-b008-exemption-test",
        "milestone": "M0",
        "title": "backend: assert Ruff B008 FastAPI Depends exemption in pyproject.toml",
        "labels": ["backend"],
        "spec_section": "18",
        "files_to_touch": ["backend/pyproject.toml"],
        "acceptance_test": "cd backend && uv run ruff check app",
        "description": "Ensure B008 is properly ignored for Depends and File across all FastAPI routes."
    },
    {
        "id": "m0-frontend-lint-staged",
        "milestone": "M0",
        "title": "frontend: add typecheck npm script and verify strict tsconfig",
        "labels": ["frontend", "good first issue"],
        "spec_section": "18",
        "files_to_touch": ["frontend/package.json", "frontend/tsconfig.json"],
        "acceptance_test": "cd frontend && npm run typecheck",
        "description": "Verify that npm run typecheck runs tsc with noEmit and strict null checks enabled."
    },
    {
        "id": "m0-dockerignore-cleanup",
        "milestone": "M0",
        "title": "infra: audit and standardize .dockerignore across backend and frontend",
        "labels": ["infra", "good first issue"],
        "spec_section": "18",
        "files_to_touch": [".dockerignore", "backend/.dockerignore"],
        "acceptance_test": "docker build --no-cache -f backend/Dockerfile backend",
        "description": "Exclude .mypy_cache, .pytest_cache, tests/, and local .env files from the Docker context."
    },
    {
        "id": "m0-editorconfig-standardization",
        "milestone": "M0",
        "title": "docs: add .editorconfig enforcing UTF-8 and trailing newlines",
        "labels": ["docs", "good first issue"],
        "spec_section": "18",
        "files_to_touch": [".editorconfig"],
        "acceptance_test": "test -f .editorconfig",
        "description": "Add an .editorconfig file standardizing 2-space indentation for web/yaml and 4-space for python."
    },
    {
        "id": "m0-env-example-validation",
        "milestone": "M0",
        "title": "backend: add test verifying every field in Settings exists in .env.example",
        "labels": ["backend", "test"],
        "spec_section": "12",
        "files_to_touch": ["backend/tests/test_config.py"],
        "acceptance_test": "cd backend && uv run pytest tests/test_config.py",
        "description": "Assert that every setting defined in app.core.config.Settings has a corresponding key in .env.example."
    },
    {
        "id": "m0-github-pr-template-labels",
        "milestone": "M0",
        "title": "docs: enhance PULL_REQUEST_TEMPLATE with testing checklist and spec tags",
        "labels": ["docs", "good first issue"],
        "spec_section": "18",
        "files_to_touch": [".github/PULL_REQUEST_TEMPLATE.md"],
        "acceptance_test": "test -f .github/PULL_REQUEST_TEMPLATE.md",
        "description": "Update the PR template with explicit check-boxes for linting, typing, and documentation updates."
    },
    {
        "id": "m0-pre-commit-hooks-setup",
        "milestone": "M0",
        "title": "infra: add optional .pre-commit-config.yaml for local development",
        "labels": ["infra", "good first issue"],
        "spec_section": "18",
        "files_to_touch": [".pre-commit-config.yaml"],
        "acceptance_test": "test -f .pre-commit-config.yaml",
        "description": "Add a pre-commit config running ruff check, ruff format, and eslint for contributors who want git hook integration."
    },
    {
        "id": "m0-ci-workflow-concurrency-cancel",
        "milestone": "M0",
        "title": "ci: ensure all workflows cancel in-progress runs on new commits",
        "labels": ["infra"],
        "spec_section": "16",
        "files_to_touch": [".github/workflows/ci-api.yml", ".github/workflows/ci-web.yml"],
        "acceptance_test": "grep -r 'cancel-in-progress: true' .github/workflows/",
        "description": "Add concurrency group with cancel-in-progress to save GitHub Actions runner minutes."
    },
    {
        "id": "m0-caddyfile-syntax-check",
        "milestone": "M0",
        "title": "infra: add caddy validate check to CI pipeline",
        "labels": ["infra"],
        "spec_section": "18",
        "files_to_touch": [".github/workflows/docker.yml"],
        "acceptance_test": "caddy validate --config infra/Caddyfile",
        "description": "Ensure changes to infra/Caddyfile are validated for correct syntax in CI."
    },
    {
        "id": "m0-architecture-doc-versioning",
        "milestone": "M0",
        "title": "docs: verify version and date headers in docs/architecture.md",
        "labels": ["docs", "good first issue"],
        "spec_section": "1",
        "files_to_touch": ["docs/architecture.md"],
        "acceptance_test": "grep 'Version' docs/architecture.md",
        "description": "Verify architecture document header matches the latest release tag."
    }
]

def make_issues(prefix, milestone, count, template_func):
    return [template_func(prefix, milestone, i + 1) for i in range(count)]

def m1_gen(p, m, idx):
    titles = [
        ("define VectorStore protocol abstraction", "backend", "9.1", ["backend/app/rag/store.py"], "test_vector_store.py"),
        ("implement PgVectorStore adhering to VectorStore protocol", "backend", "9.1", ["backend/app/rag/pgvector.py"], "test_pgvector_store.py"),
        ("formalize EmbeddingProvider protocol with async/sync typing", "backend", "9.2", ["backend/app/embeddings/base.py"], "test_embeddings.py"),
        ("create Chunker registry and strategy selector", "backend", "8.1", ["backend/app/ingestion/chunker.py"], "test_chunker.py"),
        ("validate Document status state machine transitions", "backend", "6.3", ["backend/app/ingestion/pipeline.py"], "test_ingestion_status.py"),
        ("update FakeProvider to yield deterministic token streams", "backend", "9.3", ["backend/app/llm/fake.py"], "test_llm.py"),
        ("extract inline citation markers [n] from LLM response", "backend", "8.3", ["backend/app/rag/prompt.py"], "test_prompt.py"),
        ("ensure document deletion deletes local file storage and chunk rows", "backend", "7.2", ["backend/app/api/routes/documents.py"], "test_document_delete.py"),
        ("add document size validation before writing to disk", "backend", "13.2", ["backend/app/api/routes/documents.py"], "test_upload_limits.py"),
        ("support UTF-8 BOM encoding gracefully in chunker", "backend", "8.1", ["backend/app/ingestion/chunker.py"], "test_chunker.py"),
        ("add HNSW index distance metric verification in alembic", "backend", "7.3", ["backend/alembic/versions/0001_initial.py"], "test_alembic.py"),
        ("implement query embedding caching for repeated search terms", "backend", "8.2", ["backend/app/rag/retriever.py"], "test_retriever.py"),
        ("sanitize filename strings against directory traversal attacks", "backend", "13.2", ["backend/app/api/routes/documents.py"], "test_documents.py"),
        ("add retrieval_min_score filtering to similarity searches", "backend", "8.2", ["backend/app/rag/retriever.py"], "test_retriever.py"),
        ("return 404 for non-existent document chunk inspection queries", "backend", "11.3", ["backend/app/api/routes/documents.py"], "test_documents.py"),
        ("enforce max document name length of 255 characters", "backend", "7.1", ["backend/app/db/models/document.py"], "test_documents.py"),
        ("log document processing duration in ingestion background task", "backend", "17", ["backend/app/ingestion/pipeline.py"], "test_ingestion.py"),
        ("add database session commit retry on concurrency conflict", "backend", "7.1", ["backend/app/db/session.py"], "test_db.py"),
        ("support empty query search gracefully returning zero results", "backend", "11.5", ["backend/app/api/routes/search.py"], "test_search.py"),
        ("enforce strict uuid validation on document id path parameter", "backend", "11.3", ["backend/app/api/routes/documents.py"], "test_documents.py"),
        ("add custom repr to Chunk model hiding raw high-dim vector", "backend", "7.1", ["backend/app/db/models/chunk.py"], "test_models.py"),
        ("assert pgvector vector extension exists during application startup", "backend", "7.3", ["backend/app/main.py"], "test_health.py"),
        ("add structured error detail dictionary to ApiError response", "backend", "14", ["backend/app/api/errors.py"], "test_errors.py"),
        ("validate embedding model vector dimension against EMBEDDING_DIM", "backend", "12.4", ["backend/app/embeddings/local.py"], "test_embeddings.py"),
        ("add unit test asserting FakeEmbedder returns normalized unit vectors", "backend", "16", ["backend/tests/test_embeddings.py"], "test_embeddings.py"),
        ("prevent duplicate chunk index numbers for a single document", "backend", "7.1", ["backend/app/db/models/chunk.py"], "test_models.py"),
        ("handle database connection drops gracefully with pool_pre_ping", "backend", "6.2", ["backend/app/db/session.py"], "test_session.py"),
        ("record total token count in chunk model during ingestion", "backend", "7.1", ["backend/app/ingestion/pipeline.py"], "test_ingestion.py"),
        ("add health check query verifying postgres connection readiness", "backend", "11.1", ["backend/app/api/routes/health.py"], "test_health.py"),
        ("document status enum type safety in database and pydantic", "backend", "7.1", ["backend/app/schemas/documents.py"], "test_documents.py"),
    ]
    t, lbl, spec, files, test_file = titles[(idx - 1) % len(titles)]
    return {
        "id": f"{p}-{idx:02d}",
        "milestone": m,
        "title": f"backend: {t}",
        "labels": [lbl] + (["good first issue"] if idx % 2 == 0 else []),
        "spec_section": spec,
        "files_to_touch": files,
        "acceptance_test": f"cd backend && uv run pytest tests/{test_file}",
        "description": f"Implement {t} according to section {spec} of docs/architecture.md."
    }

def m2_gen(p, m, idx):
    titles = [
        ("implement Server-Sent Events (SSE) streaming for POST /api/chat", "backend", "11.4", ["backend/app/api/routes/chat.py"], "test_chat_stream.py"),
        ("implement one retry with jitter on OpenRouter 502/503/429", "backend", "14", ["backend/app/llm/openrouter.py"], "test_openrouter_retry.py"),
        ("trim retrieved passages to CONTEXT_MAX_TOKENS", "backend", "8.2", ["backend/app/rag/prompt.py"], "test_prompt_trimming.py"),
        ("add canary test asserting X-Provider-Key never appears in logs", "backend", "13.1", ["backend/app/core/logging.py"], "test_logging_redaction.py"),
        ("add local Ollama LLM provider behind LLMProvider protocol", "backend", "9.3", ["backend/app/llm/ollama.py"], "test_ollama.py"),
        ("handle OpenRouter idle timeout after 60 seconds", "backend", "14", ["backend/app/llm/openrouter.py"], "test_llm.py"),
        ("map OpenRouter 401 response to invalid_provider_key ApiError", "backend", "14", ["backend/app/llm/openrouter.py"], "test_llm.py"),
        ("extract top-k relevant chunks and format with clear citation index headers", "backend", "8.3", ["backend/app/rag/prompt.py"], "test_prompt.py"),
        ("add unit tests verifying prompt builder orders passages by similarity", "backend", "8.3", ["backend/tests/test_prompt.py"], "test_prompt.py"),
        ("support system prompt customization via SYSTEM_PROMPT environment setting", "backend", "12.5", ["backend/app/core/config.py"], "test_config.py"),
        ("stream partial answer tokens with SSE data: JSON payloads", "backend", "11.4", ["backend/app/api/routes/chat.py"], "test_chat_stream.py"),
        ("emit citation event at end of SSE completion stream", "backend", "11.4", ["backend/app/api/routes/chat.py"], "test_chat_stream.py"),
        ("pass request-scoped timeout to httpx client in OpenRouterProvider", "backend", "9.3", ["backend/app/llm/openrouter.py"], "test_llm.py"),
        ("add fallback message when retriever finds zero matching chunks", "backend", "8.3", ["backend/app/rag/prompt.py"], "test_prompt.py"),
        ("strip Markdown code blocks from generated citation strings", "backend", "8.3", ["backend/app/rag/prompt.py"], "test_prompt.py"),
        ("assert LLM provider temperature parameter is strictly between 0.0 and 2.0", "backend", "12.5", ["backend/app/core/config.py"], "test_config.py"),
        ("validate LLM model name format preventing header injection", "backend", "13.1", ["backend/app/llm/openrouter.py"], "test_llm.py"),
        ("implement OpenRouter usage token count extraction in response headers", "backend", "9.3", ["backend/app/llm/openrouter.py"], "test_llm.py"),
        ("handle client disconnect gracefully during streaming chat completion", "backend", "11.4", ["backend/app/api/routes/chat.py"], "test_chat_stream.py"),
        ("add benchmark test for prompt building overhead under 100 chunks", "backend", "15", ["backend/tests/test_prompt.py"], "test_prompt.py"),
    ]
    t, lbl, spec, files, test_file = titles[(idx - 1) % len(titles)]
    return {
        "id": f"{p}-{idx:02d}",
        "milestone": m,
        "title": f"backend: {t}",
        "labels": [lbl] + (["good first issue"] if idx % 3 == 0 else []),
        "spec_section": spec,
        "files_to_touch": files,
        "acceptance_test": f"cd backend && uv run pytest tests/{test_file}",
        "description": f"Implement {t} according to section {spec} of docs/architecture.md."
    }

def m3_gen(p, m, idx):
    titles = [
        ("implement rotating refresh tokens for JWT authentication", "backend", "10", ["backend/app/core/security.py"], "test_refresh_token.py"),
        ("add memory-based rate limiting with 429 Retry-After headers", "backend", "12.8", ["backend/app/api/middleware/rate_limit.py"], "test_rate_limit.py"),
        ("support guest sessions via HttpOnly SameSite=Lax cookie", "backend", "13.4", ["backend/app/api/deps.py"], "test_guest_session.py"),
        ("enforce workspace-level document ownership filters", "backend", "7.1", ["backend/app/db/models/document.py"], "test_workspace_isolation.py"),
        ("validate password strength requiring min 8 chars with mixed case", "backend", "13.3", ["backend/app/core/security.py"], "test_security.py"),
        ("hash user passwords with Argon2id using recommended OWASP parameters", "backend", "13.3", ["backend/app/core/security.py"], "test_security.py"),
        ("prevent email enumeration by timing-safe password verification", "backend", "13.3", ["backend/app/api/routes/auth.py"], "test_auth.py"),
        ("implement token revocation blacklist for user logout", "backend", "10", ["backend/app/core/security.py"], "test_security.py"),
        ("add background purge task for guest sessions older than 7 days", "backend", "13.4", ["backend/app/tasks/purge.py"], "test_purge.py"),
        ("return 401 invalid_token when JWT signature check fails", "backend", "10", ["backend/app/core/security.py"], "test_security.py"),
        ("support MAX_DOCS_PER_SESSION upload limit for guest users", "backend", "12.7", ["backend/app/api/routes/documents.py"], "test_upload_limits.py"),
        ("add rate limit bypass whitelist for internal loopback health checks", "backend", "12.8", ["backend/app/api/middleware/rate_limit.py"], "test_rate_limit.py"),
        ("enforce strict bearer token extraction ignoring case in authorization header", "backend", "10", ["backend/app/api/deps.py"], "test_deps.py"),
        ("add auth disabled warning log on server startup in non-dev env", "backend", "12.7", ["backend/app/main.py"], "test_config.py"),
        ("return 409 email_taken when registering an existing email address", "backend", "11.2", ["backend/app/api/routes/auth.py"], "test_auth.py"),
        ("expire access tokens strictly after JWT_EXPIRE_MINUTES", "backend", "12.7", ["backend/app/core/security.py"], "test_security.py"),
        ("enforce lowercase email normalization on registration and login", "backend", "11.2", ["backend/app/api/routes/auth.py"], "test_auth.py"),
        ("add user account deletion endpoint with cascading document cleanup", "backend", "11.2", ["backend/app/api/routes/auth.py"], "test_auth.py"),
        ("support X-Forwarded-For header in IP rate limiter behind reverse proxy", "backend", "12.8", ["backend/app/api/middleware/rate_limit.py"], "test_rate_limit.py"),
        ("add unit tests for argon2id password verification failure modes", "backend", "16", ["backend/tests/test_security.py"], "test_security.py"),
    ]
    t, lbl, spec, files, test_file = titles[(idx - 1) % len(titles)]
    return {
        "id": f"{p}-{idx:02d}",
        "milestone": m,
        "title": f"backend: {t}",
        "labels": [lbl] + (["good first issue"] if idx % 2 == 0 else []),
        "spec_section": spec,
        "files_to_touch": files,
        "acceptance_test": f"cd backend && uv run pytest tests/{test_file}",
        "description": f"Implement {t} according to section {spec} of docs/architecture.md."
    }

def m4_gen(p, m, idx):
    titles = [
        ("implement pypdf document parser with page attribution", "backend", "8.1", ["backend/app/ingestion/parsers/pdf.py"], "test_pdf_parser.py"),
        ("implement DOCX parser using python-docx", "backend", "8.1", ["backend/app/ingestion/parsers/docx.py"], "test_docx_parser.py"),
        ("parse HTML documents with BeautifulSoup stripping scripts and styles", "backend", "8.1", ["backend/app/ingestion/parsers/html.py"], "test_html_parser.py"),
        ("detect duplicate document uploads via SHA-256 hash", "backend", "13.2", ["backend/app/api/routes/documents.py"], "test_duplicate_upload.py"),
        ("enforce MAX_UPLOAD_MB before buffering payload into memory", "backend", "13.2", ["backend/app/api/routes/documents.py"], "test_upload_limits.py"),
        ("detect and reject encrypted or password-protected PDF files", "backend", "14", ["backend/app/ingestion/parsers/pdf.py"], "test_pdf_parser.py"),
        ("reject scanned zero-text PDFs with informative no_extractable_text error", "backend", "14", ["backend/app/ingestion/parsers/pdf.py"], "test_pdf_parser.py"),
        ("add per-document parse timeout of 30 seconds to kill runaway parsers", "backend", "13.2", ["backend/app/ingestion/pipeline.py"], "test_ingestion.py"),
        ("clean up partial chunks in database when ingestion fails midway", "backend", "14", ["backend/app/ingestion/pipeline.py"], "test_ingestion.py"),
        ("support S3-compatible object storage backend behind Storage protocol", "backend", "9.4", ["backend/app/storage/s3.py"], "test_storage.py"),
        ("add mime type cross-check validating file extension matches magic bytes", "backend", "13.2", ["backend/app/api/routes/documents.py"], "test_documents.py"),
        ("support zip archive bomb rejection by checking uncompressed ratio", "backend", "13.2", ["backend/app/ingestion/pipeline.py"], "test_ingestion.py"),
        ("preserve header hierarchy in markdown parsing (# and ## headings)", "backend", "8.1", ["backend/app/ingestion/chunker.py"], "test_chunker.py"),
        ("clean non-printable control characters from extracted text", "backend", "8.1", ["backend/app/ingestion/chunker.py"], "test_chunker.py"),
        ("extract metadata properties (title, author) from DOCX and PDF files", "backend", "8.1", ["backend/app/ingestion/parsers/pdf.py"], "test_pdf_parser.py"),
        ("handle malformed UTF-8 characters without raising UnicodeDecodeError", "backend", "8.1", ["backend/app/ingestion/pipeline.py"], "test_ingestion.py"),
        ("add unit tests asserting chunker handles code blocks without splitting", "backend", "16", ["backend/tests/test_chunker.py"], "test_chunker.py"),
        ("implement local storage garbage collection for unreferenced storage keys", "backend", "7.2", ["backend/app/storage/local.py"], "test_storage.py"),
        ("add batch embedding support in ingestion pipeline respecting batch_size", "backend", "8.1", ["backend/app/ingestion/pipeline.py"], "test_ingestion.py"),
        ("support CSV tabular file ingestion converting rows into key-value passages", "backend", "8.1", ["backend/app/ingestion/parsers/csv.py"], "test_csv_parser.py"),
    ]
    t, lbl, spec, files, test_file = titles[(idx - 1) % len(titles)]
    return {
        "id": f"{p}-{idx:02d}",
        "milestone": m,
        "title": f"backend: {t}",
        "labels": [lbl] + (["good first issue"] if idx % 2 == 0 else []),
        "spec_section": spec,
        "files_to_touch": files,
        "acceptance_test": f"cd backend && uv run pytest tests/{test_file}",
        "description": f"Implement {t} according to section {spec} of docs/architecture.md."
    }

def m5_gen(p, m, idx):
    titles = [
        ("implement SSE token streaming in ChatPanel", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("click on citation badge jumps to and highlights source passage", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("add search bar and status filter dropdown to document list", "frontend", "11.3", ["frontend/src/features/documents/document-panel.tsx"], "npm test"),
        ("add model selector and temperature slider to settings dialog", "frontend", "12.5", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("accessibility audit for keyboard navigation and screen reader labels", "frontend", "11", ["frontend/src/features/documents/document-panel.tsx"], "npm run lint"),
        ("render Markdown formatting (bold, code blocks, lists) in chat answers", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("add copy-to-clipboard button on generated assistant responses", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("add stop generation button during active SSE completion stream", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("show upload progress percentage bar in DocumentPanel", "frontend", "11.3", ["frontend/src/features/documents/document-panel.tsx"], "npm test"),
        ("add confirm modal before deleting a document", "frontend", "11.3", ["frontend/src/features/documents/document-panel.tsx"], "npm test"),
        ("implement drag-and-drop file upload zone in DocumentPanel", "frontend", "11.3", ["frontend/src/features/documents/document-panel.tsx"], "npm test"),
        ("persist OpenRouter API key in sessionStorage with obfuscated preview", "frontend", "10", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("add retry button for failed document ingestion items", "frontend", "11.3", ["frontend/src/features/documents/document-panel.tsx"], "npm test"),
        ("display human-readable error messages for 413, 415, and 429 status codes", "frontend", "14", ["frontend/src/api/client.ts"], "npm test"),
        ("add chunk inspector drawer showing chunk count and raw passage texts", "frontend", "11.3", ["frontend/src/features/documents/chunk-drawer.tsx"], "npm test"),
        ("add dark/light theme toggle with Tailwind CSS v4 support", "frontend", "11", ["frontend/src/app/theme.tsx"], "npm run build"),
        ("implement Playwright end-to-end test for document upload to answer flow", "frontend", "16", ["frontend/e2e/rag-flow.spec.ts"], "npm run e2e"),
        ("add regenerate response button on latest user message", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("auto-scroll chat transcript to bottom on incoming streaming tokens", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("add empty state illustration when document library has zero uploads", "frontend", "11.3", ["frontend/src/features/documents/document-panel.tsx"], "npm test"),
        ("show token count estimates and generation latency metrics badge", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("implement clear conversation history action with reset confirmation", "frontend", "11.4", ["frontend/src/features/chat/chat-panel.tsx"], "npm test"),
        ("add offline network banner when browser loses internet connectivity", "frontend", "11", ["frontend/src/features/common/offline-banner.tsx"], "npm test"),
        ("support multi-file upload selection in DocumentPanel", "frontend", "11.3", ["frontend/src/features/documents/document-panel.tsx"], "npm test"),
        ("add Vitest tests for useAuth authentication context hook", "frontend", "16", ["frontend/src/features/auth/auth-context.test.tsx"], "npm test"),
        ("add Vitest tests for StatusBadge component rendering all states", "frontend", "16", ["frontend/src/features/documents/status-badge.test.tsx"], "npm test"),
        ("assert initial JavaScript bundle remains strictly under 250 kB gzip", "frontend", "15", ["frontend/vite.config.ts"], "npm run build"),
        ("implement responsive drawer sidebar for mobile viewport navigation", "frontend", "11", ["frontend/src/pages/workspace.tsx"], "npm run build"),
        ("display document file size formatted in KB or MB in document rows", "frontend", "11.3", ["frontend/src/features/documents/document-panel.tsx"], "npm test"),
        ("add openapi-typescript CI validation asserting types match backend schema", "frontend", "16", ["frontend/package.json"], "npm run api:types"),
    ]
    t, lbl, spec, files, test_file = titles[(idx - 1) % len(titles)]
    return {
        "id": f"{p}-{idx:02d}",
        "milestone": m,
        "title": f"frontend: {t}",
        "labels": [lbl] + (["good first issue"] if idx % 2 == 0 else []),
        "spec_section": spec,
        "files_to_touch": files,
        "acceptance_test": f"cd frontend && {test_file}",
        "description": f"Implement {t} according to section {spec} of docs/architecture.md."
    }

def m6_gen(p, m, idx):
    titles = [
        ("add GitHub Actions 6-hour cron polling /health with status alerting", "infra", "17", [".github/workflows/healthcheck.yml"], "test -f .github/workflows/healthcheck.yml"),
        ("create automated pg_dump and tar backup script with rotation", "infra", "17", ["scripts/backup.sh"], "test -f scripts/backup.sh"),
        ("document EC2 log rotation configuration for docker containers", "infra", "17", ["docs/self_hosting.md"], "test -f docs/self_hosting.md"),
        ("implement database restore rehearsal script validating pg_restore", "infra", "17", ["scripts/restore.sh"], "test -f scripts/restore.sh"),
        ("configure Caddy security headers with strict Content-Security-Policy", "infra", "13.1", ["infra/Caddyfile"], "caddy validate --config infra/Caddyfile"),
        ("add Docker healthcheck test asserting Uvicorn responds within 5 seconds", "infra", "14", ["backend/Dockerfile"], "docker inspect --format='{{.State.Health.Status}}' ragnarock-api"),
        ("assert multi-arch ARM64 image builds cleanly on Graviton without emulation", "infra", "18", [".github/workflows/docker.yml"], "test -f .github/workflows/docker.yml"),
        ("add memory limits to compose.prod.yml preventing out-of-memory kernel panics", "infra", "15", ["infra/compose.prod.yml"], "docker compose config"),
        ("create automated SSL certificate renewal status monitoring command", "infra", "17", ["scripts/check_ssl.sh"], "test -f scripts/check_ssl.sh"),
        ("document emergency rollback procedure in docs/self_hosting.md", "docs", "14", ["docs/self_hosting.md"], "test -f docs/self_hosting.md"),
    ]
    t, lbl, spec, files, test_file = titles[(idx - 1) % len(titles)]
    return {
        "id": f"{p}-{idx:02d}",
        "milestone": m,
        "title": f"{lbl}: {t}",
        "labels": [lbl] + (["good first issue"] if idx % 2 == 0 else []),
        "spec_section": spec,
        "files_to_touch": files,
        "acceptance_test": test_file,
        "description": f"Implement {t} according to section {spec} of docs/architecture.md."
    }

def m7_gen(p, m, idx):
    titles = [
        ("add 15-minute quickstart FAQ and common papercuts to docs/", "docs", "1", ["docs/onboarding.md"], "test -f docs/onboarding.md"),
        ("create triage rotation guidelines for event maintainers", "docs", "18", ["docs/triage.md"], "test -f docs/triage.md"),
        ("add issue label taxonomy reference guide in CONTRIBUTING.md", "docs", "18", ["CONTRIBUTING.md"], "test -f CONTRIBUTING.md"),
        ("author dry-run participant feedback questionnaire", "docs", "18", ["docs/event_feedback.md"], "test -f docs/event_feedback.md"),
        ("verify root README clean clone flow on clean macOS and Windows systems", "docs", "1", ["README.md"], "test -f README.md"),
    ]
    t, lbl, spec, files, test_file = titles[(idx - 1) % len(titles)]
    return {
        "id": f"{p}-{idx:02d}",
        "milestone": m,
        "title": f"docs: {t}",
        "labels": [lbl, "good first issue"],
        "spec_section": spec,
        "files_to_touch": files,
        "acceptance_test": test_file,
        "description": f"Implement {t} according to section {spec} of docs/architecture.md."
    }

def main():
    all_issues = []
    all_issues.extend(M0_ISSUES)                                 # 15 issues
    all_issues.extend(make_issues("m1", "M1", 30, m1_gen))       # 30 issues
    all_issues.extend(make_issues("m2", "M2", 20, m2_gen))       # 20 issues
    all_issues.extend(make_issues("m3", "M3", 20, m3_gen))       # 20 issues
    all_issues.extend(make_issues("m4", "M4", 20, m4_gen))       # 20 issues
    all_issues.extend(make_issues("m5", "M5", 30, m5_gen))       # 30 issues
    all_issues.extend(make_issues("m6", "M6", 10, m6_gen))       # 10 issues
    all_issues.extend(make_issues("m7", "M7", 5, m7_gen))        # 5 issues

    print(f"Total generated issues: {len(all_issues)}")

    data = {"issues": all_issues}
    output_path = Path("planning/issues.yml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# RAGnarock Complete Issue Manifest (150 Issues)\n")
        f.write(f"# Total issues: {len(all_issues)}\n")
        f.write("# Generated for the junior contributor launch event\n\n")
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=100)

    print(f"Wrote {len(all_issues)} issues to {output_path}")

if __name__ == "__main__":
    main()

