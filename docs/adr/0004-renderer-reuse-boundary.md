# ADR 0004: Renderer reuse boundary

## 中文摘要

- 保留 `markdown2`、base CSS、PNG/GIF/JPEG header detection、Mermaid payload encoding 与现有 regression fixtures。
- 重写 lifecycle、TOC string surgery、image/network globals、cache 与 HTML serialization；production package 不包含 Candidate A 或 `bs4`。
- 所有 retained third-party code 继续使用原 MIT attribution；network 与 renderer executor 完全分离。

## Status

Accepted.

## Decision

| Existing asset | Decision |
| --- | --- |
| `lib/markdown2.py` 2.3.9 | Vendor unchanged with MIT attribution |
| `resources/stylesheet.css` | Retain as `resources/preview.css`; add error, blocked-link, image and active-TOC rules |
| `get_image_size` behavior | Reimplement as pure signature-based PNG/GIF/JPEG detection with malformed-input errors |
| Mermaid JSON/base64url encoding | Retain exactly in `assets/mermaid.py` |
| Renderer/TOC tests and fixtures | Port and expand as characterization tests |
| BeautifulSoup tree/string mutation | Replace with stdlib structured tree and allowlisted serializer |
| module globals for image cache/loading/executor | Replace with injected bounded cache, resolver and network executor |
| current lifecycle/window-moving code | Do not reuse |
| `HtmlSheet` prototype | Evidence only; exclude from production package |

The retained parser and asset files remain covered by the repository MIT
license. Its copyright and MIT notice are preserved in the vendored source and
the package-level `LICENSE`. No external runtime dependency is required by
MarkdownGlance.

## Consequences

The new renderer is `parse` → `resolve` → `serialise`. Only `resolve` performs
I/O. Renderer output is viewport- and zoom-independent; presentation adds the
theme/zoom stylesheet without reparsing Markdown. The old package remains
untouched during coexistence testing.
