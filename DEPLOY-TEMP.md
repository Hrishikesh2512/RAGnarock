# RAGnarock v1 — deployment runbook (TEMPORARY)

> **Temporary operator notes.** Delete this file before publishing the repository
> if you do not want deployment specifics in the public tree. It contains no
> secrets, but it does describe your hosts and provider accounts.
>
> The authoritative specification is `docs/architecture.md` (§5.2 and §12). The
> hosting decision is recorded in `docs/adr/0001-vercel-hosted-spa.md`.

**Target:** React SPA on Vercel Hobby (Free), FastAPI + Postgres/pgvector on one
free-tier VM (e.g. AWS EC2 Free Tier or Oracle Cloud Always Free), with Caddy
providing automated HTTPS using a **free subdomain** (e.g. DuckDNS). **Zero paid
services or paid domains required.**

**What v1 can do:** register/login, upload a `.txt` or `.md` file, chunk and embed
it locally, retrieve chunks, and answer with citations. Generation is BYOK: each
chat request carries the user's OpenRouter key in `X-Provider-Key`; the server
never stores a model key.

**Not in v1:** PDF/DOCX parsing, streaming/SSE chat, refresh tokens, workspaces,
conversations, reindex, rate limiting, guest sessions, log-redaction canaries, and
automated CI/CD. Chat returns one JSON response.

---

## 1. Prerequisites (AWS Credits + Free Tier Everywhere Else)

- **Compute:** An AWS account with your credits (e.g. $100 in credits easily covers
  a `t4g.medium` + 30 GB gp3 volume for ~3 to 4 months).
- **Free Subdomain (No Paid Domain):** A free dynamic DNS account like
  [DuckDNS](https://www.duckdns.org) (sign in with GitHub). DuckDNS gives you a
  permanent, free `*.duckdns.org` subdomain pointing to your EC2 Elastic IP.
  Caddy automatically requests and renews Let's Encrypt TLS certificates for it.
  *(This is required because Vercel frontend pages are HTTPS; browsers block plain
  HTTP API calls as mixed content).*
- **GitHub Repository:** Containing this project.
- **Vercel Account:** Free Hobby tier for hosting the static frontend.
- **OpenRouter Key:** Free-tier or BYOK key for generation (entered in browser, never on server).

Except for the AWS compute usage covered by your credits, every component in this runbook is 100% free with zero out-of-pocket expense.

---

## 2. Add `frontend/vercel.json`

The repository currently does **not** contain this file. Add it before the first
Vercel deployment so client-side routes fall back to `index.html` and the SPA has
security headers.

Create `frontend/vercel.json`, replacing `your-subdomain.duckdns.org` with your free
DuckDNS subdomain in **both** places:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "no-referrer" },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' https://your-subdomain.duckdns.org; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        }
      ]
    }
  ]
}
```

Commit and push it with the rest of the project. Vercel reads this file when the
project root directory is `frontend`.

---

## 3. Deploy the frontend to Vercel

The frontend can be built before the API exists; it only calls the API at runtime.

1. In Vercel, **Add New → Project** and import the GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Use the **Vite** framework preset. Build command: `npm run build`. Output
   directory: `dist`. Node 22 or newer (`frontend/package.json` declares `>=22`).
4. Add an environment variable for the production deployment:
   - `VITE_API_BASE_URL=https://your-subdomain.duckdns.org/api`
   - No trailing slash after `/api`.
   - This is a **build-time** variable. Changing it requires a new deployment.
5. Deploy and copy the production URL, for example
   `https://ragnarock.vercel.app`.

Preview deployments get unique URLs; for v1, treat them as visual only unless you
explicitly add their origin to `ALLOWED_ORIGINS`.

The page will show API errors until the API host is running. That is expected.

---

## 4. Provision the EC2 API host

### 4.1 Instance

Launch an EC2 instance with:

- **AMI:** Ubuntu Server 24.04 LTS, **arm64**.
- **Type:** `t4g.medium` (2 vCPU / 4 GB) is the reference shape. `t4g.small` may
  work for a low-traffic demo but has less headroom for Postgres and the embedding
  model.
- **Storage:** 30 GB gp3.
- **Key pair:** create or select one you control.
- **Security group inbound:**
  - `22/tcp` from your IP only.
  - `80/tcp` from `0.0.0.0/0` (and `::/0` if you use IPv6).
  - `443/tcp` from `0.0.0.0/0` (and `::/0` if you use IPv6).
  - Do **not** expose `5432` or `8000`; the prod compose stack keeps them internal.

Allocate an **Elastic IP** and associate it with the instance. Without an Elastic
IP, the public address changes after a stop/start and DNS/TLS break.

### 4.2 Free DNS via DuckDNS (No Paid Domain)

