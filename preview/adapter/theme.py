from typing import Dict

from ..domain.contracts import ThemeSnapshot


def _luminance(color: str) -> float:
    try:
        red, green, blue = (int(color[index : index + 2], 16) for index in (1, 3, 5))
    except (TypeError, ValueError):
        return 1.0
    return (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255.0


def theme_snapshot(view) -> ThemeSnapshot:
    style: Dict[str, str] = view.style() or {}
    background = style.get("background", "#ffffff")
    foreground = style.get("foreground", "#222222")
    accent = style.get("accent", style.get("bluish", "#4f8cc9"))
    return ThemeSnapshot(background, foreground, _luminance(background) < 0.5, accent)
