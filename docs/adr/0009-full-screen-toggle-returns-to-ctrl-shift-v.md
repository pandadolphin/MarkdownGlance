# ADR 0009: The Full Screen toggle returns to Ctrl+Shift+V

## Status

Accepted. Supersedes [ADR 0008](0008-default-key-bindings.md).

## Context

ADR 0008 moved the Full Screen toggle off `ctrl+shift+v`, which is Sublime
Text's `paste_and_indent`, onto the chord `ctrl+k`, `shift+v`. The measurement
behind that choice was that no `ctrl+k` chord ending in a bare or shifted
second key is bound by anything, on any platform. That was true, and it was the
wrong conclusion to draw from it: nothing is bound there because nothing can be.

The chord shipped in 0.1.2 and does not fire. Sublime Text parses it — the
command palette lists **MarkdownGlance: Toggle Preview** with `Ctrl+K, Shift+V`
beside it — but pressing the sequence in a Markdown buffer does nothing.

## Measurements

Read out of `Default.sublime-package` in Sublime Text build 4200 on Linux, over
all 37 `ctrl+k` chords and the 2 `ctrl+j` chords:

| Second key shape | Count in Sublime Text's own keymap |
| --- | --- |
| carries `ctrl` (`ctrl+b`, `ctrl+shift+z`, `ctrl+up`, …) | 39 |
| bare character (`v`) | 0 |
| `shift` + character (`shift+v`) | 0 |

Every second key Sublime Text itself binds carries a `ctrl` modifier. A shifted
letter with no `ctrl` or `alt` reaches the key handler as the character it
produces, so a keymap entry spelled `shift+v` has nothing to match against —
which is the same reason the slot looked free in the first place.

## Decision

The Full Screen toggle returns to `ctrl+shift+v` / `super+shift+v`, in both the
Markdown source view and an owned preview. `ctrl+k`, `v` for **Open Preview to
the Side** stays; a bare second key does dispatch.

This costs the user Paste and Indent while a Markdown source view is focused,
and ADR 0008 is right that the narrow context aims the override rather than
excusing it. That is the price of the binding, accepted knowingly: a shortcut
that does not fire costs more than one that shadows a command the palette and
`Ctrl+K, Ctrl+V` still reach. Anyone who wants Paste and Indent back in Markdown
removes one entry from **Preferences → Package Settings → MarkdownGlance → Key
Bindings**.

The rest of ADR 0008 stands. The zoom bindings are unchanged, every command
remains reachable from the command palette without any binding, and the package
still ships a keymap, so the Package Control checklist box stays unchecked and
the submission says why.

## Consequences

- `Ctrl+Shift+V` is the toggle again, as in 0.1.1 and earlier. Users who
  relearned the chord for 0.1.2 relearn it once more; the release notes say so.
- `Ctrl+Shift+V` no longer means Paste and Indent in a Markdown buffer.
- `tests/unit/test_package_identity.py` no longer bans single-stroke bindings
  outright. It requires each one to be named in
  `SINGLE_STROKE_OUTSIDE_PREVIEW`, so a second such key cannot arrive without
  the list being edited.
