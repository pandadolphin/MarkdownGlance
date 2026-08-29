# Changelog

All notable changes to MarkdownGlance are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/pandadolphin/MarkdownGlance/compare/0.2.0...HEAD
[0.2.0]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.4...0.2.0
[0.1.4]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.2...0.1.3
[0.1.2]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/pandadolphin/MarkdownGlance/releases/tag/0.1.0
