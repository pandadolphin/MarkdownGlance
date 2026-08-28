# Changelog

All notable changes to MarkdownGlance are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.1...HEAD
[0.1.1]: https://github.com/pandadolphin/MarkdownGlance/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/pandadolphin/MarkdownGlance/releases/tag/0.1.0
