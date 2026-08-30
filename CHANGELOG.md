# Changelog

All notable changes to MarkdownGlance are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`enable_toc`, and it defaults to `false`.** The table of contents beside
  the preview takes an editor group of its own, which is a lot to spend without
  being asked for; set it to `true` for the old behaviour, where a document
  past `toc_minimum_length` and `toc_minimum_headings` gets one.

- **`auto_width`, defaulting to `true`.** The table of contents and the outline
  are given the width their longest heading needs instead of a fixed share of
  the window, so the rest goes to the content. It is a ceiling, not a target:
  neither group is ever wider than it used to be. Dragging the divider yourself
  turns it off for that group, and setting `auto_width` to `false` restores the
  fixed share everywhere. See
  [ADR 0011](docs/adr/0011-panel-width-fits-its-content.md).

### Changed

- The table of contents and the outline no longer carry the preview's page
  margins. They are lists in a narrow group, so they get 0.8rem of padding
  rather than the document's 1.5rem, and the table of contents loses the margin
  above its card.

- Closing the table of contents now keeps it closed for that preview. It used
  to reappear within a second, because every render reopens one for a document
  that qualifies and the viewport poll renders again as soon as the preview
  grows into the group just given back. A close is remembered until the preview
  itself is closed and reopened, or until `enable_toc` is switched off and on.

### Fixed

- Closing the table of contents from its tab left its empty group behind. The
  group was released by asking the backend which group the surface was in, but
  the view is already gone by then and a dead handle has no group, so nothing
  was released and the pane stayed on screen. The session now records the group
  it placed the table of contents in and falls back to it.

## [0.2.1] - 2026-08-29

### Changed

- Documentation only; no code, settings or key bindings change. The README now
  opens with a screenshot of the preview, its Mermaid diagram, an aligned table
  and the table of contents beside them, and the outline screenshot shows the
  outline reading this repository's own README. Both images live in
  `docs/screenshots/`, which `export-ignore` keeps out of the installed
  package.

## [0.2.0] - 2026-08-29

### Added

- **An outline of the Markdown source**, on `Ctrl+Shift+B` / `Cmd+Shift+B` and
  as `MarkdownGlance: Toggle Outline` in the command palette. It lists the
  headings as they are written in the buffer, in a group of its own beside the
  file, marks the one holding the caret, re-scans as you type, and moves the
  caret to a heading when its entry is clicked. It needs no preview and no
  successful render, which is what separates it from the table of contents
  inside the preview. The key toggles the way Zed's outline panel does — open
  and focus, focus, then close from inside — and shadows Sublime Text's
  **Build With…** only while a Markdown source view or an outline this package
  created is focused. See
  [ADR 0010](docs/adr/0010-source-outline-and-ctrl-shift-b.md).

## [0.1.4] - 2026-08-29

### Changed

- The **Settings** menu item and the `Preferences: MarkdownGlance Settings`
  palette entry now call `edit_settings` with `base_file` directly, the form
  every other package uses, instead of routing through a package command.
- The vendored copy of markdown2 no longer carries its command-line mainline.
  A Sublime Text package never runs it, and it brought `optparse`, a
  `Markdown.pl` comparison through `subprocess.Popen` and a `sys.path` insert
  with it. Two regex literals are raw strings now, so recent Python versions
  stop warning about invalid escape sequences. The library API is unchanged.

### Removed

- The `mdglance_open_settings` command. Anything bound to it should call
  `edit_settings` with
  `"base_file": "${packages}/MarkdownGlance/MarkdownGlance.sublime-settings"`.

## [0.1.3] - 2026-08-29

### Fixed

- **The Full Screen toggle is `Ctrl+Shift+V` again** (`Cmd+Shift+V` on macOS).
  The `Ctrl+K`, `Shift+V` chord that 0.1.2 moved it to never fired: Sublime Text
  lists it in the command palette but does not dispatch it, and its own keymap
  binds no chord whose second key is bare or shift-only. Taking the key back
  costs Paste and Indent while a Markdown source view is focused, where
  **Edit → Paste and Indent** still runs it by name; removing one entry from
  **Preferences → Package Settings → MarkdownGlance → Key Bindings** undoes it.
  See [ADR 0009](docs/adr/0009-full-screen-toggle-returns-to-ctrl-shift-v.md).

## [0.1.2] - 2026-08-28

### Changed

- **The Full Screen toggle moved from `Ctrl+Shift+V` to `Ctrl+K`, `Shift+V`**
  (`Cmd+K`, `Shift+V` on macOS). `Ctrl+Shift+V` is Sublime Text's own Paste and
  Indent, and a context that fires exactly while you are editing Markdown is
  exactly when you reach for it. The new chord collides with nothing on any
  platform. See [ADR 0008](docs/adr/0008-default-key-bindings.md).

## [0.1.1] - 2026-08-28

### Added

- **Preferences → Package Settings → MarkdownGlance → Key Bindings**, and the
  matching `Preferences: MarkdownGlance Key Bindings` palette entry, both
  opening the defaults beside your overrides.

### Changed

- The settings entry is now `Preferences: MarkdownGlance Settings`, following
  the convention the rest of Sublime Text uses.
- The installed package no longer carries the documentation, the ADRs or the
  test suite — 310 KB instead of 3.2 MB.

### Removed

- `Run Contract Tests` and `Run Benchmark` no longer appear in the command
  palette. They are developer commands; run them from the console with
  `window.run_command("mdglance_run_contract_tests")`.

## [0.1.0] - 2026-08-28

First public release.

### Added

- Same-window live Markdown preview for saved and unsaved buffers, in either a
  Side-by-Side or a Full Screen editor group.
- Theme-aware styling that follows the active color scheme, and per-session
  zoom.
- A separate, navigable table of contents.
- Local images, and remote images fetched asynchronously under scheme,
  redirect, timeout, payload and dimension limits, cached only in memory.
- GFM tables, typeset to the measured width of the preview.
- Opt-in Mermaid rendering, disabled by default; diagram source reaches the
  configured server only once it is enabled.
- `MarkdownGlance: Copy Diagnostics`, which redacts source text, paths, URLs
  and Mermaid payloads.

[Unreleased]: https://github.com/pandadolphin/MarkdownGlance/compare/0.2.1...HEAD
[0.2.1]: https://github.com/pandadolphin/MarkdownGlance/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.4...0.2.0
[0.1.4]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.2...0.1.3
[0.1.2]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/pandadolphin/MarkdownGlance/releases/tag/0.1.0
