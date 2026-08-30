# A table of contents for raw Markdown

![The outline of the project README beside the file, headings indented by level with the one holding the caret highlighted](../../screenshots/source-outline.png)

The preview's table of contents is built from the rendered document, so it
needs a preview, a successful render and two thresholds before it appears, and
it scrolls the preview. This feature is the other half: an **outline** of the
source buffer, opened on `Ctrl+Shift+B` (`Cmd+Shift+B`), which needs none of
them and moves the caret in the file instead.

## Behaviour

- **The key** toggles the way Zed's outline panel does: it opens the outline
  and focuses it; a second press from the source focuses it again; a press from
  inside it closes it and returns focus to the file.
- **The list** shows headings as they are written — `#` markers, raw text,
  indented by level, in the preview's monospace family.
- **The caret** decides the highlighted entry: the nearest heading at or above
  it, with the chain of headings above that one marked as ancestors. It follows
  the caret as it moves and the list re-scans as the file is edited, after
  `update_delay_ms`.
- **A click** moves the caret to that heading's line, centres it in the source
  view, and leaves focus in the outline.
- **One outline per file**, in a group acquired beside everything already in
  the row, so it never lands as a tab in the preview's group. It is revealed
  when its source is activated, renamed with it, and closed with it.
- **The group is as wide as the longest entry needs**, never wider than the
  0.3 share it used to take, and re-fitted as the file is edited, zoomed or the
  window resized. Drag the divider and it stays where you put it;
  `"auto_width": false` gives it the fixed share instead.

## Where it lives

| Concern | File |
| --- | --- |
| Scanning raw Markdown for headings | `preview/renderer/outline.py` |
| Sessions, caret tracking, navigation | `preview/application/outline.py` |
| Reading text and caret, revealing a line | `preview/adapter/source_access.py` |
| Command, key context, event routing | `preview/adapter/{commands,events}.py` |
| A group that is never shared | `LayoutOwner.acquire_beside` |
| Width from the longest entry | `preview/renderer/measure.py`, `LayoutOwner.fit` |
| Styling | `resources/preview.css`, `.source-outline*` |
| Tests | `tests/unit/test_outline.py`, `tests/state/test_outline.py` |

The scan handles ATX (`#`…`######`, closing hashes stripped) and setext
(`===`, `---`) headings, and skips fenced code blocks and YAML front matter, so
a `# comment` inside a fence and the closing `---` of front matter are not
mistaken for headings.

[ADR 0010](../../adr/0010-source-outline-and-ctrl-shift-b.md) records why the
outline is a separate surface rather than a mode of the preview's TOC, and what
`Ctrl+Shift+B` costs. [ADR 0011](../../adr/0011-panel-width-fits-its-content.md)
records how its width is measured.
