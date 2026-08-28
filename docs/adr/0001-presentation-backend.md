# ADR 0001: Presentation backend

## Status

Accepted.

## Context

The detailed design requires the same contract and gate procedure for
`HtmlSheet` and scratch `View` + `PhantomSet`. A backend ADR must be approved
before production presentation code begins. The experiment uses only the
provisional `mdpreview_phase0_*` namespace.

## Evidence

Environment: Sublime Text build 4200 stable on Linux x64. The experiment ran in
the existing package's Python 3.3 runtime because switching this repository to
Python 3.8 makes the current `bs4` dependency unavailable; the independent
package and dependency decisions remain Phase 1 gates.

The shared create/update/move/reveal/focus/close contract passes for both
candidates in [`phase0/contract-build-4200.json`](phase0/contract-build-4200.json).

### Candidate A — `HtmlSheet`

The fixed 1280 × 900 run rendered the complete 200-section fixture. Eleven
captures were pixel-identical across ten verified `set_contents()` updates;
`SCROLL-ANCHOR-100` remained at pixels 656–675. Clicking the inline
`#section-100` link produced no movement, and `Ctrl+Shift+V` did not dispatch
while the `HtmlSheet` was focused. Keyboard close was observed as the `close`
window command and reconciliation ran in the next UI callback.

See the [event log](phase0/linux-build-4200-html_sheet-phase0.json),
[measurements](phase0/linux/html_sheet/scroll-measurements.json), and adjacent
screenshots. Navigation and focused shortcut are hard gate failures.

### Candidate B — scratch `View` + `PhantomSet`

The 1280 × 900 Linux control run used the default dark scheme, 100% scaling,
hidden sidebar/minimap, and a fixed 500 ms settle interval. Across the baseline
and ten updates, `SCROLL-ANCHOR-100` remained at pixels 327–346 with a maximum
top-edge delta of 0 pixels. See
[`phase0/linux/phantom_view/scroll-measurements.json`](phase0/linux/phantom_view/scroll-measurements.json)
and the adjacent `scroll-00.png` through `scroll-10.png`.

The Linux runs also recorded:

- programmatic navigation to sections 001, 100, and 200 returned `true` and
  visibly reached each preview heading;
- the focused-preview shortcut switched to Side-by-Side with one owned surface;
- mouse tab close and keyboard `Ctrl+W` produced synchronous `on_pre_close`, and
  the following UI callback restored the original 1×1 layout;
- `close_pane` moved the still-live preview into the surviving group, so no
  session close occurred; window close produced synchronous `on_pre_close` and
  correctly skipped layout restoration.

See the [event log](phase0/linux-build-4200-phantom_view-phase0.json),
[close matrix](phase0/linux/phantom_view/close-matrix.json), navigation
screenshots, and scroll measurements under `phase0/linux/phantom_view/`.

## Decision

Select Candidate B: scratch `View` + `PhantomSet`.

Its navigation capability is `PROGRAMMATIC`, using recorded heading position
ratios with `layout_extent()` and `set_viewport_position()`. The production TOC
therefore uses a separate owned surface. Candidate A is excluded from the
release package. The evidence stays under `phase0/`; the harness
(`phase0_backend_experiment.py`, `Phase0.sublime-commands` and the
`mdpreview_phase0_*` keymap entries) runs in the old package's Python 3.3
runtime and remains in the `MarkdownLivePreview` repository at commit `a87cf7e`.

## Required follow-up

1. Use the `MarkdownGlance` identity selected by ADR 0002 and complete the
   Markdown dialect and renderer reuse ADRs before production implementation.
2. Promote only Candidate B into the production package and port the shared
   backend contract tests.
3. Track macOS and Windows as non-blocking future compatibility testing.
