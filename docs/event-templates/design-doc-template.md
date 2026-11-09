# <Design document title>

<!--
Template for the Git Together design track. Write for contributors who will
build UI in this repository.

How to use this file:
1. Copy it to the path in your issue (for example `docs/design/accessibility.md`).
2. Replace the title and every placeholder in angle brackets.
3. Delete the HTML comments before you open the pull request.
4. Use real examples from this app. The palette is dark slate with sky accents.
-->

<One short paragraph: who this document is for and what decision it supports.>

## Principles

- <Principle 1: short, testable statement.>
- <Principle 2.>
- <Principle 3.>

## <First section from the issue>

<Explain the rule. Show a correct and an incorrect example.>

| Token / pattern | Value | Use it for |
| :--- | :--- | :--- |
| `<name>` | `<value>` | <one line> |

## <Second section from the issue>

<Use a table or a before/after example.>

```text
Do:   <example>
Do not: <example>
```

## Component states

| State | Visual treatment | Notes |
| :--- | :--- | :--- |
| Default | <border, background, text> | <notes> |
| Hover | <change> | Pointer users |
| Focus | <ring> | Keyboard users; must be visible |
| Disabled | <opacity or colour> | Not focusable |
| Loading | <spinner or skeleton> | Announce with `aria-busy` if relevant |

## Accessibility

- Keyboard: <how the user reaches and operates it.>
- Screen reader: <labels, roles, live regions.>
- Contrast: <minimum ratio and where it applies.>
- Motion: <how reduced motion is respected.>

## Examples from this app

- `frontend/src/features/documents/status-badge.tsx` — status colours.
- `frontend/src/features/chat/chat-panel.tsx` — message layout.
- `frontend/src/index.css` — base theme and `color-scheme: dark`.

## Do and do not

| Do | Do not |
| :--- | :--- |
| <specific action> | <specific anti-pattern> |
| <specific action> | <specific anti-pattern> |

## Related reading

- `docs/design/design-system.md`
- `docs/design/accessibility.md`
- `docs/design/ux-copy.md`
- `docs/design/responsive.md`

These files are created by `set3-47` to `set3-50` during Git Together. Link to them
only after they exist.

<!--
Before you submit:
- [ ] The acceptance command from the issue passes from the repository root.
- [ ] Every recommendation has a concrete example.
- [ ] Colours, spacing, and states are named consistently.
- [ ] No HTML comments remain.
-->
