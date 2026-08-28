from typing import Callable, Dict, Optional

import sublime

from ..application.ports import NavigationCapability, SurfaceHandle

OWNER_KEY = "mdglance.session"
ROLE_KEY = "mdglance.role"
CHROME_SUPPRESSION = {
    "gutter": False,
    "line_numbers": False,
    "fold_buttons": False,
    "draw_indent_guides": False,
    "highlight_line": False,
    "caret_extra_width": 0,
    "caret_style": "solid",
    "scroll_past_end": False,
    "word_wrap": True,
    "rulers": [],
    "draw_white_space": "none",
    "is_widget": True,
}


class PhantomViewBackend:
    name = "phantom_view"
    navigation = NavigationCapability.PROGRAMMATIC

    def __init__(self, on_link: Optional[Callable[[SurfaceHandle, str], None]] = None):
        self._phantoms: Dict[int, object] = {}
        self._ratios: Dict[int, Dict[str, float]] = {}
        self._on_link_callback = on_link or (lambda handle, href: None)

    def set_link_handler(self, callback: Callable[[SurfaceHandle, str], None]) -> None:
        self._on_link_callback = callback

    def create(self, window, group: int, title: str, session_id: str) -> SurfaceHandle:
        view = window.new_file()
        window.set_view_index(view, group, len(window.views_in_group(group)))
        view.set_scratch(True)
        view.set_read_only(True)
        view.set_name(title)
        settings = view.settings()
        settings.set(OWNER_KEY, session_id)
        settings.set(ROLE_KEY, "preview")
        for key, value in CHROME_SUPPRESSION.items():
            settings.set(key, value)
        self._phantoms[view.id()] = sublime.PhantomSet(view, "mdglance")
        return SurfaceHandle(self.name, view.id(), window.id())

    def viewport_width(self, handle: SurfaceHandle) -> float:
        view = self._view(handle)
        return float(view.viewport_extent()[0]) if view is not None else 0.0

    def set_role(self, handle: SurfaceHandle, role: str) -> None:
        view = self._view(handle)
        if view is not None:
            view.settings().set(ROLE_KEY, role)

    def update(self, handle: SurfaceHandle, html: str) -> None:
        view = self._view(handle)
        phantom_set = self._phantoms.get(handle.id)
        if view is None:
            return
        if phantom_set is None:
            phantom_set = sublime.PhantomSet(view, "mdglance")
            self._phantoms[handle.id] = phantom_set
        phantom_set.update(
            [
                sublime.Phantom(
                    sublime.Region(0),
                    html,
                    sublime.LAYOUT_BLOCK,
                    lambda href: self._on_link_callback(handle, href),
                )
            ]
        )

    def set_heading_ratios(
        self, handle: SurfaceHandle, ratios: Dict[str, float]
    ) -> None:
        self._ratios[handle.id] = dict(ratios)

    def navigate(self, handle: SurfaceHandle, slug: str) -> bool:
        view = self._view(handle)
        ratio = self._ratios.get(handle.id, {}).get(slug)
        if view is None or ratio is None:
            return False
        document_height = view.layout_extent()[1]
        viewport_height = view.viewport_extent()[1]
        y = max(0.0, document_height * ratio - viewport_height * 0.1)
        view.set_viewport_position((0.0, y), True)
        return True

    def move(self, handle: SurfaceHandle, group: int) -> None:
        window, view = self._window_view(handle)
        if view is not None:
            window.set_view_index(view, group, len(window.views_in_group(group)))

    def reveal(self, handle: SurfaceHandle) -> None:
        window, view = self._window_view(handle)
        if view is None:
            return
        previous = window.active_group()
        group, _ = window.get_view_index(view)
        window.focus_group(group)
        window.focus_view(view)
        window.focus_group(previous)

    def focus(self, handle: SurfaceHandle) -> None:
        _, view = self._window_view(handle)
        if view is not None:
            view.window().focus_view(view)

    def close(self, handle: SurfaceHandle) -> None:
        view = self._view(handle)
        self._phantoms.pop(handle.id, None)
        self._ratios.pop(handle.id, None)
        if view is not None:
            view.settings().erase(OWNER_KEY)
            view.settings().erase(ROLE_KEY)
            view.close()

    def is_alive(self, handle: SurfaceHandle) -> bool:
        return self._view(handle) is not None

    def group_of(self, handle: SurfaceHandle):
        window, view = self._window_view(handle)
        return window.get_view_index(view)[0] if view is not None else None

    def set_title(self, handle: SurfaceHandle, title: str) -> None:
        view = self._view(handle)
        if view is not None:
            view.set_name(title)

    def live_handles(self, window):
        return [
            SurfaceHandle(self.name, view.id(), window.id())
            for view in window.views()
            if view.settings().has(OWNER_KEY)
        ]

    def owner_of(self, sheet_or_view):
        if sheet_or_view is None:
            return None
        view = sheet_or_view.view() if hasattr(sheet_or_view, "view") else sheet_or_view
        return view.settings().get(OWNER_KEY) if view is not None else None

    def role_of(self, sheet_or_view):
        if sheet_or_view is None:
            return None
        view = sheet_or_view.view() if hasattr(sheet_or_view, "view") else sheet_or_view
        return view.settings().get(ROLE_KEY) if view is not None else None

    def _window(self, window_id: int):
        return next(
            (window for window in sublime.windows() if window.id() == window_id), None
        )

    def _view(self, handle: SurfaceHandle):
        window = self._window(handle.window_id)
        return (
            next((view for view in window.views() if view.id() == handle.id), None)
            if window is not None
            else None
        )

    def _window_view(self, handle: SurfaceHandle):
        window = self._window(handle.window_id)
        return window, self._view(handle)
