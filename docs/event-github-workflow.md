# GitHub workflow for Git Together

This is the contributor workflow for the day. Follow it in order. If you already
know Git, skim the sections and use the checklists.

> **Goal:** one issue → one branch → one pull request → one merge.
> You do not merge it yourself. A maintainer does.

## 0. Before you start

You need:

- A GitHub account.
- Git installed.
- Your fork of `bit-nodedotai/RAGnarok`.
- A terminal open in the repository folder.

Check your setup:

```bash
git --version
git status
git remote -v
```

## 1. Fork the repository

1. Open <https://github.com/bit-nodedotai/RAGnarok>.
2. Click **Fork** in the top-right corner.
3. Keep the default name (`RAGnarok`) and click **Create fork**.

You now have `https://github.com/<your-username>/RAGnarok`.

## 2. Clone your fork

```bash
git clone https://github.com/<your-username>/RAGnarok.git
cd RAGnarok
```

Add the original repository as `upstream` so you can sync later:

```bash
git remote add upstream https://github.com/bit-nodedotai/RAGnarok.git
git remote -v
```

Expected output:

```text
origin    https://github.com/<your-username>/RAGnarok.git (fetch)
origin    https://github.com/<your-username>/RAGnarok.git (push)
upstream  https://github.com/bit-nodedotai/RAGnarok.git (fetch)
upstream  https://github.com/bit-nodedotai/RAGnarok.git (push)
```

## 3. Claim an issue

1. Pick **one** issue from your assigned set. Use
   [issue-index.md](event-issue-index.md) to browse.
2. Open the issue on GitHub.
3. Comment with this template:

```text
I would like to work on this issue.

Set: <1, 2, or 3>
Experience: <first Git Together / some React / some Python / no code yet>
Estimated time: <e.g. 45 minutes>
```

4. Wait for a maintainer to assign you. **Do not start a PR before the issue is
   assigned to you.** This prevents duplicated work.
5. If the issue has a dependency (the issue body says "Depends on #…"), check that
   the dependency is merged or ask a mentor to reorder your issue.

## 4. Sync `main` before branching

Your fork can be behind. Always branch from the latest `main`:

```bash
git switch main
git fetch upstream
git merge --ff-only upstream/main
git push origin main
```

If `git merge --ff-only` fails, your local `main` has commits. Ask a mentor before
doing anything destructive.

## 5. Create a branch

Use this format:

```text
<type>/<issue-number>-<short-description>
```

Examples:

```bash
git switch -c docs/12-add-testing-guide
git switch -c feat/87-add-button-component
git switch -c fix/44-normalize-upload-filename
```

Allowed `type` values: `feat`, `fix`, `docs`, `test`, `refactor`, `infra`, `chore`.

Keep the description short and lowercase, with hyphens. Do not use spaces.

## 6. Do the work

1. Read the issue body from top to bottom.
2. Open every file listed under **Files to touch**.
3. Follow the **Steps** in order.
4. Run the **Acceptance test** from the repository root.
5. Run the broader check for your set (see below).
6. Re-read your diff before committing.

Do **not** edit files outside `Files to touch` unless a mentor explicitly agrees.
Small, focused diffs get reviewed and merged faster.

### Checks by set

| Set | Minimum before PR |
| :--- | :--- |
| Set 1 - docs | The issue's `test -s` / `grep` command |
| Set 1 - tests | `cd backend && uv run pytest <test-file> -q` |
| Set 2 - backend | `cd backend && uv run pytest <test-file> -q`, `uv run ruff check <file>` |
| Set 3 - frontend | `cd frontend && npx vitest run <test-file>`, `npm run typecheck` |

When in doubt, also run the full suite:

```bash
cd backend && uv run pytest -m "not integration" -q
cd frontend && npm test && npm run typecheck
```

## 7. Commit

Stage only the files you changed:

```bash
git status
git add path/to/file1 path/to/file2
git status
```

Write a Conventional Commit message:

```text
<type>: <short imperative summary>
```

Examples:

