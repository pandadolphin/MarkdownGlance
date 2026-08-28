# MarkdownGlance

## 中文摘要

- `MarkdownGlance` 是 Sublime Text 4 的 same-window live Markdown preview；首个 release 仅以 Linux、build 4200+ 为 required platform。
- Side-by-Side、Full Screen、TOC、zoom、local/remote images 与 opt-in Mermaid 均由 native scratch `View` + `PhantomSet` 实现。
- 与 `MarkdownLivePreview` 可并存，但默认 shortcuts 重叠；migration 期间应 disable 旧 package 的 key bindings 或自定义其中一套。

MarkdownGlance renders live Markdown in Sublime Text editor groups without a
browser or WebView. It supports saved and unsaved buffers, theme-aware styling,
a separate navigable TOC, per-session zoom, local and bounded asynchronous
remote images, GFM tables, and optional Mermaid diagrams.

Sublime Text's minihtml cannot lay out a table, so tables are typeset as aligned
monospace columns sized to the measured width of the preview: they fill the
group and re-fit when the window is resized. `table_max_columns` (200) only caps
that on a very wide screen. See
[ADR 0007](docs/adr/0007-table-rendering-under-minihtml.md).

## Requirements and installation

- Linux
- Sublime Text build 4200 or newer

Install the `MarkdownGlance` directory as a package. The package has no external
Python dependency. macOS and Windows compatibility testing is deferred.

## Commands

- `MarkdownGlance: Open Preview to the Side` — `Ctrl+K`, then `V`
- `MarkdownGlance: Toggle Preview` — `Ctrl+Shift+V`
- `MarkdownGlance: Zoom In/Out/Reset Zoom` — `Ctrl+=`, `Ctrl+-`, `Ctrl+0`
- `MarkdownGlance: Open Settings`
- `MarkdownGlance: Copy Diagnostics`

The open and toggle commands work while an owned preview has focus. Closing the
source closes its preview; closing the preview never closes or recreates the
source. A plugin-created group is restored only if the user has not changed its
layout.

## Network and privacy

Remote images are fetched off the UI thread with scheme, redirect, timeout,
payload and dimension limits. They are cached only in memory. Mermaid is
disabled by default; enabling it sends diagram source to the configured Mermaid
server. Diagnostics redact source text, paths, URLs and Mermaid payloads.

See [migration.md](docs/migration.md) and
[manual-test-plan.md](docs/manual-test-plan.md).

MarkdownGlance is MIT-licensed. Vendored dependency attribution is recorded in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
