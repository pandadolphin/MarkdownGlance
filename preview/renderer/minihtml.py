import json
import re
from html import escape
from typing import Dict, List, Sequence, Set
from urllib.parse import urlsplit

from ..domain.contracts import (
    AssetKey,
    AssetKind,
    AssetResult,
    AssetStatus,
    Failed,
    Pending,
    PreviewDocument,
    Ready,
    RenderRequest,
)
from .errors import asset_placeholder
from .model import ElementNode, Node, StructuredDoc, TextNode

ALLOWED_TAGS = frozenset(
    (
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "a",
        "strong",
        "em",
        "b",
        "i",
        "code",
        "pre",
        "ul",
        "ol",
        "li",
        "blockquote",
        "img",
        "br",
        "hr",
        "span",
        "div",
    )
)
DROP_CONTENT_TAGS = frozenset(("script", "style", "iframe", "object", "embed"))
VOID_TAGS = frozenset(("img", "br", "hr"))
CLASS_TOKEN = re.compile(r"^[A-Za-z0-9_-]+$")


def _attr(value: str) -> str:
    return escape(value, quote=True)


def _class_value(value: str) -> str:
    return " ".join(token for token in value.split() if CLASS_TOKEN.match(token))


def _pre_text(value: str) -> str:
    pieces: List[str] = []
    for char in value:
        if char == " ":
            pieces.append('<i class="space">.</i>')
        elif char == "\n":
            pieces.append("<br />")
        else:
            pieces.append(escape(char, quote=True))
    return "".join(pieces)


def _relative_action(request: RenderRequest, index: int) -> str:
    args = json.dumps(
        {"token": request.action_token, "path": index}, separators=(",", ":")
    )
    return "subl:mdglance_open_relative {}".format(args)


def _href(
    value: str,
    heading_slugs: Set[str],
    links: Sequence[str],
    request: RenderRequest,
) -> str:
    if value.startswith("#") and value[1:] in heading_slugs:
        return ' href="{}"'.format(_attr(value))
    parsed = urlsplit(value)
    if parsed.scheme in ("http", "https"):
        return ' href="{}"'.format(_attr(value))
    if value and not parsed.scheme and not value.startswith("#"):
        try:
            index = links.index(value)
        except ValueError:
            return ' class="blocked-link"'
        return ' href="{}"'.format(_attr(_relative_action(request, index)))
    return ' class="blocked-link"'


def _serialise_image(
    node: ElementNode,
    results: Dict[AssetKey, AssetResult],
    privacy_seen: List[bool],
) -> str:
    key = node.asset_key
    result = results.get(key) if key is not None else None
    if isinstance(result, Ready):
        asset = result.asset
        attrs = [
            'src="{}"'.format(_attr(asset.data_uri)),
            'alt="{}"'.format(_attr(node.attrs.get("alt", ""))),
            'width="{}"'.format(asset.width),
            'height="{}"'.format(asset.height),
            'style="width: {:.4f}rem; height: {:.4f}rem"'.format(
                asset.width / 16.0, asset.height / 16.0
            ),
        ]
        return "<img {}>".format(" ".join(attrs))
    status = (
        AssetStatus.LOADING if isinstance(result, Pending) else AssetStatus.UNAVAILABLE
    )
    if isinstance(result, Failed):
        status = result.status
    privacy = None
    if key is not None and key.kind == AssetKind.MERMAID and not privacy_seen[0]:
        privacy_seen[0] = True
        privacy = "Diagram source is sent to {}".format(
            urlsplit(key.locator).hostname or "the configured server"
        )
    return asset_placeholder(status, privacy)


def _serialise_node(
    node: Node,
    results: Dict[AssetKey, AssetResult],
    heading_slugs: Set[str],
    links: Sequence[str],
    request: RenderRequest,
    privacy_seen: List[bool],
    in_pre: bool = False,
) -> str:
    if isinstance(node, TextNode):
        return _pre_text(node.text) if in_pre else escape(node.text, quote=True)
    if node.tag in DROP_CONTENT_TAGS:
        return ""
    if node.tag == "img":
        return _serialise_image(node, results, privacy_seen)
    body = "".join(
        _serialise_node(
            child,
            results,
            heading_slugs,
            links,
            request,
            privacy_seen,
            in_pre or node.tag == "pre",
        )
        for child in node.children
    )
    if node.tag not in ALLOWED_TAGS:
        return body

    attrs: List[str] = []
    class_value = _class_value(node.attrs.get("class", ""))
    if class_value:
        attrs.append('class="{}"'.format(_attr(class_value)))
    if node.tag in ("h1", "h2", "h3", "h4", "h5", "h6") and node.generated:
        attrs.append('id="{}"'.format(_attr(node.attrs.get("id", ""))))
    if node.tag == "a":
        attrs.append(
            _href(node.attrs.get("href", ""), heading_slugs, links, request).strip()
        )
    prefix = "<{}{}>".format(node.tag, " " + " ".join(attrs) if attrs else "")
    return (
        prefix if node.tag in VOID_TAGS else "{}{}</{}>".format(prefix, body, node.tag)
    )


def serialise(
    structured: StructuredDoc,
    results: Dict[AssetKey, AssetResult],
    request: RenderRequest,
) -> PreviewDocument:
    heading_slugs = {heading.slug for heading in structured.headings}
    privacy_seen = [False]
    body = "".join(
        _serialise_node(
            node,
            results,
            heading_slugs,
            structured.links,
            request,
            privacy_seen,
        )
        for node in structured.roots
    ).replace("<br>", "<br />")
    pending = tuple(
        key for key in structured.asset_keys if isinstance(results.get(key), Pending)
    )
    return PreviewDocument(
        request.generation,
        body,
        structured.headings,
        structured.asset_keys,
        pending,
        structured.links,
    )
