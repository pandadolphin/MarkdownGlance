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
