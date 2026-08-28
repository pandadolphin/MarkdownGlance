import json
from html import escape
from typing import Optional, Sequence

from ..domain.contracts import Heading


def toc_required(
    markdown_length: int,
    headings: Sequence[Heading],
    minimum_length: int,
    minimum_headings: int,
) -> bool:
    return markdown_length >= minimum_length and len(headings) >= minimum_headings


def build_toc(
    headings: Sequence[Heading], action_token: str, active_slug: Optional[str] = None
) -> str:
    entries = []
    active = next(
        (heading for heading in headings if heading.slug == active_slug), None
    )
    ancestor_ordinals = set()
    if active is not None:
        next_level = active.level - 1
        for heading in reversed(headings[: active.ordinal]):
            if next_level < 2:
                break
            if heading.level == next_level:
                ancestor_ordinals.add(heading.ordinal)
                next_level -= 1
    for heading in headings:
        classes = ["table-of-contents-level-{}".format(heading.level)]
        if heading.slug == active_slug:
            classes.append("table-of-contents-active")
        elif heading.ordinal in ancestor_ordinals:
            classes.append("table-of-contents-ancestor")
        args = json.dumps(
            {"token": action_token, "slug": heading.slug}, separators=(",", ":")
        )
        entries.append(
            '<div class="{}"><a href="{}">{}</a></div>'.format(
                " ".join(classes),
                escape("subl:mdglance_navigate {}".format(args), quote=True),
                escape(heading.text, quote=True),
            )
        )
    toc_class = "table-of-contents"
    if active_slug:
        toc_class += " table-of-contents-has-active"
    return '<div class="{}">{}</div>'.format(toc_class, "".join(entries))
