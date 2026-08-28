# ADR 0008: Default key bindings, and the keys the package refuses to take

## Status

Accepted. Supersedes the shortcut clause of PRD §5 (Full Screen preview).

## Context

The PRD specified `Ctrl+Shift+V` / `Cmd+Shift+V` for the Full Screen toggle,
with a context that restricts it to a Markdown source view or an owned preview.
Package Control's submission checklist asks a package not to add key bindings at
all, on the grounds that "there aren't enough keys for all packages, so you risk
overriding those of other packages", and it is the first thing a reviewer looks
at. That prompted a check of what the defaults actually are, rather than an
argument about whether a context makes an override safe.

## Measurements

Read out of `Default.sublime-package` in Sublime Text build 4200:

| Binding | Sublime Text default |
| --- | --- |
| `ctrl+shift+v` | `paste_and_indent` |
| `ctrl+k`, `ctrl+v` | `paste_from_history` |
| `ctrl+k`, `v` | none |
| `ctrl+k`, `shift+v` | none |
| `ctrl+=` / `ctrl+-` | `increase_font_size` / `decrease_font_size` |
| `ctrl+0` | `focus_side_bar` |

Every second key in Sublime Text's own `ctrl+k` chord table carries a `ctrl`
modifier — `ctrl+k ctrl+b`, `ctrl+k ctrl+u`, and so on. A bare second key after
`ctrl+k` collides with nothing, on any of the three platforms.

## Decision

The Full Screen toggle moves from `ctrl+shift+v` to `ctrl+k`, `shift+v`.

The context guard is not the point. `mdglance.markdown_source` is true exactly
when the user is editing Markdown, which is exactly when they reach for Paste
and Indent; a guard that narrow does not make the override safe, it aims it. A
chord under `ctrl+k` takes nothing from anyone, and it pairs with the
`ctrl+k`, `v` that already opens the preview to the side.

The zoom bindings stay. They fire only while a view this package created is
focused — a scratch preview, where there is no font to size and no reason to
reach for the sidebar — and `ctrl+=` / `ctrl+-` / `ctrl+0` there mean the same
thing they mean everywhere else, applied to the preview. `ctrl+0` shadows
`focus_side_bar` inside that view and nowhere else.

Every command remains reachable from the command palette without any binding,
and the defaults are editable from **Preferences → Package Settings →
MarkdownGlance → Key Bindings**.

## Consequences

- `Ctrl+Shift+V` keeps its Sublime Text meaning in every buffer, including
  Markdown ones.
- Users of 0.1.1 or earlier have to relearn one shortcut. It is called out in
  the release notes and the changelog.
- The package still ships a keymap, so the Package Control checklist box stays
  unchecked; the submission says so and explains why.
