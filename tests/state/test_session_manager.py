import unittest

from MarkdownGlance.preview.application.ports import NavigationCapability, SurfaceHandle
from MarkdownGlance.preview.application.session import (
    CloseCause,
    PreviewSession,
    SessionState,
)
from MarkdownGlance.preview.application.session_manager import SessionManager
from MarkdownGlance.preview.domain.contracts import PreviewMode


class FakeBackend:
    navigation = NavigationCapability.PROGRAMMATIC

    def __init__(self):
        self.alive = set()
        self.closed = []

    def is_alive(self, handle):
        return handle.id in self.alive

    def close(self, handle):
        self.closed.append(handle.id)
        self.alive.discard(handle.id)

    def live_handles(self, window):
        return [SurfaceHandle("fake", item, window.id()) for item in self.alive]

    def group_of(self, handle):
        return 2 if handle.id == 11 else 1


class FakeLayout:
    def __init__(self):
        self.releases = []

    def release(self, window, group, session_id, restore=True):
        self.releases.append((group, restore))


class FakeResolver:
    def __init__(self):
        self.forgot = []

    def forget_session(self, session_id):
        self.forgot.append(session_id)


class FakeWindow:
    def id(self):
        return 1


def session():
    return PreviewSession(
        "s",
        1,
        2,
        3,
        SurfaceHandle("fake", 10, 1),
        SurfaceHandle("fake", 11, 1),
        PreviewMode.SIDE_BY_SIDE,
        SessionState.VISIBLE,
        requested_generation=1,
        completed_generation=1,
        successful_generation=1,
        last_document=object(),
        layout_groups={1, 2},
    )


class SessionManagerTest(unittest.TestCase):
    def setUp(self):
        self.backend = FakeBackend()
        self.backend.alive = {10, 11}
        self.layout = FakeLayout()
        self.resolver = FakeResolver()
        self.manager = SessionManager(
            self.backend, self.layout, self.resolver, lambda window_id: FakeWindow()
        )
        self.session = session()
        self.manager.add(self.session)

    def test_source_close_closes_owned_surfaces_never_source(self):
        self.manager.close(self.session, CloseCause.SOURCE_CLOSED)
        self.assertEqual(self.backend.closed, [11, 10])
        self.assertNotIn(3, self.backend.closed)
        self.assertEqual(self.layout.releases, [(2, True), (1, True)])
        self.assertEqual(self.resolver.forgot, ["s"])

    def test_preview_user_close_does_not_close_preview_again(self):
        self.backend.alive.discard(10)
        self.manager.close(self.session, CloseCause.PREVIEW_CLOSED_BY_USER)
        self.assertEqual(self.backend.closed, [11])

    def test_window_close_skips_layout_restore(self):
        self.manager.close(self.session, CloseCause.WINDOW_CLOSED)
        self.assertEqual(self.layout.releases, [(2, False), (1, False)])

    def test_toc_close_keeps_session(self):
        self.manager.surface_closed(11)
        self.assertIs(self.manager.get("s"), self.session)
        self.assertIsNone(self.session.toc_surface)

    def test_reconcile_closes_only_proven_owned_orphan(self):
        orphan = 99
        self.backend.alive.add(orphan)
        self.manager.reconcile(FakeWindow())
        self.assertIn(orphan, self.backend.closed)
