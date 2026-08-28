# MarkdownGlance manual test plan

## 中文摘要

- release gate 仅覆盖 Linux ST 4200/Python 3.8 stable；newest dev/Python 3.14、macOS 与 Windows testing 均不阻塞 release。
- 必测 saved/unsaved、两种 modes、三种 themes、tables、images、TOC、zoom、Mermaid、layout/lifecycle 和 coexistence。
- 每次 run 记录 build/runtime、结果、screenshots 与 deviations；不可用的 environment 标为 blocked，不可记 pass。

## Matrix

Run the release matrix on Linux with Sublime Text build 4200/Python 3.8. The
newest available dev build/Python 3.14, macOS and Windows are optional future
compatibility testing.

1. Open saved and unsaved Markdown in Side-by-Side and Full Screen; repeat open
   and toggles from source, preview and TOC focus.
2. Edit, save, Save As, rename and delete on disk. Confirm the latest edit wins,
   the title/base path update, and the source is never closed or recreated.
3. Check default light, default dark and one third-party scheme; change scheme
   while open. Exercise keyboard and mouse zoom, then reset.
4. Check short, Unicode, malformed/raw HTML and 100 KiB documents. For TOC,
   test below-threshold, nested and duplicate headings and top/middle/bottom
   navigation.
5. Check tables: narrow, wider than the preview, right/centre aligned, CJK and
   mixed CJK/Latin, links and bold inside cells, and a raw HTML table. Confirm
   every row stays on the column grid and no row is wrapped by the host. Resize
   and maximise the window, and zoom in and out: the table refits within about
   a second and still fills the group.
6. Check relative, absolute, missing, oversized and extensionless local images;
   HTTPS, redirect, timeout, invalid and oversized remote images.
7. Check Mermaid disabled, enabled disclosure, offline, timeout, invalid source
   and custom HTTPS server. Confirm diagnostics contain no source or locator.
8. Close TOC, preview, source, group and window; reload the plugin. Change the
   layout after preview creation and confirm it is not overwritten on close.
9. Install beside MarkdownLivePreview. Check directory, module, command,
   settings and resource isolation; document the expected shortcut collision.

## Automated prerequisites

Run `python -m unittest discover -s MarkdownGlance/tests -t . -p 'test_*.py'` from the parent of the `MarkdownGlance` checkout, Python
compilation, `MarkdownGlance: Run Contract Tests`, and the 100-sample benchmark.
Attach JSON evidence from `docs/verification/` to the release record.
