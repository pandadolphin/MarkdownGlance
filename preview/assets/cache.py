import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, Optional

from ..domain.contracts import AssetKey, AssetResult, Failed, Ready


@dataclass(frozen=True)
class CacheEntry:
    result: AssetResult
    stored_at: float
    policy_revision: int


class AssetCache:
    def __init__(
        self,
        max_bytes: int = 64 * 1024 * 1024,
        negative_ttl_s: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.max_bytes = max_bytes
        self.negative_ttl_s = negative_ttl_s
        self._clock = clock
        self._entries = OrderedDict()
        self._cost = 0

    def _entry_cost(self, entry: CacheEntry) -> int:
        return (
            entry.result.asset.cache_cost_bytes
            if isinstance(entry.result, Ready)
            else 0
        )

    def get(self, key: AssetKey) -> Optional[CacheEntry]:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if (
            isinstance(entry.result, Failed)
            and self._clock() - entry.stored_at >= self.negative_ttl_s
        ):
            self.pop(key)
            return None
        self._entries.move_to_end(key)
        return entry

    def put(self, key: AssetKey, result: AssetResult, policy_revision: int) -> None:
        self.pop(key)
        entry = CacheEntry(result, self._clock(), policy_revision)
        self._entries[key] = entry
        self._cost += self._entry_cost(entry)
        while self._cost > self.max_bytes and self._entries:
            _, evicted = self._entries.popitem(last=False)
            self._cost -= self._entry_cost(evicted)

    def pop(self, key: AssetKey) -> Optional[CacheEntry]:
        entry = self._entries.pop(key, None)
        if entry is not None:
            self._cost -= self._entry_cost(entry)
        return entry

    @property
    def cost_bytes(self) -> int:
        return self._cost

    def __len__(self) -> int:
        return len(self._entries)
