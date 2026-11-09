# How to read your issue

Every Git Together contributor finishes **one issue**. This page is how the 150
issues are organized, how to read one, and how you know you are done.

You are doing contributor work: a doc, a test, a small helper, or a component.
You are not deploying the app.

> The full list is in [event-issue-index.md](event-issue-index.md). The source of
> truth is [`planning/issues.yml`](../planning/issues.yml).

## The three sets

| Set | Name | What it contains | What you need |
| :--- | :--- | :--- | :--- |
| **Set 1** | Starter | Docs, focused backend tests, and tiny tooling files | Git and a text editor; backend tests need `uv` |
| **Set 2** | Backend | Small Python helper modules, one-file integrations, regression tests | Python 3.12, `uv`, no database |
| **Set 3** | Frontend & Design | React utilities, hooks, UI components, feature components, design tokens and docs | Node.js 22 only |

Each set has exactly **50 issues**. They are independent, but the recommended
order is **Set 1 → Set 2 → Set 3**. Set 3 can run at the same time as Set 2.

## Labels

| Label | Meaning |
| :--- | :--- |
| `set-1`, `set-2`, `set-3` | Which set the issue belongs to |
| `docs` | Documentation or design writing |
| `test` | Automated tests only |
| `backend` | Python / FastAPI / database code |
| `frontend` | React / TypeScript / CSS code |
| `design` | Design system, UX copy, accessibility, responsive rules |
| `infra` | Repository tooling, editor config, Dependabot |
| `ci` | GitHub Actions and automation |
| `difficulty:beginner` | About 20–60 minutes; read the linked source first |
| `difficulty:intermediate` | About 1–2 hours; read the linked source first |
| `good first issue` | Safe starting point for a first contribution |
| `no-code` | No programming required; docs, config, or design work |

Not every issue is a "good first issue". That label is used only for beginner
issues. An `intermediate` issue is still doable; it just needs more reading.
`no-code` means you will not write Python or JavaScript. See the
[no-code track](event-no-code-track.md).

## How to choose an issue

1. Start with your assigned set.
2. Prefer an issue whose files you are curious about.
3. Check the estimated time and pick something you can finish in one sitting.
4. Check `Depends on` in the issue body. If the dependency is not merged, pick a
   different issue or ask a mentor.
5. Do not pick an issue that is already assigned.

If you have no preference, beginner issues are a safe default.

## Anatomy of an issue

Every issue has the same sections. Here is what they mean.

### Goal

A one-paragraph description of the change. This is the "why".

### Event set

Shows the set, difficulty, estimated time, and area. Use this to plan.

### Files to touch

The only files you should change. If a file is listed as new, create it. If it
already exists, stop and ask a mentor — the repository may have moved on.

Example:

```text
- `frontend/src/components/ui/button.tsx` (new)
- `frontend/src/components/ui/button.test.tsx` (new)
```

### Steps

An ordered list. Follow it in order. Read the referenced source files before
writing code. The steps are written for someone who has never seen this
repository.

### Acceptance test

A command you run **from the repository root**. It must pass before you open a
pull request.

```bash
cd frontend && npx vitest run src/components/ui/button.test.tsx
```

```bash
cd backend && uv run pytest tests/test_chunking_empty.py -q
```

```bash
test -s docs/guides/testing.md && grep -qi "pytest" docs/guides/testing.md
```

If the command fails, read the error. It usually points at the exact file and
line. See [troubleshooting.md](event-troubleshooting.md) if you are stuck.

### Definition of done

The shared quality bar:

- The acceptance command passes locally.
- The change is limited to the listed files.
- The PR description links the issue with `Closes #<issue-number>`.

### Depends on

Some Set 2 integration issues depend on a helper issue. For example, "use the safe
filename helper on upload" depends on "add document metadata helpers". If the
dependency is not merged yet:

- Ask a mentor to move you to another issue, **or**
- Wait for the dependency to merge, then sync `main` and start.

Do not copy the helper into the integration issue. That creates conflicts.

## Claiming an issue

Comment on the GitHub issue:

```text
I would like to work on this issue.

Set: 2
Experience: some Python, first open-source PR
Estimated time: 1 hour
```

A maintainer assigns it to you. Then follow
[github-workflow.md](event-github-workflow.md).

**One active issue per person.** Finish and merge your PR before asking for a
second issue.

## Quality bar

Your PR should be:

- **Small.** Usually under 400 lines of diff.
- **Focused.** Only the listed files, no drive-by refactors.
- **Tested.** The acceptance command passes; new behavior has a test.
- **Readable.** Names are clear, comments explain "why", not "what".
- **Consistent.** Follow the style of the surrounding code.
- **Safe.** No secrets, no `.env` files, no credentials in logs.

For frontend work:

- Use TypeScript with explicit prop types.
- Use Tailwind utility classes, not new CSS files, unless the issue is about tokens.
- Add `aria-*` attributes where the issue asks for accessibility.
- Test behaviour, not implementation details.

For backend work:

- Keep helpers dependency-free where the issue says so.
- Do not touch FastAPI routes in a helper issue.
- Do not add database or network calls to unit tests.
- Use the project's `ApiError` and error envelope.

For docs work:

- Use real commands from this repository.
- Use fenced code blocks with a language.
- Keep paragraphs short.
- Link to related docs.
- Do not invent flags, endpoints, or environment variables.

## What "done" looks like

Before you request review:

- [ ] The acceptance command passes from the repository root.
- [ ] I ran the set-specific check.
- [ ] I changed only the listed files.
- [ ] I added or updated tests where the issue asks for them.
- [ ] I read my own diff.
- [ ] My PR says `Closes #<issue-number>`.
- [ ] CI is green, or I left a comment explaining the failure.

## If an issue looks wrong

Issues are written by humans. If something is unclear, contradictory, or
impossible:

1. Comment on the issue with the exact problem.
2. Tag a mentor in the Git Together chat.
3. Do not guess and do not expand the scope.

A quick question is always cheaper than a large, wrong PR.

## Related reading

- [Setup](event-setup.md)
- [GitHub workflow](event-github-workflow.md)
- [Troubleshooting](event-troubleshooting.md)
