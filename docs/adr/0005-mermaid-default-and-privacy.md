# ADR 0005: Mermaid default and privacy

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