Do not buy a domain. Use [DuckDNS](https://www.duckdns.org) for a free, permanent
subdomain:

1. Go to [https://www.duckdns.org](https://www.duckdns.org) and log in (e.g. with GitHub).
2. Under **domains**, choose a name, for example `ragnarock-api` (full domain: `ragnarock-api.duckdns.org`).
3. In the **current ip** box, paste your AWS **Elastic IP** and click **update ip**.
4. Test that it resolves:
   ```bash
   nslookup ragnarock-api.duckdns.org
   ```

DuckDNS points directly to your Elastic IP. When Caddy starts, it will use this
domain to automatically obtain a free, trusted Let's Encrypt TLS certificate via
standard HTTP-01 challenge.

### 4.3 Install Docker

SSH in:

```bash
ssh -i ~/.ssh/<your-key>.pem ubuntu@<Elastic IP>
```

Install Docker Engine and the Compose plugin:

```bash
sudo apt-get update
sudo apt-get upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
newgrp docker
docker compose version
```

`newgrp` applies the group in the current shell; log out and back in if Docker
still asks for permission in a new session.

### 4.4 Clone and configure

```bash
git clone https://github.com/bit-nodedotai/RAGnarock.git
cd RAGnarock
cp .env.example .env
chmod 600 .env
```

Generate URL-safe secrets:

```bash
openssl rand -hex 24   # POSTGRES_PASSWORD
openssl rand -hex 32   # JWT_SECRET
```

Edit `.env` and set:

```dotenv
POSTGRES_PASSWORD=<the 48-character hex value>
JWT_SECRET=<the 64-character hex value>
SITE_ADDRESS=your-subdomain.duckdns.org
ALLOWED_ORIGINS=https://ragnarock.vercel.app
API_WORKERS=2
```

Notes:

- `POSTGRES_PASSWORD` is embedded in the database URL. Use hex (or another
  URL-safe value); punctuation such as `@`, `/`, or `:` must be URL-encoded.
- `ALLOWED_ORIGINS` is an exact, comma-separated allowlist. Add the Vercel custom
  domain too if you use one:
  `https://app.example.com,https://ragnarock.vercel.app`.
  Do not add a trailing slash and never use `*`.
- `SITE_ADDRESS` is a hostname, not a URL. Do not include `https://`.
- Leave `APP_ENV`, `AUTH_DISABLED`, `LLM_PROVIDER`, and `EMBEDDING_PROVIDER`
  alone. `infra/compose.prod.yml` forces production auth, OpenRouter generation,
  local embeddings, JSON logs, and the required `ALLOWED_ORIGINS`.
- Set the database password **before the first boot**. Postgres only applies it
  when initializing an empty data volume; changing it later does not change the
  role's password.

If the repository is private, use a GitHub deploy key or a fine-grained token
with read access. Do not put a token in the clone URL stored in shell history.

---

## 5. Start the production stack

From the repository root on the instance:

```bash
docker compose -f infra/compose.prod.yml up -d --build
```

This builds the API and edge images, starts Postgres, waits for its healthcheck,
runs `alembic upgrade head` from the API command, and starts the API and Caddy.

Check status and logs:

```bash
docker compose -f infra/compose.prod.yml ps
docker compose -f infra/compose.prod.yml logs --tail=100 api
docker compose -f infra/compose.prod.yml logs --tail=100 edge
```

Expected: `db` healthy, `api` healthy, `edge` running. Only `edge` publishes
ports 80/443.

Verify TLS and the API:

```bash
curl -fsS https://your-subdomain.duckdns.org/health
curl -fsS https://your-subdomain.duckdns.org/version
```

`/version` should report `"environment":"production"`. The first HTTPS request
may take a few seconds while Caddy obtains the certificate. If DNS is not ready
or port 80 is closed, Caddy retries; check its logs.

At this point, the Vercel page can call the API. Open the Vercel URL and:

1. Register an account with an email and password (8+ characters).
2. Upload a `.txt` or `.md` file.
3. Wait for the status to become `ready`.
4. In the chat panel, open the provider-key section and paste an OpenRouter key.
5. Ask a question and confirm the answer includes a citation.

The key is sent in `X-Provider-Key` on that request only and is not stored by the
API. It lives in the page's memory; re-enter it after a reload. There is no
server-side fallback key by default.

Test data isolation if you want: register a second account and confirm the first
account's uploaded documents are not visible.

---

## 6. CORS and origin changes

The API only accepts browser calls from origins in `ALLOWED_ORIGINS`, and it also
rejects mutations whose `Origin` header is not allowlisted. CORS is not the
authentication boundary; every protected route still checks the bearer token.

If the Vercel URL changes, or you add a custom domain:

```bash
cd ~/RAGnarock
nano .env                           # update ALLOWED_ORIGINS
docker compose -f infra/compose.prod.yml up -d api
```

Use `up -d api` (recreate), not `restart api`: a restart keeps the old environment.

Check the preflight from your machine:

```bash
curl -i -X OPTIONS https://your-subdomain.duckdns.org/api/chat \
  -H 'Origin: https://ragnarock.vercel.app' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization,content-type,x-provider-key'
```

Expect `200` and an `access-control-allow-origin` header containing the exact
Vercel origin. A foreign origin should be rejected, not silently allowed.

If you change `SITE_ADDRESS`, recreate the edge too:

```bash
docker compose -f infra/compose.prod.yml up -d edge
```

---

## 7. Updating the deployment

There is no CI/CD pipeline in v1. Deploy from the instance:

```bash
cd ~/RAGnarock
git pull
docker compose -f infra/compose.prod.yml up -d --build
docker image prune -f
```

- Migrations run automatically when the API container starts.
- Named volumes `pgdata`, `uploads`, and `hf-cache` survive rebuilds and normal
  `docker compose down`.
- Never use `docker compose down -v` on production; it deletes the database and
  uploaded files.
- After changing frontend code, Vercel redeploys from the pushed commit. After
  changing only the frontend environment variable, redeploy from Vercel.
- After changing backend-only environment variables, run `up -d api` to recreate
  the API container.

Useful commands:

```bash
docker compose -f infra/compose.prod.yml logs -f --tail=100 api
docker compose -f infra/compose.prod.yml logs -f --tail=100 edge
docker compose -f infra/compose.prod.yml ps
docker stats
df -h
```

If the VM runs out of memory with two API workers, set `API_WORKERS=1` in `.env`
and run `up -d api`. The local embedding model loads once per worker.

---

## 8. Backups

Postgres and uploads live in Docker volumes on the instance. Back both up and copy
the archives off the instance.

Database:

```bash
mkdir -p ~/backups
docker compose -f infra/compose.prod.yml exec -T db \
  pg_dump -U ragnarock ragnarock | gzip > ~/backups/db-$(date +%F).sql.gz
```

Uploads (the volume name is `ragnarock_uploads` because the prod compose project
is named `ragnarock`; confirm with `docker volume ls`):

```bash
docker run --rm \
  -v ragnarock_uploads:/data \
  -v "$HOME/backups":/backup \
  alpine tar czf "/backup/uploads-$(date +%F).tgz" -C /data .
```

Copy the archives to your machine or another store:

```bash
scp -i ~/.ssh/<your-key>.pem ubuntu@<Elastic IP>:~/backups/*.gz .
```

Restore the database (stop the API first, then restore, then start it):

```bash
docker compose -f infra/compose.prod.yml stop api
gunzip -c ~/backups/db-YYYY-MM-DD.sql.gz | \
  docker compose -f infra/compose.prod.yml exec -T db \
  psql -U ragnarock -d ragnarock
docker compose -f infra/compose.prod.yml start api
```

There is no S3 backup integration in v1; scheduling `pg_dump` and the uploads
archive plus an off-box copy is your responsibility.

Rotating `JWT_SECRET` invalidates all current sessions. Users must log in again.

---

## 9. Troubleshooting

| Symptom | Check |
|---|---|
| `502 Bad Gateway` from Caddy | `docker compose -f infra/compose.prod.yml ps`; inspect `api` logs and the Postgres healthcheck. |
| Caddy cannot issue a certificate | DuckDNS domain `your-subdomain.duckdns.org` must point at the Elastic IP; ports 80 and 443 must be open; `SITE_ADDRESS` must have no scheme. Check Caddy logs with `docker compose -f infra/compose.prod.yml logs edge`. |
| Browser shows a CORS or "failed to fetch" error | `ALLOWED_ORIGINS` must exactly match the Vercel origin (scheme included, no trailing slash). Recreate `api` with `up -d api`. Check the preflight with the curl command in §6. |
| `401` on `/api/auth/me` | Production requires a valid bearer token. Log in again; access tokens expire after 60 minutes and there is no refresh flow in v1. |
| `provider_key_required` in chat | Enter an OpenRouter key in the chat panel. The API does not hold a model key in production. |
| Upload rejected with `415` | v1 only accepts `text/plain` and `text/markdown` (`.txt`, `.md`). |
| Upload stays `pending` or becomes `failed` | Inspect `api` logs. The first ingestion downloads the embedding model into the `hf-cache` volume; check disk, memory, and outbound network. |
| Vercel page calls the wrong host | `VITE_API_BASE_URL` was missing or wrong at build time. Set it to `https://your-subdomain.duckdns.org/api` and redeploy. |
| CSP blocks the API | Update `connect-src` in `frontend/vercel.json` to the exact API origin and redeploy. |
| Database authentication fails after changing `.env` | The existing data volume still has the old role password. Restore the old value, or change the role password with SQL; do not delete the volume casually. |
| `exec format error` from the API | The image was built for the wrong CPU architecture. Build on the Graviton instance, or build `linux/arm64` explicitly. |
| Disk full | `df -h` and `docker system df`. Prune dangling images/build cache, but do not prune volumes. |

---

## 10. Shutdown and teardown

Stop the stack without deleting data:

```bash
docker compose -f infra/compose.prod.yml down
```

Start it again with `up -d`.

If you actually want to destroy the demo, `down -v` removes the Postgres and
uploads volumes. Terminating the EC2 instance also removes its local volumes;
release the Elastic IP and remove the Vercel project/domain when you are done.

Before making the repository public, delete this file if the deployment details
should stay private.
