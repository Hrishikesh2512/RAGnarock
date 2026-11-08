# Self-Hosting & Deployment Guide

This guide provides instructions for deploying, configuring, and operating RAGnarock across local development and production environments.

---

## Deployment Topologies

RAGnarock supports two deployment topologies:

| Environment | Orchestration | Components | Purpose |
| :--- | :--- | :--- | :--- |
| **Local Development** | Docker Compose (`infra/compose.yml`) | API (:8000), Vite Web (:5173), Postgres 17 (:5432 via debug profile) | Fast iteration, hot-reloading, auto-signed local user |
| **Production Single-Host** | Docker Compose (`infra/compose.prod.yml`) | API (:8000 internal), Caddy Edge (:80/:443), Postgres 17 (internal) | Production deployments, automated TLS, JWT auth enforced |

---

## Option 1: Quickstart via Docker Compose (Recommended)

The simplest way to run RAGnarock locally:

### 1. Clone and Configure
```bash
git clone https://github.com/bit-nodedotai/RAGnarock.git
cd RAGnarock
cp .env.example .env
```

### 2. Boot Services
```bash
docker compose up --build
```

### 3. Verify
- **Frontend SPA:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Docs:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

*(Optional: Run `docker compose --profile debug up` to publish Postgres directly on `127.0.0.1:5432` for external GUI clients like DBeaver or TablePlus).*

---

## Option 2: Production Deployment on a Single VM

For production deployments on AWS EC2, Oracle Cloud, or any commodity Linux virtual machine:

### 1. System Requirements
- **OS:** Ubuntu Server 24.04 LTS (ARM64 or x86_64)
- **Hardware:** 2 vCPU, 2–4 GB RAM, 30 GB SSD
- **Swap:** 2 GB swapfile recommended for 2 GB RAM instances
- **Ports:** Inbound `80/tcp` (HTTP) and `443/tcp` (HTTPS) open; `5432` and `8000` kept internal.

### 2. Domain & TLS Preparation
Ensure you have a DNS `A` record pointing to your server's public IP address (for example using a free [DuckDNS](https://www.duckdns.org) subdomain like `ragnarock-api.duckdns.org`). Caddy automatically requests and renews Let's Encrypt TLS certificates.

### 3. Environment Secrets
Generate cryptographically random secrets:
```bash
openssl rand -hex 24   # Use for POSTGRES_PASSWORD
openssl rand -hex 32   # Use for JWT_SECRET
```

Create `.env` on your server:
```dotenv
POSTGRES_PASSWORD=your_48_char_postgres_password
JWT_SECRET=your_64_char_jwt_secret
SITE_ADDRESS=your-subdomain.duckdns.org
ALLOWED_ORIGINS=https://your-frontend.vercel.app
API_WORKERS=1
```

### 4. Launch Production Stack
```bash
docker compose --env-file .env -f infra/compose.prod.yml up -d --build
```

### 5. Verify Production Health
```bash
curl -fsS https://your-subdomain.duckdns.org/health
# Expected: {"status":"ok"}

curl -fsS https://your-subdomain.duckdns.org/version
# Expected: {"name":"RAGnarock","version":"0.1.0","environment":"production"}
```

---

## Configuration Reference

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | Runtime environment (`development`, `production`, `test`) |
| `DATABASE_URL` | `postgresql+psycopg://...` | Connection URI for PostgreSQL + pgvector |
| `AUTH_DISABLED` | `true` (dev) / `false` (prod) | In development, auto-authenticates a default user |
| `JWT_SECRET` | — | Required when `AUTH_DISABLED=false` |
| `ALLOWED_ORIGINS` | `""` | Comma-separated CORS allowlist (e.g. `https://ragnarock.vercel.app`) |
| `SITE_ADDRESS` | `localhost` | Hostname for Caddy edge automatic TLS provisioning |
| `API_WORKERS` | `1` | Number of Uvicorn API workers (keep at 1 for 2 GB RAM instances) |
| `EMBEDDING_PROVIDER` | `local` | `local`, `openrouter`, or `fake` |
| `LLM_PROVIDER` | `openrouter` | `openrouter`, `ollama`, or `fake` |
| `LLM_MODEL` | `nvidia/nemotron-3-ultra-550b-a55b:free` | Default model sent to OpenRouter |
| `MAX_UPLOAD_MB` | `10` | Maximum file size for uploaded documents in MB |

---

## Database Backup & Restore

PostgreSQL volumes are persisted in Docker volume `ragnarock_pgdata`.

### Backup Database:
```bash
docker compose -f infra/compose.prod.yml exec -T db \
  pg_dump -U ragnarock ragnarock | gzip > db-backup-$(date +%F).sql.gz
```

### Restore Database:
```bash
docker compose -f infra/compose.prod.yml stop api
gunzip -c db-backup-YYYY-MM-DD.sql.gz | \
  docker compose -f infra/compose.prod.yml exec -T db \
  psql -U ragnarock -d ragnarock
docker compose -f infra/compose.prod.yml start api
```

