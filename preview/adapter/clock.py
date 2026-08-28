from typing import Callable, Dict

import sublime


class SublimeClock:
    def __init__(self) -> None:
        self._next = 0
        self._active: Dict[int, bool] = {}
        self._once_pending = set()

    def call_later(self, delay_ms: int, callback: Callable[[], None]):
        self._next += 1
        handle = self._next
        self._active[handle] = True

        def run() -> None:
            if self._active.pop(handle, False):
                callback()

        sublime.set_timeout(run, delay_ms)
        return handle

    def cancel(self, handle) -> None:
        if handle is not None:
            self._active.pop(handle, None)

    def once_per_tick(self, key, callback: Callable[[], None]) -> None:
        if key in self._once_pending:
            return
        self._once_pending.add(key)

        def run() -> None:
            self._once_pending.discard(key)
            callback()

        sublime.set_timeout(run, 0)
