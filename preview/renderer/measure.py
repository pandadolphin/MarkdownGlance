"""How wide a table of contents or an outline wants to be, in pixels.

minihtml offers no way to ask a phantom for its natural width, so the width is
estimated from the text, the way `tables.budgets` estimates how many monospace
columns fit a preview: per-character advances for the font stacks in
`resources/preview.css`, at the root font size the current zoom gives.

The proportional advances are bucketed rather than tabulated. They target the
stack that actually resolves on each host -- Ubuntu on Linux, and Arial,
Helvetica or Open Sans elsewhere, whose advances agree to within a percent or
two -- and they run a few percent over it, so the estimate leans wide. DejaVu
Sans, the last named fallback, is about a tenth wider again; on a host that has
nothing but DejaVu the longest entry may wrap onto a second line, which the
slack below is sized to absorb for all but the very longest headings.
"""

import math
import unicodedata
from typing import Mapping, Sequence

from .tables import LATIN_ADVANCE, WIDE_WIDTHS

THIN = frozenset(" ilj.,;:!|'`")
NARROW = frozenset('ftrIJ()[]{}/\\-"')
BROAD = frozenset("mwMW@%")
THIN_ADVANCE = 0.28
NARROW_ADVANCE = 0.36
BROAD_ADVANCE = 0.90
UPPER_ADVANCE = 0.68
DIGIT_ADVANCE = 0.57
LOWER_ADVANCE = 0.56

# `stylesheet.PANEL_CSS`: 0.8rem of body padding each side, and for the table
# of contents 0.8rem of its own padding plus a 0.08rem border each side.
PANEL_BODY_REM = 1.6
PANEL_TOC_FRAME_REM = 1.76
# The outline's entries carry 0.3rem of padding; only the right side is width.
PANEL_OUTLINE_FRAME_REM = 0.3
# Room for the scrollbar a long list gets, and for the error in the estimate.
SCROLLBAR_REM = 0.9
SLACK_REM = 0.6

# `padding-left` per heading level, mirroring `resources/preview.css`.
TOC_INDENT_REM = {1: 0.0, 2: 0.8, 3: 1.6}
TOC_DEEP_INDENT_REM = 2.4
OUTLINE_INDENT_REM = {1: 0.3, 2: 1.3, 3: 2.6, 4: 3.9, 5: 5.2, 6: 6.5}


def _is_wide(character: str) -> bool:
    return unicodedata.east_asian_width(character) in WIDE_WIDTHS


def sans_width_em(text: str) -> float:
    """Width of proportional text, as a multiple of the font size."""
    total = 0.0
    for character in text:
        if _is_wide(character):
            total += 1.0
        elif character in THIN:
            total += THIN_ADVANCE
        elif character in NARROW:
            total += NARROW_ADVANCE
        elif character in BROAD:
            total += BROAD_ADVANCE
        elif character.isdigit():
            total += DIGIT_ADVANCE
        elif character.isupper():
            total += UPPER_ADVANCE
        else:
            total += LOWER_ADVANCE
    return total


def mono_columns(text: str) -> int:
    """Monospace columns the text occupies, counting CJK as two."""
    return sum(2 if _is_wide(character) else 1 for character in text)


def _indent_rem(level: int, table: Mapping[int, float], deep: float) -> float:
    return table.get(max(1, min(6, level)), deep)


def toc_width_px(headings: Sequence, rem_px: int) -> float:
    """Width the table of contents needs for its longest entry, in pixels."""
    if rem_px <= 0:
        return 0.0
    longest = max(
        (
            _indent_rem(heading.level, TOC_INDENT_REM, TOC_DEEP_INDENT_REM)
            + sans_width_em(heading.text)
            for heading in headings
        ),
        default=0.0,
    )
    if not longest:
        return 0.0
    chrome = PANEL_BODY_REM + PANEL_TOC_FRAME_REM + SCROLLBAR_REM + SLACK_REM
    return (longest + chrome) * rem_px


def outline_width_px(headings: Sequence, rem_px: int) -> float:
    """Width the outline needs for its longest entry, in pixels.

    The outline is monospace and every entry carries its `#` marker and one
    space, so it is counted in columns of one advance each, rounded up to whole
    pixels the way minihtml rounds them.
    """
    if rem_px <= 0:
        return 0.0
    advance = math.ceil(LATIN_ADVANCE * rem_px)
    widest = max(
        (
            _indent_rem(heading.level, OUTLINE_INDENT_REM, 6.5) * rem_px
            + (heading.level + 1 + mono_columns(heading.text or "(untitled)")) * advance
            for heading in headings
        ),
        default=0.0,
    )
    if not widest:
        return 0.0
    chrome = PANEL_BODY_REM + PANEL_OUTLINE_FRAME_REM + SCROLLBAR_REM + SLACK_REM
    return widest + chrome * rem_px
