from typing import Protocol

from ...lib.markdown2 import Markdown

MARKDOWN_EXTRAS = (
    "fenced-code-blocks",
    "highlightjs-lang",
    "cuddled-lists",
    "header-ids",
)


class MarkdownEngine(Protocol):
    def convert(self, source: str) -> str: ...


class Markdown2Engine:
    version = "2.3.9"
    extras = MARKDOWN_EXTRAS

    def __init__(self) -> None:
        self._engine = Markdown(extras=list(self.extras))

    def convert(self, source: str) -> str:
        return str(self._engine.convert(source))


DEFAULT_ENGINE = Markdown2Engine()
