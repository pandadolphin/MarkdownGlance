import base64
import io
import threading
from concurrent.futures import Executor
from typing import Callable, Dict, Iterable, Sequence, Set

from ..domain.contracts import (
    AssetKey,
    AssetKind,
    AssetResult,
    AssetStatus,
    Failed,
    FetchedAsset,
    Pending,
    Ready,
)
from ..domain.paths import HOST
from .cache import AssetCache
from .fetcher import ImageFetcher
from .images import InvalidImage, detect
from .policy import NetworkPolicy

POLICY_DERIVED = frozenset((AssetStatus.BLOCKED, AssetStatus.TOO_LARGE))


class AssetResolver:
    def __init__(
        self,
        cache: AssetCache,
        fetcher: ImageFetcher,
        policy_provider: Callable[[], NetworkPolicy],
        network_executor: Executor,
        run_on_ui: Callable[[Callable[[], None]], None],
        on_available: Callable[[AssetKey, Set[str]], None],
    ) -> None:
        self._cache = cache
        self._fetcher = fetcher
        self._policy_provider = policy_provider
        self._executor = network_executor
        self._run_on_ui = run_on_ui
        self._on_available = on_available
        self._lock = threading.RLock()
        self._inflight = {}
        self._waiters: Dict[AssetKey, Set[str]] = {}

    def _submit(self, key: AssetKey, policy: NetworkPolicy) -> None:
        future = self._executor.submit(self._fetcher.fetch, key, policy)
        self._inflight[key] = future
        future.add_done_callback(
            lambda completed, k=key, revision=policy.revision: self._run_on_ui(
                lambda: self._complete_future(k, completed, revision)
            )
        )

    def _complete_future(self, key: AssetKey, future, revision: int) -> None:
        try:
            result = future.result()
        except Exception:
            result = Failed(AssetStatus.UNAVAILABLE)
        self._complete(key, result, revision)

    def resolve(
        self, keys: Sequence[AssetKey], session_id: str
    ) -> Dict[AssetKey, AssetResult]:
        results: Dict[AssetKey, AssetResult] = {}
        local_misses = []
        policy = self._policy_provider()
        with self._lock:
            for key in keys:
                blocked = policy.evaluate_key(key)
                if blocked is not None:
                    result = Failed(blocked)
                    self._cache.put(key, result, policy.revision)
                    results[key] = result
                    continue
                entry = self._cache.get(key)
                if entry is not None:
                    if (
                        isinstance(entry.result, Failed)
                        and entry.result.status in POLICY_DERIVED
                        and entry.policy_revision != policy.revision
                    ):
                        self._cache.pop(key)
                        entry = None
                    elif isinstance(entry.result, Ready):
                        status = policy.evaluate(key, entry.result.asset)
                        if status is not None:
                            result = Failed(status)
                            self._cache.put(key, result, policy.revision)
                            results[key] = result
                            continue
                if entry is not None:
                    results[key] = entry.result
                    continue
                if key.kind == AssetKind.LOCAL_IMAGE:
                    local_misses.append(key)
                    continue
                self._waiters.setdefault(key, set()).add(session_id)
                if key not in self._inflight:
                    self._submit(key, policy)
                results[key] = Pending()

        for key in local_misses:
            result = self._read_local(key, policy)
            with self._lock:
                self._cache.put(key, result, policy.revision)
                results[key] = result
        return results

    def _read_local(self, key: AssetKey, policy: NetworkPolicy) -> AssetResult:
        settings = policy.settings
        if not HOST.is_absolute(key.locator):
            return Failed(AssetStatus.UNAVAILABLE)
        try:
            with open(key.locator, "rb") as handle:
                content = handle.read(settings.remote_max_bytes + 1)
            if len(content) > settings.remote_max_bytes:
                return Failed(AssetStatus.TOO_LARGE)
            info = detect(io.BytesIO(content))
            if (
                info.width > settings.remote_max_dimension
                or info.height > settings.remote_max_dimension
            ):
                return Failed(AssetStatus.TOO_LARGE)
            data_uri = "data:{};base64,{}".format(
                info.mime_type, base64.b64encode(content).decode("ascii")
            )
            return Ready(
                FetchedAsset(
                    data_uri,
                    info.width,
                    info.height,
                    len(content),
                    len(data_uri),
                    "file",
                    policy.revision,
                )
            )
        except (OSError, InvalidImage):
            return Failed(AssetStatus.UNAVAILABLE)

    def _complete(self, key: AssetKey, result: AssetResult, revision: int) -> None:
        wake = set()
        resubmit = False
        with self._lock:
            self._inflight.pop(key, None)
            current = self._policy_provider()
            if revision != current.revision:
                if isinstance(result, Ready):
                    status = current.evaluate(key, result.asset)
                else:
                    status = current.evaluate_key(key)
                if status is None:
                    if not self._waiters.get(key):
                        return
                    resubmit = True
                else:
                    result = Failed(status)
            if resubmit:
                self._submit(key, current)
                return
            self._cache.put(key, result, current.revision)
            wake = self._waiters.pop(key, set())
        if wake:
            self._on_available(key, wake)

    def forget_session(self, session_id: str) -> None:
        with self._lock:
            for waiters in self._waiters.values():
                waiters.discard(session_id)
