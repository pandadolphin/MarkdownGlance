"""The outline of a Markdown *source* buffer.

The table of contents in `toc.py` is built from the parsed preview document, so
it exists only once a render has succeeded. This module reads the raw buffer
instead: it is what the outline surface shows beside a Markdown file that has no
preview open at all, and it stays a line-based scan so that every entry can be
mapped back to the row the caret has to move to.
"""

import json
import re
from html import escape
from typing import List, Optional, Sequence, Tuple

from ..domain.contracts import SourceHeading

# CommonMark: up to three leading spaces, one to six hashes, then either the end
# of the line or a space before the text. `#hashtag` is not a heading.
ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
CLOSING_HASHES = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
FRONT_MATTER = re.compile(r"^(-{3,})[ \t]*$")


def _atx(line: str) -> Optional[Tuple[int, str]]:
    match = ATX.match(line)
    if match is None:
        return None
    body = match.group(2) or ""
    text = CLOSING_HASHES.sub("", body).strip()
    return len(match.group(1)), text


def scan_outline(text: str) -> Tuple[SourceHeading, ...]:
    """Locate ATX and setext headings in Markdown source, by line."""
    lines = text.split("\n")
    headings: List[SourceHeading] = []
    fence: Optional[Tuple[str, int]] = None
    start = 0

    # A YAML front matter block opens on the very first line; its closing rule
    # would otherwise read as a setext underline for the last key in it.
    if lines and FRONT_MATTER.match(lines[0]):
        for index in range(1, len(lines)):
            if FRONT_MATTER.match(lines[index]) or lines[index].rstrip() == "...":
                start = index + 1
                break

    for index in range(start, len(lines)):
        line = lines[index]
        opening = FENCE.match(line)
        if fence is not None:
            if (
                opening is not None
                and opening.group(1)[0] == fence[0]
                and len(opening.group(1)) >= fence[1]
                and not opening.group(2).strip()
            ):
                fence = None
            continue
        if opening is not None:
            fence = (opening.group(1)[0], len(opening.group(1)))
            continue

        atx = _atx(line)
        if atx is not None:
            level, heading_text = atx
            headings.append(
                SourceHeading(level, heading_text, len(headings), index)
            )
            continue

        underline = SETEXT.match(line)
        if underline is None or index == start:
            continue
        previous = lines[index - 1]
        # The underlined line has to be a paragraph: not blank, not a fence, and
        # not a heading already claimed above.
        if (
            not previous.strip()
            or FENCE.match(previous) is not None
            or _atx(previous) is not None
            or (headings and headings[-1].line == index - 1)
        ):
            continue
        headings.append(
            SourceHeading(
                1 if underline.group(1)[0] == "=" else 2,
                previous.strip(),
                len(headings),
                index - 1,
            )
        )
    return tuple(headings)


def active_ordinal(
    headings: Sequence[SourceHeading], row: int
) -> Optional[int]:
    """The heading the caret sits under, which is the last one at or above it."""
    active = None
    for heading in headings:
        if heading.line > row:
            break
        active = heading.ordinal
    return active


def build_outline(
    headings: Sequence[SourceHeading],
    action_token: str,
    active: Optional[int] = None,
) -> str:
    if not headings:
        return (
            '<div class="source-outline">'
            '<div class="source-outline-empty">No headings</div>'
            "</div>"
        )
    ancestors = set()
    if active is not None and active < len(headings):
        next_level = headings[active].level - 1
        for heading in reversed(headings[:active]):
            if next_level < 1:
                break
            if heading.level == next_level:
                ancestors.add(heading.ordinal)
                next_level -= 1
    entries = []
    for heading in headings:
        classes = ["source-outline-level-{}".format(heading.level)]
        if heading.ordinal == active:
            classes.append("source-outline-active")
        elif heading.ordinal in ancestors:
            classes.append("source-outline-ancestor")
        args = json.dumps(
            {"token": action_token, "line": heading.line}, separators=(",", ":")
        )
        entries.append(
            '<div class="{}"><a href="{}">'
            '<span class="source-outline-marker">{}</span> {}</a></div>'.format(
                " ".join(classes),
                escape("subl:mdglance_outline_navigate {}".format(args), quote=True),
                "#" * heading.level,
                escape(heading.text or "(untitled)", quote=True),
            )
        )
    outline_class = "source-outline"
    if active is not None:
        outline_class += " source-outline-has-active"
    return '<div class="{}">{}</div>'.format(outline_class, "".join(entries))
