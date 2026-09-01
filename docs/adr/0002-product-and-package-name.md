# ADR 0002: Product and package name

## Status

Accepted.

## Context

The redesign is an independent Sublime Text package that must coexist with
`MarkdownLivePreview`. Names composed only by reordering "Native", "Markdown",
and "Preview" were available but visually indistinct from the existing
`MarkdownPreview`, `MarkdownLivePreview`, and related packages.

The Package Control `channel_v3.json` snapshot contained 5,432 package names.
Exact-name checks for `MarkdownGlance` found no Package Control or GitHub
repository match. The npm registry returned `404`, and a web search found no
VS Code Marketplace match. The checks establish current evidence, not a name
reservation.

## Decision

Use the following identity:

| Surface | Value |
| --- | --- |
| Public product and Package Control name | `MarkdownGlance` |
| Package directory | `MarkdownGlance` |
| Settings file | `MarkdownGlance.sublime-settings` |
| Command prefix | `mdglance_` |
| Context prefix | `mdglance.` |
| Owned-view setting prefix | `mdglance.` |
| `PhantomSet` key | `mdglance` |
| Worker thread prefixes | `mdglance-render`, `mdglance-net` |
| Repository | `pandadolphin/MarkdownGlance` |

The package description is "Live Markdown preview, native to Sublime Text 4."
The description carries the ST4-native positioning without making the generic
word "Native" the product's distinguishing feature.

## Consequences

- Production code must not retain the provisional `mdpreview_phase0_*`
  namespace. The Phase 0 harness keeps it as historical experiment code.
- Default shortcuts overlap the old package during coexistence. The migration
  guide must tell users to disable the old package or customize bindings, and
  coexistence testing must include keymap precedence as well as identifier
  collisions.
- The repository name should be reserved before public prerelease work begins.

## Addendum 2026-08-30: `MarkdownPreviewPlus` and `MarkdownPreviewExtended`

### Status

Considered and rejected. The name stays `MarkdownGlance`.

### Context

With `MarkdownLivePreview` and `MarkdownPreviewEnhanced` taken on Package
Control, `MarkdownPreviewPlus` and `MarkdownPreviewExtended` were proposed as
the next free names in the same family. Checked on 2026-08-30:

| Name | Package Control | Elsewhere |
| --- | --- | --- |
| `MarkdownPreviewPlus` | free | Atom `atom-community/markdown-preview-plus` (archived); Chrome extension "Markdown Preview Plus" (`volca/markdown-preview`) |
| `MarkdownPreviewExtended` | free | no notable match |
| `MarkdownGlance` | free, not yet submitted | no match |

The repository was two days old, with no stars, forks or Package Control
submission, so a rename would have cost nothing at that point. The decision
was made on the merits of the names, not on the cost of changing.

### Reasons for rejecting

1. Both names read as a fork or superset of `MarkdownPreview` (about 944,000
   unique installs on packagecontrol.io), which renders in a browser. This
   package's distinguishing feature is the opposite: it renders inside the
   editor with minihtml, and offers fewer output options, not more. A `Plus`
   or `Extended` suffix promises the wrong thing.
2. `MarkdownPreviewPlus` collides with well-known Atom and Chrome projects,
   the same objection that ruled out `Enhanced` above. A web search for it
   would not surface this package; `MarkdownGlance` is a unique token.
3. Discoverability does not need `Preview` in the name. The packagecontrol.io
   search for "markdown preview" matches descriptions -- it returns
   `OmniMarkupPreviewer`, whose name contains neither word -- and the
   in-editor install list shows the description "Live Markdown preview,
   native to Sublime Text 4." directly under the name.

### Consequences

- Renaming stays cheap only until the Package Control channel pull request is
  merged. After that, a rename needs `previous_names` in the channel entry,
  orphans users' `Packages/User/MarkdownGlance.sublime-settings` and keymap
  overrides, and changes the public `mdglance_` command and `mdglance.`
  context identifiers. Any further naming discussion must happen before
  submission; the name is frozen at submission.
