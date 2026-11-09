# Troubleshooting for contributors

Work through this page before you ask for help. Most Git Together problems are
one of the cases below. You are fixing **your laptop or your pull request**,
not a production incident.

When you ask for help, include:

1. Your operating system and shell (PowerShell, Git Bash, WSL, macOS, Linux).
2. The exact command you ran.
3. The full error output, not a screenshot of one line.
4. What you already tried.

## First checks

```bash
git --version
node --version     # must be v22.x
npm --version
python3 --version  # must be 3.12.x
uv --version
docker --version   # only if using Docker
```

Run commands from the correct directory:

| Task | Directory |
| :--- | :--- |
| Backend tests | `backend/` |
| Frontend tests | `frontend/` |
| Docs acceptance commands | repository root |
| Docker Compose | repository root |

A very common mistake is running `npm` commands from the repository root or `uv`
commands from `frontend/`.

---

## Node.js and npm

### `node: command not found` or wrong version

Install Node.js 22 LTS from <https://nodejs.org>. If you use `nvm`:

```bash
nvm install 22
nvm use 22
node --version
```

The repository requires Node 22 or newer. Node 18 and 20 may fail on Vite 8.

### `npm ci` fails with `EUSAGE` or lockfile errors

`npm ci` requires `package-lock.json` and an exact match with `package.json`.

```bash
cd frontend
ls package-lock.json
npm ci
```

If the lockfile is missing, you cloned the wrong folder or deleted it. Restore it:

```bash
git restore package-lock.json
npm ci
```

Do **not** run `npm install` to "fix" a lockfile mismatch; it rewrites the lockfile
and creates a large diff. Ask a mentor instead.

### `npm ci` fails with network or registry errors

```bash
npm config get registry
npm cache verify
npm ci
```

If you are behind a proxy, set it:

```bash
npm config set proxy http://your-proxy:port
npm config set https-proxy http://your-proxy:port
```

### `node_modules` is in a broken state

```bash
cd frontend
rm -rf node_modules
npm ci
```

Do not delete `package-lock.json`.

### `npm run dev` starts but the page is blank

1. Open the browser console and read the first error.
2. Check the terminal running Vite.
3. Confirm you are on <http://localhost:5173>, not `https`.
4. Run `npm run typecheck` to catch import errors.

### Port 5173 is already in use

Stop the other process, or use another port:

```bash
npm run dev -- --port 5174
```

Do not commit a port change to avoid a local conflict.

### `npm run build` fails but `npm test` passes

The build runs `tsc --noEmit` first. Fix TypeScript errors before Vite errors.

```bash
npm run typecheck
```

Common causes:

- Unused imports or variables (`noUnusedLocals`, `noUnusedParameters`).
- A type imported as a value (`verbatimModuleSyntax`). Use `import type { X }`.
- A missing `@/` path — the alias points at `frontend/src`.

```ts
// Wrong
import { Citation } from "@/api/types";

// Right when Citation is only a type
import type { Citation } from "@/api/types";
```

---

## Vitest and React tests

### `No test files found`

The path is wrong or the file does not exist yet. Check the exact path from the
issue:

```bash
cd frontend
ls src/components/ui/button.test.tsx
npx vitest run src/components/ui/button.test.tsx
```

Run from `frontend/`, not the repository root. Do not include `frontend/` twice in
the path.

### `Cannot find module '@/...'`

Vitest uses the Vite config, which defines the `@` alias. Make sure you run
`npx vitest run` from `frontend/` and that the file is under `frontend/src/`.

### `document is not defined`

The test environment should be `jsdom`; it is configured in `vite.config.ts`.
Do not override the environment unless the issue asks for it. If you added
`// @vitest-environment node`, remove it.

### `renderHook` or `screen` is undefined

Import from the testing library:

```ts
import { renderHook } from "@testing-library/react";
import { screen } from "@testing-library/react";
```

`jest-dom` matchers are loaded by `src/test/setup.ts`. Do not import them again.

### A test times out

Common causes:

- A real `fetch` call. Mock it.
- A timer that is never advanced. Use `vi.useFakeTimers()` and `vi.advanceTimersByTime()`.
- An effect that loops forever. Check dependencies.

### Tests pass locally but fail in CI

- Run the exact command from CI: `npm test` from `frontend/`.
- Check for tests that depend on the current date, timezone, or locale.
- Check for shared state between tests.
- Do not rely on test execution order.

---

## Python, uv, and pytest

### `uv: command not found`

Install:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart the terminal, then:

```bash
uv --version
```

### `uv sync` is slow or appears stuck

The first install downloads PyTorch and `sentence-transformers`, which can be
several hundred MB. Give it 5–15 minutes on a normal connection. Do not cancel
repeatedly and restart; that makes it slower.

```bash
cd backend
uv sync --extra dev
```

### `uv sync` fails on Python version

The project requires Python 3.12. Check:

```bash
python3 --version
cat backend/.python-version
```

Let `uv` manage Python:

```bash
cd backend
uv python install 3.12
uv sync --extra dev
```

### `ModuleNotFoundError: No module named 'app'`

Run pytest from `backend/`:

```bash
cd backend
uv run pytest tests/test_chunking_empty.py -q
```

Do not run `pytest` directly from the repository root. Use `uv run` so the
project environment is used.

### `ModuleNotFoundError` for a package you just added

You probably added a dependency. Git Together issues do not require new dependencies.
If the issue truly needs one, ask a mentor first.

### Tests fail with a database connection error

Unit tests should not need a database. Check that you ran the unit suite:

```bash
cd backend
uv run pytest -m "not integration" -q
```

If your test starts the full app and hits Postgres, it is an integration test. Mark
it or mock the dependency. Most Git Together tests should use `TestClient` with the default test
configuration and no real database.

