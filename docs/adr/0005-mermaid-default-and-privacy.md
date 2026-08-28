# ADR 0005: Mermaid default and privacy

## 中文摘要

- `enable_mermaid` 默认值为 `false`；用户启用后 diagram source 才会发送到 configured HTTPS server。
- install message 与 settings 在首次启用前披露 network behavior；diagnostics 在任何模式下都不记录 Mermaid URL/path。

## Status

Accepted.

## Decision

Mermaid rendering is opt-in. `enable_mermaid` defaults to `false`; disabled
fences remain readable code. Settings and install copy state that enabling it
sends diagram source to `mermaid_server`. The first pending diagram in each
render includes a one-time host-only privacy caption.

Mermaid uses the same HTTPS, redirect, timeout, byte, dimension, cache and
generation controls as remote images. Its locator is never logged, including
when `debug_logging` is enabled, because the encoded URL path contains the
diagram source.