```bash
git commit -m "docs: add the testing guide"
git commit -m "test: cover empty chunking input"
git commit -m "feat: add Button component"
git commit -m "fix: normalize upload filenames"
```

Rules:

- Use the imperative mood: "add", not "added" or "adds".
- Keep the first line under 72 characters.
- One commit is enough for most Git Together issues.
- Never commit `.env`, `node_modules`, `.venv`, or build output.

## 8. Push

```bash
git push -u origin <your-branch-name>
```

If Git asks for credentials, use a **personal access token** or the GitHub CLI
(`gh auth login`). Passwords are not accepted by GitHub.

## 9. Open the pull request

1. Open your fork on GitHub. GitHub shows a **Compare & pull request** banner.
2. Set **base repository** to `bit-nodedotai/RAGnarok` and **base branch** to `main`.
3. Set **head repository** to your fork and **compare branch** to your branch.
4. Use a clear title, for example:

```text
docs: add the testing guide
feat: add the Button component
```

5. Fill in the pull request template.
6. Make sure the description contains `Closes #<issue-number>`.
7. For UI changes, drag a screenshot into the description.
8. Click **Create pull request**.

### PR description template

```markdown
## What changed

- Added `docs/guides/testing.md` with backend, frontend, and CI test commands.

## Why

Closes #42

## How I verified it

- [x] `test -s docs/guides/testing.md && grep -qi "pytest" docs/guides/testing.md`
- [x] Read the rendered Markdown locally

## Notes

None.
```

## 10. Watch CI

CI runs automatically:

| Workflow | Runs when | Checks |
| :--- | :--- | :--- |
| Backend CI | `backend/**` changed | Ruff, format, mypy, pytest |
| Frontend CI | `frontend/**` changed | ESLint, typecheck, Vitest, build |
| Docs/validation | `planning/**` or `scripts/**` changed | Manifest validation |

A red check is normal on the first push. Open the failed job, read the first error,
fix it, commit, and push again. Do not close the PR and start over.

## 11. Respond to review

A mentor will review your PR. Common requests:

- "Please add a test for the empty case."
- "This file is outside the issue scope."
- "Use the existing helper instead of duplicating it."
- "Fix the lint error."

Make the change, commit, and push to the **same branch**. The PR updates
automatically.

```bash
git add .
git commit -m "test: cover the empty case"
git push
```

Reply to the review comment when you have addressed it. Do not resolve comments
yourself unless the reviewer asks you to.

## 12. Merge

A maintainer squash-merges the PR. You do **not** need to merge it yourself.

After the merge:

- The issue closes automatically because of `Closes #<number>`.
- Delete your branch on GitHub if prompted.
- Sync your fork before claiming another issue:

```bash
git switch main
git fetch upstream
git merge --ff-only upstream/main
git push origin main
git branch -d <your-branch-name>
```

## 13. Common Git fixes

### I committed to `main` by mistake

```bash
git switch -c fix/123-my-change
git switch main
git reset --hard upstream/main
```

Your commit is now on the new branch. Ask a mentor if you are unsure.

### I need to update my branch with the latest `main`

```bash
git fetch upstream
git switch <your-branch-name>
git merge upstream/main
```

Resolve conflicts in your editor, then:

```bash
git add <resolved-file>
git commit
git push
```

### I need to undo my last commit but keep the changes

```bash
git reset --soft HEAD~1
```

### I need to discard all local changes

```bash
git restore .
```

This cannot be undone. Ask a mentor first if you are unsure.

### My push was rejected

```bash
git pull --rebase origin <your-branch-name>
git push
```

If there are conflicts, resolve them before pushing.

## Event-day checklist

Before you ask for review:

- [ ] The issue is assigned to me.
- [ ] I branched from the latest `main`.
- [ ] I changed only the listed files.
- [ ] The acceptance test passes.
- [ ] The set-specific checks pass.
- [ ] My commit message follows Conventional Commits.
- [ ] The PR says `Closes #<issue-number>`.
- [ ] CI is green or I have explained the remaining failure.
- [ ] UI changes include a screenshot.
