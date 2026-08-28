import unittest
from concurrent.futures import Future

from MarkdownGlance.preview.assets.cache import AssetCache
from MarkdownGlance.preview.assets.policy import NetworkPolicy
from MarkdownGlance.preview.assets.resolver import AssetResolver
from MarkdownGlance.preview.domain.contracts import (
    AssetKey,
    AssetKind,
    AssetStatus,
    Failed,
    FetchedAsset,
    Pending,
    Ready,
    RenderSettings,
)


class ManualExecutor:
    def __init__(self):
        self.calls = []

    def submit(self, fn, key, policy):
        future = Future()
        self.calls.append((fn, key, policy, future))
        return future

    def complete(self, index, result):
        self.calls[index][3].set_result(result)

    def fail(self, index, error):
        self.calls[index][3].set_exception(error)


class FakeFetcher:
    def fetch(self, key, policy):
        raise AssertionError("manual executor does not run fetch")


def asset(revision=0, scheme="https", size=10, width=10):
    return Ready(
        FetchedAsset(
            "data:image/png;base64,AA==", width, 10, size, 30, scheme, revision
        )
    )


class ResolverTest(unittest.TestCase):
    def setUp(self):
        self.revision = 0
        self.settings = RenderSettings()
        self.executor = ManualExecutor()
        self.available = []
        self.cache = AssetCache()
        self.resolver = AssetResolver(
            self.cache,
            FakeFetcher(),
            lambda: NetworkPolicy(self.settings, self.revision),
            self.executor,
            lambda callback: callback(),
            lambda key, waiters: self.available.append((key, waiters)),
        )
        self.key = AssetKey(AssetKind.REMOTE_IMAGE, "https://example.test/image")

    def test_concurrent_requests_deduplicate_and_wake_both_waiters(self):
        first = self.resolver.resolve([self.key], "one")
        second = self.resolver.resolve([self.key], "two")
        self.assertIsInstance(first[self.key], Pending)
        self.assertIsInstance(second[self.key], Pending)
        self.assertEqual(len(self.executor.calls), 1)
        self.executor.complete(0, asset())
        self.assertEqual(self.available, [(self.key, {"one", "two"})])
        self.assertIsInstance(
            self.resolver.resolve([self.key], "three")[self.key], Ready
        )

    def test_forgotten_waiter_is_not_woken(self):
        self.resolver.resolve([self.key], "forgotten")
        self.resolver.forget_session("forgotten")
        self.executor.complete(0, asset())
        self.assertEqual(self.available, [])
        self.assertIsNotNone(self.cache.get(self.key))

    def test_permitting_policy_change_during_fetch_resubmits(self):
        self.resolver.resolve([self.key], "one")
        self.revision = 1
        self.executor.complete(0, asset(revision=0))
        self.assertEqual(len(self.executor.calls), 2)
        self.assertEqual(self.available, [])
        self.executor.complete(1, asset(revision=1))
        self.assertEqual(self.available, [(self.key, {"one"})])

    def test_blocking_policy_change_during_fetch_wakes_once(self):
        self.resolver.resolve([self.key], "one")
        self.settings = RenderSettings(allow_insecure_remote_images=False)
        self.revision = 1
        self.executor.complete(0, asset(revision=0, scheme="http"))
        self.assertEqual(self.available, [(self.key, {"one"})])
        entry = self.cache.get(self.key)
        self.assertIsInstance(entry.result, Failed)
        self.assertEqual(entry.result.status, AssetStatus.BLOCKED)

    def test_tightened_limit_reclassifies_cache_without_fetch(self):
        self.cache.put(self.key, asset(size=100), 0)
        self.settings = RenderSettings(remote_max_bytes=50)
        self.revision = 1
        result = self.resolver.resolve([self.key], "one")[self.key]
        self.assertIsInstance(result, Failed)
        self.assertEqual(result.status, AssetStatus.TOO_LARGE)
        self.assertEqual(len(self.executor.calls), 0)

    def test_unexpected_fetch_exception_becomes_unavailable(self):
        self.resolver.resolve([self.key], "one")
        self.executor.fail(0, RuntimeError("secret fetch failure"))
        self.assertEqual(self.available, [(self.key, {"one"})])
        entry = self.cache.get(self.key)
        self.assertIsInstance(entry.result, Failed)
        self.assertEqual(entry.result.status, AssetStatus.UNAVAILABLE)
