# MarkdownGlance architecture

## 中文摘要

- production backend 为 scratch `View` + `PhantomSet`；`adapter/` 与 `presentation/` 是唯一可 import `sublime` 的 layers。
- 每个 source buffer 对应一个 session；每 session 只允许一个 in-flight render，generation check 保证 stale completion 不会覆盖新内容。
- renderer 为 pure `parse -> resolve -> serialise` pipeline；network 使用独立 bounded executor，callback 先回 UI thread 再更新 session。

## Boundaries

`adapter` translates Sublime commands and events into use cases. `application`
owns sessions, scheduling and orchestration through ports. `domain`, `renderer`
and `assets` are independently testable Python. `presentation` owns native
surfaces and layout bookkeeping.

The selected backend is a read-only scratch `View` containing one block
`Phantom`. Heading position ratios provide programmatic TOC navigation. Layout
ownership is fingerprinted; restoration occurs only for an empty, unchanged,
plugin-created group after its last holder closes.

## Reliability and safety

Each immutable `RenderRequest` contains a generation. A session has at most one
render in flight; edits coalesce and the newest requested generation dispatches
immediately after completion. Results return to the UI thread and are applied
only to a live session at its current generation.

Asset fetching uses a separate four-worker executor, a 64 MiB in-memory LRU,
30-second negative caching, HTTPS by default, at most five redirects, a 15-second
timeout, 10 MiB response limit, and 4096 px dimension limit. Only
`AssetKey.safe_label` is diagnostic-safe; Mermaid locators are never logged.

Decision details and experiment evidence are in the repository-level
`docs/adr/` directory.
