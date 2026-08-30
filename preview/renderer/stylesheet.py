from html import escape

from ..domain.contracts import ThemeSnapshot

# A table of contents or an outline is the only thing in a narrow group of its
# own, so the page margins `preview.css` gives a document are lost width there.
# The override lives here rather than in the stylesheet because it is `body` it
# has to reach, and no class can: each surface gets its own phantom, and so its
# own `<style>` block. `measure.PANEL_*_REM` mirrors these numbers.
PANEL_CSS = """
body { padding: 0.7rem 0.8rem; }
.table-of-contents { margin: 0; padding: 0.7rem 0.8rem; }
"""


def root_font_px(zoom: float) -> int:
    """The px value of 1rem in the preview, which minihtml needs in px."""
    return round(max(0.5, min(3.0, zoom)) * 16)


def stylesheet(
    theme: ThemeSnapshot, zoom: float, base_css: str, panel: bool = False
) -> str:
    return """<style>
    html {{ font-size: {}px; }}
body {{ background-color: {}; color: {}; }}
a {{ color: {}; }}
{}{}
</style>""".format(
        root_font_px(zoom),
        escape(theme.background),
        escape(theme.foreground),
        escape(theme.accent),
        base_css,
        PANEL_CSS if panel else "",
    )


def represent(
    body_html: str,
    theme: ThemeSnapshot,
    zoom: float,
    base_css: str,
    panel: bool = False,
) -> str:
    return "{}\n{}".format(stylesheet(theme, zoom, base_css, panel), body_html)