### `ruff check` fails

```bash
cd backend
uv run ruff check path/to/file.py
uv run ruff check --fix path/to/file.py
uv run ruff format path/to/file.py
```

Read the rule code (for example `F401` unused import). Fix the cause; do not add
`# noqa` unless the issue or a mentor says so.

### `ruff format --check` fails

```bash
cd backend
uv run ruff format path/to/file.py
```

Then re-run the check.

### `mypy` fails

- Add type annotations to function arguments and return values.
- Use `X | None` instead of `Optional[X]`.
- Do not use `Any` to silence errors.
- If a third-party package has no types, ask a mentor before adding an ignore.

---

## Docker and PostgreSQL

### `Cannot connect to the Docker daemon`

Start Docker Desktop (Windows/macOS) or the Docker service (Linux):

```bash
sudo systemctl start docker
docker info
```

On Linux, add your user to the `docker` group, then log out and back in:

```bash
sudo usermod -aG docker $USER
```

### `docker compose` is not a command

You have Compose v1. Use the v2 plugin:

```bash
docker compose version
```

If that fails, install Docker Compose v2 from Docker's documentation. Do not use
`docker-compose` with a hyphen.

### Port 5432 is already in use

You already have PostgreSQL running locally. Either stop it or use the debug
profile port mapping from `infra/compose.yml`. Do not change committed ports.

```bash
sudo systemctl stop postgresql   # Linux, only if you do not need it
```

### The API cannot reach the database

Inside Compose, the hostname is `db`, not `localhost`. Check `.env`:

```text
DATABASE_URL=postgresql+psycopg://ragnarok:ragnarok@db:5432/ragnarok
```

For a native backend against the debug Postgres, use `localhost`:

```text
DATABASE_URL=postgresql+psycopg://ragnarok:ragnarok@localhost:5432/ragnarok
```

### The database schema is out of date

```bash
cd backend
uv run alembic upgrade head
```

In Docker:

```bash
docker compose exec api uv run alembic upgrade head
```

### I want a clean database

```bash
docker compose down -v
docker compose up --build
```

`-v` deletes the database volume. You will lose uploaded documents.

### Docker build runs out of memory

Close other apps, or build with more memory in Docker Desktop. The backend image
installs PyTorch; 4 GB may not be enough.

### `permission denied` when writing uploads in Docker

Do not change file permissions in the repository. Ask a mentor; the volume may be
owned by another user.

---

## Documentation acceptance commands

Docs issues use commands like:

```bash
test -s docs/guides/testing.md && grep -qi "pytest" docs/guides/testing.md
```

### `test -s` fails

`test -s` fails when the file does not exist **or is empty**. Create the file and
write real content. An empty placeholder is not done.

```bash
ls -l docs/guides/testing.md
```

### `grep` fails

The required word is missing or has different casing. `grep -qi` is
case-insensitive, so check spelling.

```bash
grep -in "pytest" docs/guides/testing.md
```

Make sure you wrote the word in the file, not only in a code fence comment.

### The command works in bash but not PowerShell

Use **Git Bash** or **WSL** on Windows. PowerShell does not support `test -s`,
`grep`, or `&&` the same way.

### `&&` is not recognized

You are in PowerShell or `cmd`. Use Git Bash or run the two commands separately.

---

## Git

### `fatal: not a git repository`

You are in the wrong folder:

```bash
pwd
cd /path/to/RAGnarok
git status
```

### `Permission denied (publickey)`

Use HTTPS, not SSH, on the day:

```bash
git remote set-url origin https://github.com/<your-username>/RAGnarok.git
git push
```

Authenticate with a personal access token or `gh auth login`.

### `Support for password authentication was removed`

GitHub requires a token. Create one at
<https://github.com/settings/tokens> with `repo` scope, or run:

```bash
gh auth login
```

### `Updates were rejected because the remote contains work`

```bash
git pull --rebase origin <your-branch-name>
git push
```

Resolve conflicts if Git asks.

### I have merge conflicts

1. Open each conflicted file.
2. Find `<<<<<<<`, `=======`, `>>>>>>>`.
3. Keep the correct content and delete the markers.
4. Run the tests.
5. Stage and commit:

```bash
git add <file>
git commit
git push
```

If you are unsure which side to keep, ask a mentor.

### I am in detached HEAD state

```bash
git switch -c fix/123-my-change
```

Then continue. Do not commit on a detached HEAD.

### My branch is based on old `main`

```bash
git fetch upstream
git switch <your-branch-name>
git merge upstream/main
```

Run tests after the merge.

### CRLF / line-ending noise on Windows

Set the repository default:

```bash
git config core.autocrlf true
```

Do not commit a whole file just because line endings changed. If your diff shows
every line changed, stop and ask a mentor.

---

## CI

### CI fails on formatting

```bash
cd backend
uv run ruff format .
uv run ruff check .
```

Commit the formatted files.

### CI fails on a test that passes locally

- Run the exact CI command.
- Check for timezone or locale dependence.
- Check for ports or environment variables.
- Re-read the failing job log; the first error is the important one.

### CI does not run at all

CI is path-filtered. A docs-only PR may not trigger backend or frontend CI. That is
expected. The validation workflow runs for `planning/` and `scripts/` changes.

### I cannot restart CI

Ask a mentor. Do not push empty commits repeatedly to trigger CI.

---

## Still stuck?

1. Re-read the issue steps.
2. Run the acceptance command exactly as written.
3. Search this page for the first line of the error.
4. Ask in the Git Together chat with the four details listed at the top.
5. If you have been blocked for 15 minutes, tell a mentor. Switching to a
   docs or config issue is a valid recovery.
