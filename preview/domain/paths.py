"""Host path handling behind a swappable flavour."""

import os.path
from typing import Any


class PathFlavour:
    def __init__(self, module: Any = os.path) -> None:
        self.module = module

    def expand(self, source: str) -> str:
        return self.module.expanduser(source)

    def is_absolute(self, path: str) -> bool:
        return self.module.isabs(path)

    def normalise(self, path: str) -> str:
        return self.module.realpath(path)

    # Expansion precedes the join: a tilde only starts a path of its own.
    def resolve(self, base_path: str, source: str) -> str:
        return self.module.realpath(self.module.join(base_path, self.expand(source)))


HOST = PathFlavour()
