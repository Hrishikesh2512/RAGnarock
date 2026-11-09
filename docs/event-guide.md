# Git Together

Git Together is our college open-source day. You contribute to **RAGnarok**: one
small issue, one branch, one pull request. By the end of the day you will have
used the same workflow maintainers use on this repository.

You are here as a **contributor**. You do not deploy the app, run a server, or
write an operator runbook. Mentors review and merge. You fork, change the files
your issue names, and open the pull request.

New to the repository? Read the [README](../README.md), then come back here.

> **Wait for the GO message before claiming an issue.** Mentors publish the three
> sets and say when claiming opens.

## Quick links

| Guide | What you do with it |
| :--- | :--- |
| [Setup](event-setup.md) | Install only the tools your issue needs, then prove they work |
| [GitHub workflow](event-github-workflow.md) | Fork, branch, commit, push, pull request, review |
| [Issue guide](event-issue-guide.md) | Read an issue and know when you are done |
| [No-code track](event-no-code-track.md) | 19 issues that are Markdown, YAML, or CSS |
| [Troubleshooting](event-troubleshooting.md) | Fixes for the errors you are likely to hit |
| [Issue index](event-issue-index.md) | All 150 contributor issues, with time estimates |

## What you leave with

- A merged, or review-ready, pull request on `bit-nodedotai/RAGnarok`.
- Your name on a commit in the project history.
- A working copy of the fork → branch → pull request loop.

## The three sets

| Set | Name | Your work | Install |
| :--- | :--- | :--- | :--- |
| **Set 1** | Starter | Docs, focused tests, and tiny config files | Git. Tests also need Python 3.12 and `uv` |
| **Set 2** | Backend | Small Python helpers and the tests that prove them | Git, Python 3.12, `uv` |
| **Set 3** | Frontend & Design | React pieces, or a design note | Git and Node.js 22. Design notes need Git only |

Every set has **exactly 50 issues**. Take the set a mentor gives you. If you
have no coding experience, take the [no-code track](event-no-code-track.md).
You still use Git and the terminal. You do not write Python or JavaScript.

## How the day works

1. **Setup (30–45 min).** Follow [event-setup.md](event-setup.md) and run the
   verification commands for your set. Ask a mentor if you are stuck.
2. **Claim (10 min).** Pick one open issue from your set. Comment on it. Wait
   until it is assigned to you. Read [event-issue-guide.md](event-issue-guide.md).
3. **Build (2–3 hours).** Follow the issue steps. Change only the listed files.
   Run the acceptance command from the repository root.
4. **Pull request (30 min).** Follow [event-github-workflow.md](event-github-workflow.md).
   The description must contain `Closes #<issue-number>`.
5. **Review (30–60 min).** A mentor reviews. You push fixes to the **same branch**.
   A maintainer squash-merges. The issue closes on its own.

## Rules

- **One active issue per person.** Wait until your pull request is merged before you ask for another.
- **Change only the files named in the issue** unless a mentor agrees.
- **Run the acceptance command** before you open the pull request.
- **Keep the pull request small.** If the diff grows past about 400 lines, ask a mentor to split it.
- **Do not add a dependency** unless the issue says so.
- **Do not deploy.** `docs/self_hosting.md` is for maintainers who run a server. Skip it.
- **Be kind.** Read the [Code of Conduct](../CODE_OF_CONDUCT.md).

## What you will learn

- How to fork this repository and keep your fork in sync with `upstream`.
- How to create a branch and write a Conventional Commit.
- How to open a pull request, answer review, and fix a red check.
- How to run the test or the docs command your issue asks for.
- How to turn a written issue into a small, reviewable change.

## Before you arrive

- Create a GitHub account and verify the email address.
- Install Git and a text editor. Everyone needs these.
- **Docs, config, and design notes:** stop there.
- **Set 1 tests and Set 2:** also install Python 3.12 and `uv`.
- **Set 3 code (`set3-01`–`set3-45`):** also install Node.js 22. Docker is optional.
- **Set 3 design (`set3-46`–`set3-50`):** Git and a text editor. `set3-46` is CSS only.
- Read this guide and [CONTRIBUTING.md](../CONTRIBUTING.md).
- Reply in the event group chat with your operating system and your set.

Do not install tools your issue does not use. [event-setup.md](event-setup.md)
has a track for each set.

## Common questions

**Can I do more than one issue?**
Yes, after your first pull request is merged. One active issue at a time.

**Can I work with a friend?**
Yes. Each person still owns their own issue and opens their own pull request.

**Do I need to stay all day?**
Stay for setup and for review. If you have to leave, tell a mentor so the issue
can be reassigned.

**Can I fix something else I noticed?**
Tell a mentor. Keep this pull request on the assigned issue.

**Can I edit `workspace.tsx`, `chat-panel.tsx`, or `document-panel.tsx`?**
Only when the issue lists that file. Set 3 component issues create new files.
The frontend lead wires them in later.

**My CI check is red. Is the pull request rejected?**
No. Open the first failing step, fix it, and push to the same branch. See
[event-github-workflow.md](event-github-workflow.md).

**How do I know it merged?**
GitHub shows **Merged**. The issue closes when the description contains
`Closes #<number>`.

**Will I be credited?**
Yes. The commit stays in history. Mention Git Together in the pull request if
you want the event named on your profile.

**Where is the full issue text?**
On GitHub after mentors publish, and in [event-issue-index.md](event-issue-index.md).
The source is [`planning/issues.yml`](../planning/issues.yml).

## Roles

| Role | What they do |
| :--- | :--- |
| **Contributor** | Owns one issue, opens one pull request, answers review |
| **Mentor** | Helps with setup, reviews pull requests, keeps the queue moving |
| **Frontend lead** | Coordinates Set 3 and reviews UI pull requests |
| **Maintainer** | Assigns issues, merges pull requests, handles conflicts |

## Pages that are not your task

| Page | Who it is for |
| :--- | :--- |
| [event-setup.md](event-setup.md) | You, before you claim an issue |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | You, for branch names, commits, and the one-issue rule |
| [docs/architecture.md](architecture.md) | You, when an issue tells you to read a design rule |
| [docs/self_hosting.md](self_hosting.md) | Maintainers who run a server. Not a Git Together task |
| [SECURITY.md](../SECURITY.md) | Vulnerability reports. During the event, tell a mentor first |

## Need help?

- Check [event-troubleshooting.md](event-troubleshooting.md) first.
- Ask in the event group chat with your OS, the command you ran, and the full error.
- If you are blocked for more than 15 minutes, tell a mentor. Do not spend the
  day on setup.
