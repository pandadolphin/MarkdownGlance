# ADR 0006: Cache limits and settings migration

## Status

Accepted.

## Decision

Use a 64 MiB in-memory LRU measured by encoded data-URI cost and a 30-second
negative-cache TTL. Remote and local images share the configured 10 MiB payload
and 4096 px dimension defaults. Every cache hit is re-evaluated against the
current policy revision, so tightened settings take effect without a flush.

Do not copy settings automatically from `MarkdownLivePreview`. The packages
must coexist, their behavior and defaults differ, and implicit copying makes a
rollback ambiguous. Document the small compatible-key mapping instead.

## Consequences

The cache is bounded and process-local; persistence remains P2. Users opt into
Mermaid explicitly and migrate other compatible values manually.
