import os
import os.path
import unittest
from unittest import mock

from MarkdownGlance.preview.application.ports import SurfaceHandle
from MarkdownGlance.preview.application.session_manager import SessionManager
from MarkdownGlance.preview.application.usecases import UseCases
from MarkdownGlance.preview.domain.contracts import (
    Heading,
    PreviewDocument,
    PreviewMode,
    RenderSettings,
    ThemeSnapshot,
)

# Paths that are absolute on every host, so the suite runs from any of them.
BASE = os.path.realpath(os.path.abspath(os.sep + "mdglance"))
OUTSIDE = os.path.abspath(os.sep + "mdglance-outside")
HOME = os.path.abspath(os.sep + "mdglance-home")


class Sheet:
    def __init__(self, identifier, view):
        self._id = identifier
        self._view = view

    def id(self):
        return self._id

    def view(self):
        return self._view


class View:
    def __init__(self, identifier, name="source.md", filename=None, markdown=True):
        self._id = identifier
        self._name = name
        self._filename = filename
        self.markdown = markdown
        self._sheet = Sheet(identifier + 100, self)
        self._window = None

    def buffer_id(self):
        return self._id

    def sheet(self):
        return self._sheet

    def window(self):
        return self._window

    def name(self):
        return self._name

    def file_name(self):
        return self._filename

    def match_selector(self, point, selector):
        return self.markdown


class Window:
    def __init__(self, identifier, source, folders=()):
        self._id = identifier
        self.source = source
        source._window = self
        self._active = source.sheet()
        self.opened = []
        self.focused = []
        self._folders = list(folders)

    def id(self):
        return self._id

    def active_sheet(self):
        return self._active

    def active_view(self):
        return self._active.view()

    def get_view_index(self, view):
        return (0, 0)

    def views(self):
        return [self.source]

    def focus_view(self, view):
        self._active = view.sheet()
        self.focused.append(view)

    def open_file(self, path):
        self.opened.append(path)

    def folders(self):
        return list(self._folders)


class Backend:
    def __init__(self, windows):
        self.windows = windows
        self.next_id = 1000
        self.handles = {}
        self.groups = {}
        self.roles = {}
        self.closed = []
        self.focused = []
        self.navigations = []
        self.updates = []

    def create(self, window, group, title, session_id):
        self.next_id += 1
        handle = SurfaceHandle("fake", self.next_id, window.id())
        self.handles[handle.id] = (handle, session_id)
        self.groups[handle.id] = group
        return handle

    def set_role(self, handle, role):
        self.roles[handle.id] = role

    def focus(self, handle):
        self.focused.append(handle.id)
        window = self.windows[handle.window_id]
        window._active = Sheet(handle.id, None)

    def move(self, handle, group):
        self.groups[handle.id] = group

    def reveal(self, handle):
        pass

    def update(self, handle, html):
        self.updates.append((handle.id, html))

    def set_heading_ratios(self, handle, ratios):
        pass

    def set_title(self, handle, title):
        pass

    def navigate(self, handle, slug):
        self.navigations.append((handle.id, slug))
        return True

    def is_alive(self, handle):
        return handle.id in self.handles

    def close(self, handle):
        self.closed.append(handle.id)
        self.handles.pop(handle.id, None)

    def group_of(self, handle):
        return self.groups.get(handle.id)

    def live_handles(self, window):
        return [
            item[0]
            for item in self.handles.values()
            if item[0].window_id == window.id()
        ]


class Layout:
    def __init__(self):
        self.releases = []

    def acquire(self, window, anchor, role, session_id):
        return anchor + 1

    def is_owned(self, window, group):
        return True

    def release(self, window, group, session_id, restore=True):
        self.releases.append((window.id(), group, restore))


class Scheduler:
    def __init__(self):
        self.requests = []

    def request_render(self, session_id, reason):
        self.requests.append((session_id, reason))


class Resolver:
    def forget_session(self, session_id):
        pass


