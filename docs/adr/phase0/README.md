# Phase 0 presentation backend experiment

Run `Markdown Preview Phase 0: Run Backend Contracts` first. Then run each
backend with the same window, fixture, theme, zoom, and interaction sequence.

1. Set the window to 1280 x 900 logical pixels, hide sidebar and minimap, use
   the default dark scheme, and keep OS scaling at 100%.
2. Begin one backend. Navigate to `SCROLL-ANCHOR-100` and place its top edge at
   one third of the viewport. Capture the baseline screenshot.
3. Run `mdpreview_phase0_update` ten times. After each command returns, wait
   exactly 500 ms and capture a screenshot.
4. Test navigation to sections 001, 100, and 200. For `HtmlSheet`, click the
   inline fragment links; for `PhantomView`, run `mdpreview_phase0_navigate`
   with `target` set to `1`, `100`, and `200`.
5. Close by mouse, keyboard, group close, and window close in separate runs.
6. With the preview focused, press the platform Full Screen shortcut and switch
   modes twice. Record the gate result with `mdpreview_phase0_record`.
7. Run `mdpreview_phase0_finish`; retain the JSON log, eleven screenshots, and
   marker pixel measurements for each backend on Linux.

The provisional commands and contexts are isolated under the
`mdpreview_phase0_*` namespace. A safety-net activation event does not count as
a close-detection pass. Linux is the only required platform; macOS and Windows
runs are deferred, non-blocking future compatibility testing.
