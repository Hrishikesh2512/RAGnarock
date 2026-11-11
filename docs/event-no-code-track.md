# No-code track

This track is for Git Together contributors who **do not write code**. You edit
Markdown, YAML, CSS, or a small config file. Every issue has a copy-paste
acceptance command. A mentor is paired with the track.

You are still a contributor. You use Git, follow the terminal steps, and open
a pull request. You do not deploy anything.

> If you have never used a terminal, tell a mentor and start with `set1-05`.

## What you need

- Git and a GitHub account.
- A text editor (VS Code, Cursor, or any editor).
- A terminal: **Git Bash** or **WSL** on Windows; Terminal on macOS/Linux.
- 30-60 minutes for one issue.
- No Python, no Node.js, no Docker required for the documentation or design issues.
- `set1-23` and `set1-25` need only Git.

## Pick one issue

Start with the first row you have not done. Each person completes **one** issue.
Comment on the GitHub issue and wait to be assigned before you start.

### Track A - Documentation and configuration (14 issues)

| ID | Issue | What you will produce | Time |
| :--- | :--- | :--- | ---: |
| `set1-05` | Git command cheat sheet | A copy-paste Git reference | 30 min |
| `set1-23` | `.editorconfig` | A 15-line editor config | 20 min |
| `set1-25` | Dependabot config | A small YAML file | 25 min |
| `set1-01` | Native local development guide | Steps to run the app without Docker | 45 min |
| `set1-02` | Docker development guide | Steps to run the app with Docker | 40 min |
| `set1-03` | Testing guide | Backend and frontend test commands | 40 min |
| `set1-04` | Code style guide | Formatting and lint rules | 35 min |
| `set1-06` | Backend troubleshooting | Fixes for common Python errors | 45 min |
| `set1-07` | Frontend troubleshooting | Fixes for common Node errors | 40 min |
| `set1-11` | Environment variables | A readable `.env` reference | 45 min |
| `set1-14` | What happens after your pull request merges | A contributor's view of merge and sync | 40 min |
| `set1-20` | Reset your local database | How to wipe your laptop's Docker data | 45 min |
| `set1-21` | When your pull request is stuck | CI, review, and conflicts | 45 min |
| `set1-22` | Check your local API | Health, version, and docs URLs | 40 min |

### Track B - Design team (5 issues)

These are for the frontend lead and the design team. They need design judgement,
not programming.

| ID | Issue | What you will produce | Time |
| :--- | :--- | :--- | ---: |
| `set3-46` | Design tokens | CSS custom properties in `frontend/src/styles/tokens.css` | 40 min |
| `set3-47` | Design system reference | Colour, type, spacing, states | 35 min |
| `set3-48` | Accessibility checklist | Keyboard, focus, labels, contrast, motion | 35 min |
| `set3-49` | UX copy guide | Buttons, empty states, errors, confirmations | 35 min |
| `set3-50` | Responsive layout guide | Breakpoints and workspace layout | 35 min |

> `set3-46` is the only design issue that touches a code file (`tokens.css` and
> the `@import` in `index.css`). It is still CSS only, no JavaScript.

## Suggested pairing

If you are new to the terminal, do these in order:

1. `set1-05` - practise Git commands in a safe way.
2. `set1-23` or `set1-25` - a tiny file with an exact shape.
3. `set1-03` - a guide with commands you can copy from the repository.
4. One of `set1-01`, `set1-02`, `set1-06`, `set1-07`.

If you are on the design team, start with `set3-47`, then `set3-48`-`set3-50`, and
leave `set3-46` until the lead confirms the token names.

## How to do a no-code issue

1. Open the issue on GitHub and read it fully.
2. Open the template:
   - Contributor docs: [`event-templates/doc-template.md`](event-templates/doc-template.md)
   - Design docs: [`event-templates/design-doc-template.md`](event-templates/design-doc-template.md)
3. Read the source file named in the issue. You do not need to understand all of
   it; look for the commands, paths, and names you need to mention.
4. Copy the template to the path in the issue.
5. Fill in every section. Delete the guidance comments.
6. Run the acceptance command from the repository root:
   ```bash
   test -s docs/guides/testing.md && grep -qi "pytest" docs/guides/testing.md
   ```
7. Follow [github-workflow.md](event-github-workflow.md) to commit, push, and open a PR.
8. In the PR, paste the exact command you ran and its result.

## Quality rules

- **Use real commands.** Copy them from `README.md`, `CONTRIBUTING.md`,
  `docs/self_hosting.md`, or the source file named in the issue.
- **Do not invent flags, endpoints, or environment variables.** If you cannot find
  a value, write `<unknown>` and ask a mentor; do not guess.
- **Keep code fences labelled:** `bash`, `text`, `python`, `ts`, `json`, `yaml`.
- **Use short paragraphs.** One idea per paragraph.
- **Link related docs** instead of repeating them.
- **Do not edit code files.** Your issue lists the only files you may change.
- **Do not copy another contributor's doc.** Write your own words.

## What "done" means

- [ ] The file exists at the exact path in the issue.
- [ ] The acceptance command passes.
- [ ] Every command is copy-pasteable.
- [ ] Every code fence has a language.
- [ ] The PR says `Closes #<issue-number>`.
- [ ] A mentor has reviewed it.

## If you get stuck

- Missing command? Search the repository:
  ```bash
  grep -rn "uv run" README.md CONTRIBUTING.md docs/
  ```
- Not sure what a file does? Open it and read the top comment.
- Acceptance command fails? Read the error; `test -s` usually means the file is
  missing or empty.
- Still stuck after 15 minutes? Ask a mentor. Do not spend the whole event on one
  paragraph.

## After your first issue

If you enjoyed it and want to try code later, tell a mentor. Good next steps are:

- `set1-26` (a small backend test) with a Python mentor.
- `set3-01` (a small TypeScript utility) with a frontend mentor.
- `set3-22` or `set3-26` (simple components) with a frontend mentor.

Do not jump straight into Set 2 integration issues. They assume you can read the
existing FastAPI code.