class UseCasesTest(unittest.TestCase):
    def setUp(self):
        self.source = View(10, filename=os.path.join(BASE, "source.md"))
        self.window = Window(1, self.source)
        self.windows = {1: self.window}
        self.backend = Backend(self.windows)
        self.layout = Layout()
        self.scheduler = Scheduler()
        self.manager = SessionManager(
            self.backend,
            self.layout,
            Resolver(),
            lambda identifier: self.windows.get(identifier),
        )
        self.usecases = UseCases(
            self.manager,
            self.scheduler,
            self.backend,
            self.layout,
            lambda session, generation: None,
            RenderSettings,
            lambda view: ThemeSnapshot(),
            lambda view, session_id: None,
            "",
        )

    def test_open_repeat_open_and_switch_modes_keep_one_session(self):
        self.usecases.open_side_by_side(self.window)
        session = self.manager.for_source(1, 10)
        self.assertEqual(session.mode, PreviewMode.SIDE_BY_SIDE)
        self.assertEqual(len(self.manager.sessions_in(1)), 1)
        self.window._active = self.source.sheet()
        self.usecases.open_side_by_side(self.window)
        self.assertEqual(len(self.manager.sessions_in(1)), 1)
        self.window._active = Sheet(session.preview_surface.id, None)
        self.usecases.toggle_full_screen(self.window)
        self.assertEqual(session.mode, PreviewMode.FULL_SCREEN)
        self.assertNotIn(self.source.sheet().id(), self.backend.closed)

    def test_fullscreen_preview_toggle_closes_only_owned_surface(self):
        self.usecases.toggle_full_screen(self.window)
        session = self.manager.for_source(1, 10)
        preview_id = session.preview_surface.id
        self.usecases.toggle_full_screen(self.window)
        self.assertIsNone(self.manager.get(session.id))
        self.assertIn(preview_id, self.backend.closed)
        self.assertNotIn(self.source.sheet().id(), self.backend.closed)

    def test_saved_unsaved_and_zoom_paths(self):
        unsaved = View(20, name="Untitled", filename=None)
        second = Window(2, unsaved, (os.path.join(BASE, "project"),))
        self.windows[2] = second
        self.usecases.open_side_by_side(second)
        session = self.manager.for_source(2, 20)
        self.assertEqual(session.base_path, os.path.join(BASE, "project"))
        self.usecases.source_modified(unsaved)
        unsaved._filename = os.path.join(BASE, "saved.md")
        self.usecases.source_saved(unsaved)
        self.assertEqual(session.base_path, BASE)
        reasons = [
            reason for sid, reason in self.scheduler.requests if sid == session.id
        ]
        self.assertEqual(reasons, ["open", "edit", "save"])
        second._active = Sheet(session.preview_surface.id, None)
        self.usecases.adjust_zoom(second, 9.0)
        self.assertEqual(session.zoom, 3.0)
        self.assertEqual(reasons, ["open", "edit", "save"])

    def test_absolute_editor_link_is_rejected(self):
        self.usecases.open_side_by_side(self.window)
        session = self.manager.for_source(1, 10)
        session.last_document = PreviewDocument(
            1, "", (), (), (), (OUTSIDE, "~/secret")
        )
        self.window._active = Sheet(session.preview_surface.id, None)
        with mock.patch.dict(os.environ, {"HOME": HOME, "USERPROFILE": HOME}):
            for index in (0, 1):
                self.usecases.open_relative(self.window, session.action_token, index)
        self.assertEqual(self.window.opened, [])

    def test_toc_navigation_uses_action_token_not_active_sheet(self):
        self.usecases.open_side_by_side(self.window)
        first = self.manager.for_source(1, 10)
        first.last_document = PreviewDocument(
            1,
            "",
            (Heading(2, "First", "first", 0, 0.5),),
            (),
            (),
            (),
        )

        second_source = View(20, filename=os.path.join(BASE, "second.md"))
        second_source._window = self.window
        self.usecases.open_side_by_side(self.window, second_source)
        second = self.manager.for_source(1, 20)
        second.last_document = PreviewDocument(
            1,
            "",
            (Heading(2, "Second", "second", 0, 0.5),),
            (),
            (),
            (),
        )
        self.window._active = Sheet(9999, None)

        self.usecases.navigate(self.window, first.action_token, "first")

        self.assertEqual(
            self.backend.navigations, [(first.preview_surface.id, "first")]
        )

    def test_toc_navigation_rejects_slug_outside_token_session(self):
        self.usecases.open_side_by_side(self.window)
        session = self.manager.for_source(1, 10)
        session.last_document = PreviewDocument(
            1,
            "",
            (Heading(2, "First", "first", 0, 0.5),),
            (),
            (),
            (),
        )

        self.usecases.navigate(self.window, session.action_token, "missing")

        self.assertEqual(self.backend.navigations, [])


if __name__ == "__main__":
    unittest.main()
