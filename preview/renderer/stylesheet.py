from html import escape

from ..domain.contracts import ThemeSnapshot


def stylesheet(theme: ThemeSnapshot, zoom: float, base_css: str) -> str:
    zoom = max(0.5, min(3.0, zoom))
    return """<style>
    html {{ font-size: {}px; }}
body {{ background-color: {}; color: {}; }}
a {{ color: {}; }}
{}
</style>""".format(
        round(zoom * 16),
        escape(theme.background),
        escape(theme.foreground),
        escape(theme.accent),
        base_css,
    )


def represent(body_html: str, theme: ThemeSnapshot, zoom: float, base_css: str) -> str:
    return "{}\n{}".format(stylesheet(theme, zoom, base_css), body_html)
