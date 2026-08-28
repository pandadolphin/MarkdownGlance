# MarkdownGlance

[![CI](https://github.com/pandadolphin/MarkdownGlance/actions/workflows/markdown-glance.yml/badge.svg)](https://github.com/pandadolphin/MarkdownGlance/actions/workflows/markdown-glance.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Sublime Text](https://img.shields.io/badge/Sublime%20Text-4200%2B-orange.svg)](https://www.sublimetext.com/)

Live Markdown preview for Sublime Text 4, rendered in an editor group of the
same window — no browser, no WebView, no external process.

## Features

- Live preview of saved and unsaved buffers, Side-by-Side or Full Screen.
- Theme-aware styling that follows the active color scheme.
- A separate, navigable table of contents.
- Per-session zoom.
- Local images, and remote images fetched asynchronously under strict limits.
- GFM tables, typeset to the measured width of the preview.
- Optional Mermaid diagrams, disabled by default.

## Requirements

Sublime Text build 4200 or newer — that is the whole list. The package is pure
Python over the Sublime API, with no external dependency, and it is used on
Linux, macOS and Windows.

## Installation

### Package Control

Open the Command Palette, run **Package Control: Install Package**, and choose
**MarkdownGlance**.

### Manually

Open **Preferences → Browse Packages…** in Sublime Text and clone this
repository into the directory it opens, under the name `MarkdownGlance`:

```bash
git clone https://github.com/pandadolphin/MarkdownGlance.git MarkdownGlance
```

Either way, open a Markdown file and run **MarkdownGlance: Open Preview to the
Side** from the Command Palette.

## Commands

| Command | Shortcut |
| --- | --- |
| MarkdownGlance: Open Preview to the Side | `Ctrl+K`, then `V` |
| MarkdownGlance: Toggle Preview | `Ctrl+Shift+V` |
| MarkdownGlance: Zoom In / Out / Reset Zoom | `Ctrl+=`, `Ctrl+-`, `Ctrl+0` |
| Preferences: MarkdownGlance Settings | — |
| Preferences: MarkdownGlance Key Bindings | — |
| MarkdownGlance: Copy Diagnostics | — |

On macOS, `Cmd` replaces `Ctrl`. The zoom keys apply only while the preview
itself is focused. `Ctrl+Shift+V` is the one key the package takes from Sublime
Text: it shadows Paste and Indent while a Markdown source view or an owned
preview is focused, and `Ctrl+K`, `Ctrl+V` still pastes from history —
[ADR 0009](docs/adr/0009-full-screen-toggle-returns-to-ctrl-shift-v.md) has the
reasoning. Edit the
defaults from **Preferences → Package Settings → MarkdownGlance → Key
Bindings**; every command is in the command palette with or without a binding.

The open and toggle commands also work while an owned preview has focus.
Closing the source closes its preview; closing the preview never closes or
recreates the source. A group created by the plugin is restored only if its
layout has not been changed since.

## Settings

Run **MarkdownGlance: Open Settings** to see every setting with its default and
a comment. The defaults are conservative: Mermaid off, insecure remote images
blocked, and remote fetches bounded by timeout, payload size and dimension.

## Tables

Sublime Text's minihtml cannot lay out a table, so tables are typeset as
aligned monospace columns sized to the measured width of the preview: they fill
the group and re-fit when the window is resized. `table_max_columns` (200) only
caps that on a very wide screen. See
[ADR 0007](docs/adr/0007-table-rendering-under-minihtml.md).

## Network and privacy

Remote images are fetched off the UI thread with scheme, redirect, timeout,
payload and dimension limits, and are cached only in memory. Mermaid is
disabled by default; enabling it sends diagram source to the configured Mermaid
server. Diagnostics redact source text, paths, URLs and Mermaid payloads.

## Documentation

- [Architecture](docs/architecture.md)
- [Architecture decision records](docs/adr)
- [Migrating from MarkdownLivePreview](docs/migration.md)
- [Manual test plan](docs/manual-test-plan.md)
- [Changelog](CHANGELOG.md)
- [Security policy](SECURITY.md)

## Contributing

Issues and pull requests are welcome. [CONTRIBUTING.md](CONTRIBUTING.md) covers
running the tests, trying a change inside Sublime Text, and what a pull request
should carry. In short:

```bash
python -m unittest discover -s MarkdownGlance/tests -t . -p 'test_*.py'
```

run from the parent of the package directory, which must be named
`MarkdownGlance`. CI runs the same suite on Linux, macOS and Windows against
Python 3.8 — the Sublime Text 4200 runtime — and 3.14.

## Acknowledgements

MarkdownGlance owes its idea to
[MarkdownLivePreview](https://github.com/math2001/MarkdownLivePreview) by
Mathieu Paturel — thank you for showing that a same-window Markdown preview
belongs in Sublime Text. MarkdownGlance is an independent implementation for
Sublime Text 4; the code here is its own.

## License

MIT. See [LICENSE](LICENSE). Vendored dependency attribution is recorded in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
