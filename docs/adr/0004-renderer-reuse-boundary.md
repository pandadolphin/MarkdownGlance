# ADR 0004: Renderer reuse boundary

## Status

Accepted.

## Decision

The assets below are this repository's own implementations from its fork stage,
the ones the rewrite had to keep, replace or drop. The single exception is
`lib/markdown2.py`, which is vendored third-party code.

| Existing asset | Decision |
| --- | --- |
| `lib/markdown2.py` 2.3.9 | Vendor unchanged with MIT attribution |
| `resources/stylesheet.css` | Retain as `resources/preview.css`; add error, blocked-link, image and active-TOC rules |
| `get_image_size` behavior | Reimplement as pure signature-based PNG/GIF/JPEG detection with malformed-input errors |
| Mermaid JSON/base64url encoding | Retain in `assets/mermaid.py`; theme and `bgColor` follow the colour scheme |
| Renderer/TOC tests and fixtures | Port and expand as characterization tests |
| BeautifulSoup tree/string mutation | Replace with stdlib structured tree and allowlisted serializer |
| module globals for image cache/loading/executor | Replace with injected bounded cache, resolver and network executor |
| current lifecycle/window-moving code | Do not reuse |
| `HtmlSheet` prototype | Evidence only; exclude from production package |

`lib/markdown2.py` keeps its own copyright and MIT notice in the vendored
source and in `THIRD_PARTY_NOTICES.md`. Everything else the rewrite retains is
this repository's own work under its MIT license. No external runtime
dependency is required by MarkdownGlance.

## Consequences

The new renderer is `parse` → `resolve` → `serialise`. Only `resolve` performs
I/O. Renderer output is viewport- and zoom-independent; presentation adds the
theme/zoom stylesheet without reparsing Markdown. The old package remains
untouched during coexistence testing.
