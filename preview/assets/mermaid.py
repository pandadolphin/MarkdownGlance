import base64
import json
from string import hexdigits
from typing import Tuple

from ..domain.contracts import ThemeSnapshot

# mermaid.ink renders on a transparent background unless asked otherwise, and
# its light theme draws sequence message labels straight onto it in #333. On a
# dark colour scheme those labels disappear while the filled actor boxes stay,
# so the diagram has to be told which way round the preview is.
DARK_FALLBACK = "1e1e1e"
LIGHT_FALLBACK = "ffffff"


def background_hex(theme: ThemeSnapshot) -> str:
    """The six hex digits mermaid.ink takes for `bgColor`, alpha dropped."""
    colour = theme.background.lstrip("#")
    if len(colour) in (3, 4):
        colour = "".join(digit * 2 for digit in colour[:3])
    colour = colour[:6]
    if len(colour) == 6 and all(digit in hexdigits for digit in colour):
        return colour.lower()
    return DARK_FALLBACK if theme.is_dark else LIGHT_FALLBACK


def diagram_appearance(theme: ThemeSnapshot) -> Tuple[str, str]:
    """The part of a theme that reaches the image: same pair, same diagram.

    The server bakes the image, so unlike the preview's own HTML it cannot be
    re-coloured by a repaint. Two themes that agree here share a URL, and a
    cached diagram; two that do not need a new one fetched.
    """
    return ("dark" if theme.is_dark else "default", background_hex(theme))


def mermaid_image_url(diagram: str, server: str, theme: ThemeSnapshot) -> str:
    name, background = diagram_appearance(theme)
    payload = json.dumps(
        {"code": diagram, "mermaid": {"theme": name}},
        separators=(",", ":"),
    ).encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    return "{}/img/{}?type=png&bgColor={}".format(
        server.rstrip("/"), encoded, background
    )
