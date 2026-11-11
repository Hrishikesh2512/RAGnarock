## Description

Briefly describe what you changed and why.

Closes #(issue-number)

## Git Together

- [ ] Set 1 - Starter
- [ ] Set 2 - Backend
- [ ] Set 3 - Frontend & Design
- [ ] Not a Git Together contribution

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Documentation update
- [ ] Test or refactor improvement
- [ ] Repository tooling or CI

## Verification

Paste the acceptance command from the issue and its result.

```bash
# Example
cd frontend && npx vitest run src/components/ui/button.test.tsx
```

- [ ] The acceptance command passes locally.
- [ ] I ran the set-specific checks below.

### Backend checks

- [ ] `cd backend && uv run pytest -m "not integration"`
- [ ] `cd backend && uv run ruff check .`
- [ ] `cd backend && uv run ruff format --check .`
- [ ] `cd backend && uv run mypy app`

### Frontend checks

- [ ] `cd frontend && npm run lint`
- [ ] `cd frontend && npm run typecheck`
- [ ] `cd frontend && npm test`
- [ ] `cd frontend && npm run build`

### Docs and config checks

- [ ] The issue's `test -s` / `grep` acceptance command passes.
- [ ] Every code fence has a language.
- [ ] Every command is copy-pasteable.

## Checklist

- [ ] The change is limited to the files listed in the issue.
- [ ] The PR is focused and under ~400 lines of diff.
- [ ] I added or updated tests where the issue asks for them.
- [ ] I followed the project invariants in [`docs/architecture.md`](https://github.com/bit-nodedotai/RAGnarok/blob/main/docs/architecture.md).
- [ ] I updated documentation if behavior or configuration changed.
- [ ] No secrets, `.env` files, credentials, or build artifacts are included.
- [ ] UI changes include a screenshot below.

## Screenshots

<!-- Drag a before/after screenshot here for UI changes. Delete this section otherwise. -->

## Notes for reviewers

<!-- Optional: anything you are unsure about, or a follow-up that should be a separate issue. -->
