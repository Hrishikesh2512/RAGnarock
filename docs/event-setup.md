# Setup for Git Together

Install only what **your issue** needs. You are setting up a contributor laptop,
not a server.

- **Full app with Docker (optional).** One command starts Postgres, the API, and the
  frontend so you can click through the product. No issue requires this.
- **Backend without Docker.** For Set 1 tests and Set 2. Unit tests do not need a
  database.
- **Frontend without Docker.** For Set 3 code. Node.js is the only extra requirement.
- **Docs, config, and design notes.** Git and a text editor.

Read the table below before you install anything.

If you are stuck for more than 15 minutes, ask a mentor. Do not spend the day
on setup.

## 1. Choose what you need

| Your issue | Install |
| :--- | :--- |
| No-code docs and config (`set1-01`–`set1-07`, `set1-11`, `set1-14`, `set1-20`–`set1-23`, `set1-25`) | Git + text editor |
| No-code design (`set3-46`–`set3-50`) | Git + text editor (CSS for `set3-46`) |
| Set 1 backend tests | Git + Python 3.12 + `uv` |
| Set 2 backend | Git + Python 3.12 + `uv` |
| Set 3 code (`set3-01`–`set3-45`) | Git + Node.js 22 |
| Running the full app | Everything above + Docker Desktop |

You do **not** need Docker to finish a Git Together issue. Install it only if you
want to click through the app.

## 2. Prerequisites

Install only the tools for your path. The table lists every supported tool so the
guide works for everyone.

| Tool | Version | Windows | macOS | Linux |
| :--- | :--- | :--- | :--- | :--- |
| Git | 2.40+ | [Git for Windows](https://git-scm.com/download/win) | `xcode-select --install` or [git-scm](https://git-scm.com/download/mac) | `sudo apt install git` / `sudo dnf install git` |
| GitHub account | — | [github.com](https://github.com) | same | same |
| Docker Desktop | 4.30+ | [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/) | [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/) | [Docker Engine](https://docs.docker.com/engine/install/) |
| Node.js | 22 LTS | [nodejs.org](https://nodejs.org) | [nodejs.org](https://nodejs.org) or `brew install node@22` | [nodesource](https://github.com/nodesource/distributions) |
| Python | 3.12 | [python.org](https://www.python.org/downloads/) | `brew install python@3.12` | `sudo apt install python3.12` |
| uv | 0.11+ | `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` | `curl -LsSf https://astral.sh/uv/install.sh | sh` | same as macOS |

Verify the tools you installed:

```bash
git --version
node --version     # Set 3: should print v22.x
python3 --version  # Set 1 tests / Set 2: should print 3.12.x
uv --version       # Set 1 tests / Set 2
docker --version   # full app only
```

> **Windows note:** use **Git Bash** or **WSL2** for the shell commands in this
> guide. PowerShell works for most commands, but the `cp` and `grep` examples need
> Git Bash or WSL.

## 3. Get the code

Fork the repository on GitHub, then clone **your fork**:

```bash
git clone https://github.com/<your-username>/RAGnarok.git
cd RAGnarok
```

Add the upstream repository so you can sync later:

```bash
git remote add upstream https://github.com/bit-nodedotai/RAGnarok.git
git remote -v
```

## 4. Full app with Docker

```bash
cp .env.example .env
docker compose up --build
```

The first run downloads images and installs the backend dependencies, including the
CPU embedding model. Expect **5–15 minutes** on a typical laptop.

Verify:

| URL | Expected |
| :--- | :--- |
| <http://localhost:5173> | Workspace UI opens |
| <http://localhost:8000/health> | `{"status":"ok"}` |
| <http://localhost:8000/api/docs> | FastAPI docs |
| <http://localhost:8000/version> | Name, version, environment |

Useful commands:

```bash
docker compose ps                 # service status
docker compose logs -f api        # follow API logs
docker compose down               # stop services
docker compose down -v            # stop and delete the database volume
```

## 5. Backend without Docker

You need PostgreSQL 17 with the `pgvector` extension for the full app. Unit tests do
**not** need a database.

```bash
cd backend
uv sync --extra dev
uv run pytest -m "not integration" -q
uv run ruff check .
uv run ruff format --check .
uv run mypy app
```

To run the API against a local database:

```bash
# from the repository root, start only Postgres and publish it on localhost
docker compose --profile debug up -d db db-debug

export DATABASE_URL=postgresql+psycopg://ragnarok:ragnarok@localhost:5432/ragnarok
cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

> `uv sync` downloads the CPU build of PyTorch and `sentence-transformers`; the
> first install can take several minutes. This is expected.

## 6. Frontend without Docker

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api`, `/health`, and `/version` to
`http://localhost:8000`, so start the API if you want the full app.

Frontend checks:

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

**Set 3 contributors:** you can complete component, hook, utility, and design issues
with only Node.js. You do not need Docker or a running API for `npm test` or
`npm run build`.

## 7. Verify your setup

Run only the block for your issue.

**Everyone:**

```bash
git --version
git config user.name
git config user.email
```

**Set 3 code (`set3-01`–`set3-45`, frontend):**

```bash
cd frontend
npm ci
npm run typecheck
npm test
```

**Set 1 backend tests and Set 2 (backend):**

```bash
cd backend
uv sync --extra dev
uv run pytest -m "not integration" -q
```

**No-code docs, config, and runbooks:**

You need only Git and a text editor. Your acceptance command is usually `test -s`
or `grep`, so there is nothing else to verify.

If any command fails, read [troubleshooting.md](event-troubleshooting.md) before asking
for help.

## 8. Ports

| Port | Service | Notes |
| :--- | :--- | :--- |
| 5173 | Vite frontend | Docker and native |
| 8000 | FastAPI | Docker and native |
| 5432 | PostgreSQL | Only with `--profile debug` |
| 80 / 443 | Caddy edge | Production compose only |

If a port is busy, stop the other process or change the dev port. Do not change
committed configuration just to work around a local port conflict.

## 9. If something fails

See [troubleshooting.md](event-troubleshooting.md). Include the following in your help
request:

- Operating system and shell.
- The exact command you ran.
- The full error output.
- What you already tried.
