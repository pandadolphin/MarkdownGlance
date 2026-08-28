# MarkdownGlance

[![CI](https://github.com/pandadolphin/MarkdownGlance/actions/workflows/markdown-glance.yml/badge.svg)](https://github.com/pandadolphin/MarkdownGlance/actions/workflows/markdown-glance.yml)

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

Open **Preferences → Browse Packages…** in Sublime Text and clone this
repository into the directory it opens, under the name `MarkdownGlance`:

```bash
git clone https://github.com/pandadolphin/MarkdownGlance.git MarkdownGlance
```

Then open a Markdown file and run **MarkdownGlance: Open Preview to the Side**
from the Command Palette.

## Commands

| Command | Shortcut |
| --- | --- |
| MarkdownGlance: Open Preview to the Side | `Ctrl+K`, then `V` |
| MarkdownGlance: Toggle Preview | `Ctrl+Shift+V` |
| MarkdownGlance: Zoom In / Out / Reset Zoom | `Ctrl+=`, `Ctrl+-`, `Ctrl+0` |
| MarkdownGlance: Open Settings | — |
| MarkdownGlance: Copy Diagnostics | — |

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

## Contributing

Issues and pull requests are welcome. Run the tests from the parent of the
package directory, which must be named `MarkdownGlance`:

```bash
python -m unittest discover -s MarkdownGlance/tests -t . -p 'test_*.py'
```

CI runs the same suite on Linux, macOS and Windows against Python 3.8 — the
Sublime Text 4200 runtime — and 3.14. A behavioural change should come with a
test, and a decision that constrains the design belongs in a new ADR under
`docs/adr`.

## Acknowledgements

MarkdownGlance owes its idea to
[MarkdownLivePreview](https://github.com/math2001/MarkdownLivePreview) by
Mathieu Paturel — thank you for showing that a same-window Markdown preview
belongs in Sublime Text. MarkdownGlance is an independent implementation for
Sublime Text 4; the code here is its own.

## License

MIT. See [LICENSE](LICENSE). Vendored dependency attribution is recorded in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
