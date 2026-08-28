# MarkdownGlance implementation audit

## 中文摘要

- authoritative design 的 production scope 已实现：package identity、pure renderer、session/generation、selected backend、layout ownership、assets、TOC、zoom、settings、privacy copy 与 docs 均有 code/test evidence。
- Linux ST 4200 contract 与 real UI smoke 通过；CPython 3.8.20/3.14 pure suites 各 56 tests 通过。ST 4207 GUI testing 因 dev build 要求 license 未执行，但按批准决定不构成 blocker。
- 100-sample benchmark 为 p50 766.424 ms / p95 784.685 ms；高于 250 ms reference target，但 PRD 明确其不是 release gate。
- macOS/Windows 按批准决定 deferred。完整 release manual matrix 尚未执行；本记录验证 implementation，不宣称 public release acceptance。

## Requirement verification

| Area | Result | Evidence |
| --- | --- | --- |
| Identity and coexistence | Pass | ADR 0002; unique `MarkdownGlance`, `mdglance_` and `mdglance.` namespaces; metadata/keymap tests; both packages loaded in one isolated ST 4200 configuration. Expected default-shortcut precedence is documented. |
| Platform scope | Pass | the Package Control channel entry restricts releases to Linux; PRD, design, plan, README and manual plan defer macOS/Windows. |
| Backend decision | Pass | ADR 0001 and Phase 0 JSON/screenshots reject `HtmlSheet`; scratch `View` + `PhantomSet` passes the four Linux gates. Candidate A is absent from the production package. |
| FR-001/002/003 modes and commands | Pass with release-manual follow-up | state tests cover open/repeat, Side-by-Side/Full Screen, source preservation and focused branches; ST 4200 smoke confirms real group creation and Full Screen movement. Phase 0 proves focused-preview shortcut dispatch and synchronous close detection. |
| FR-010/011/012 live rendering | Pass | deterministic scheduler tests cover debounce, one in-flight render, latest-wins, close-during-flight, never-lost edits and failure recovery; saved/unsaved/Save As state tests include first-project-folder fallback; errors preserve prior HTML and use stage-only safe messages. |
| FR-020/021 Markdown and style | Pass | characterized dialect, malformed/raw HTML, sanitizer, stable heading and zoom tests; real ST 4200 dark-scheme smoke confirms px root sizing and word wrapping. Light and third-party schemes remain in the release manual matrix. |
| FR-030 local images | Pass | PNG/GIF/JPEG signature and dimension tests, extensionless image test, bounded local reads, intrinsic `rem` sizing and `max-width: 100%`; missing/invalid states use typed placeholders. |
| FR-031 remote images | Pass | canonical URL and credential rejection tests; mocked success, timeout, invalid, declared/streamed oversize and downgrade redirect tests; bounded network executor, LRU/negative cache, deduplication, waiter removal and policy-revision tests. |
| FR-040 Mermaid | Pass | opt-in conversion and exact payload test; disabled source remains code; shared resolver/policy/cache; settings, install message, README and first pending placeholder disclose host-only transmission. FR-041 remains P2. |
| FR-050 TOC | Pass | hierarchy/duplicate/active-ancestor tests; Phase 0 top/middle/bottom navigation evidence; ST 4200 live click confirms `6.1` navigation, active marking and a persistent separate TOC. |
| FR-060/061 zoom and links | Pass | per-session clamp/reset and no-rerender tests; body HTML is zoom-independent; source schemes are allowlisted, relative links use token + opaque index, absolute editor paths are rejected. |
| FR-070/071 settings and diagnostics | Pass | validation/default tests; `add_on_change` and detach implementation; policy revision invalidates/resubmits in-flight work; diagnostics contain only build/runtime/settings/stage names. |
| Architecture boundaries | Pass | Python 3.8 AST/import-boundary tests cover every pure layer; only `adapter/` and `presentation/` import `sublime`; renderer I/O is isolated behind the resolver port. |
| Lifecycle and cleanup | Pass | source/preview/TOC/window/unload/reconcile tests; reverse layout release; fingerprint test prevents overwriting user layout; executors and settings/theme callbacks are owned and detached. |
| Linux stable compatibility | Pass | ST 4200/Python 3.8.12 package load, backend contract JSON and real Side-by-Side/Full Screen UI smoke. |
| Python forward compatibility | Pass for pure code | 56 tests and compilation pass on CPython 3.14. Vendored `markdown2` emits two non-fatal invalid-escape `SyntaxWarning`s. |
| ST dev forward testing | Not run, non-blocking | Official build 4207 was downloaded and launched, but its GUI stops at `Enter License`. Stable ST 4200 is the only required integration gate. |
| Performance | Recorded deviation | `cpython-benchmark.json`: 102,446 bytes, 3 warmups, 100 samples, p50 766.424 ms, p95 784.685 ms. The 250 ms value is an initial non-gating reference target. |

## Self-review

The review found and fixed four defects before this audit: minihtml percentage
root sizing, disabled preview word wrap, TOC creation stealing focus, and
surface-close cleanup racing layout restoration. The final pass additionally
fixed missing project-folder fallback for untitled sources, non-canonical remote
asset keys, credential-bearing image URLs, unexpected fetch-future exceptions,
absolute editor links, implicit boolean key contexts, an unusably narrow TOC,
repository-shipped `package-metadata.json` causing Package Control to remove
the development symlink at startup, and `subl:` link commands rejecting ST
4200's injected `event` argument. TOC actions now locate their session by the
opaque token instead of relying on active-sheet focus.

No old lifecycle implementation or `bs4` code is imported. Generated command
links are validated by per-session random tokens; documents, locators and
response bodies do not enter errors or diagnostics.

## Deviations and deferred gates

1. The package was developed in a transitional `MarkdownGlance/` subdirectory
   of the `MarkdownLivePreview` repository and split into this repository with
   its history on 2026-08-28; package-internal paths did not change.
2. `word_wrap` is enabled on the scratch preview. The initial design's chrome
   suppression value clipped prose in real ST 4200; the authoritative design was
   updated to record this verified requirement.
3. The 100-sample p95 is 784.685 ms, above the 250 ms reference. `markdown2`
   2.5.0 was slower in a local comparison, so ADR 0003 retains 2.3.9 and records
   optimization as follow-up rather than changing dialect without evidence.
4. ST 4207/Python 3.14 GUI integration was not run because the dev build requires
   a license. This is optional future testing, not a blocker; required ST 4200
   integration and CPython 3.14 pure compatibility pass.
5. The full Linux release manual matrix (light/third-party themes and live
   network/offline cases) is not claimed complete. macOS/Windows are explicitly
   deferred future testing.
