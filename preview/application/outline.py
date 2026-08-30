"""Outline surfaces over Markdown source buffers.

An outline is deliberately *not* a `PreviewSession`: it needs no render, no
asset resolution and no generation bookkeeping, and it has to work for a file
that has never been previewed. It owns its own surfaces, keyed by source
buffer, and everything it needs from a view arrives as an injected callable so
that this layer stays free of the Sublime API.
"""

import os.path
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

from ..domain.contracts import SourceHeading, ThemeSnapshot
from ..domain.ids import new_action_token, new_session_id
from ..renderer.measure import outline_width_px
from ..renderer.outline import active_ordinal, build_outline, scan_outline
from ..renderer.stylesheet import represent, root_font_px
from .ports import GroupRole, SurfaceHandle


@dataclass
class OutlineSession:
    id: str
    window_id: int
    source_buffer_id: int
    surface: SurfaceHandle
    source_name: str
    action_token: str
    headings: Tuple[SourceHeading, ...] = ()
    active: Optional[int] = None
    zoom: float = 1.0
    layout_groups: Set[int] = field(default_factory=set)
    debounce_handle: object = None


class OutlineController:
    def __init__(
        self,
        backend,
        layout_owner,
        clock,
        window_for_id: Callable[[int], object],
        settings_provider,
        theme_provider,
        read_source: Callable[[object], str],
        caret_row: Callable[[object], int],
        reveal_line: Callable[[object, int], None],
        base_css: str,
    ) -> None:
        self.backend = backend
        self.layout_owner = layout_owner
        self.clock = clock
        self.window_for_id = window_for_id
        self.settings_provider = settings_provider
        self.theme_provider = theme_provider
        self.read_source = read_source
        self.caret_row = caret_row
        self.reveal_line = reveal_line
        self.base_css = base_css
        self._by_source: Dict[Tuple[int, int], OutlineSession] = {}
        self._by_surface: Dict[int, OutlineSession] = {}

    # -- lookup ---------------------------------------------------------

    def for_source(self, window_id: int, buffer_id: int) -> Optional[OutlineSession]:
        return self._by_source.get((window_id, buffer_id))

    def for_surface(self, surface_id: int) -> Optional[OutlineSession]:
        return self._by_surface.get(surface_id)

    def owns_surface(self, surface_id: int) -> bool:
        return surface_id in self._by_surface

    def sessions_in(self, window_id: int) -> List[OutlineSession]:
        return [
            session
            for session in self._by_source.values()
            if session.window_id == window_id
        ]

    # -- opening and closing --------------------------------------------

    def _is_markdown(self, view) -> bool:
        return bool(view and view.match_selector(0, "text.html.markdown"))

    def _source_name(self, view) -> str:
        return view.name() or os.path.basename(view.file_name() or "") or "Untitled"

    def _active_view(self, window):
        sheet = window.active_sheet() if window is not None else None
        return sheet.view() if sheet is not None else None

    def toggle(self, window, source=None) -> None:
        """Zed's toggle: open and focus, focus, then close on the third press."""
        active = self._active_view(window)
        focused = self.for_surface(active.id()) if active is not None else None
        if focused is not None:
            source = self._source_view(focused, window)
            self.close(focused, window)
            if source is not None:
                window.focus_view(source)
            return
        source = source or active
        if source is None:
            return
        existing = self.for_source(window.id(), source.buffer_id())
        if existing is not None:
            self.backend.focus(existing.surface)
            return
        if not self._is_markdown(source):
            return
        self._open(window, source)

    def _open(self, window, source) -> None:
        source_group, _ = window.get_view_index(source)
        session_id = new_session_id()
        # Scanned before the split, so the group is the right width the moment
        # it appears rather than snapping narrower on the first repaint.
        headings = scan_outline(self.read_source(source))
        group = self.layout_owner.acquire_beside(
            window,
            source_group,
            GroupRole.OUTLINE,
            session_id,
            self._width(headings, 1.0),
        )
        surface = self.backend.create(
            window, group, "Outline: {}".format(self._source_name(source)), session_id
        )
        # Before the first paint, so the empty surface never shows in a scheme
        # the source does not use.
        self.backend.apply_theme(surface, self.theme_provider(source))
        self.backend.set_role(surface, "outline")
        session = OutlineSession(
            session_id,
            window.id(),
            source.buffer_id(),
            surface,
            self._source_name(source),
            new_action_token(),
        )
        if self.layout_owner.is_owned(window, group):
            session.layout_groups.add(group)
        self._by_source[(session.window_id, session.source_buffer_id)] = session
        self._by_surface[surface.id] = session
        self.refresh(session, source)
        self.backend.focus(surface)

    def close(self, session: OutlineSession, window=None) -> None:
        self._forget(session)
        if self.backend.is_alive(session.surface):
            self.backend.close(session.surface)
        self._release(session, window)

    def _forget(self, session: OutlineSession) -> None:
        self.clock.cancel(session.debounce_handle)
        session.debounce_handle = None
        self._by_source.pop((session.window_id, session.source_buffer_id), None)
        self._by_surface.pop(session.surface.id, None)

    def _release(self, session: OutlineSession, window=None, restore=True) -> None:
        window = window or self.window_for_id(session.window_id)
        if window is None:
            return
        for group in sorted(session.layout_groups, reverse=True):
            self.layout_owner.release(window, group, session.id, restore=restore)
        session.layout_groups.clear()

    def surface_closed(self, surface_id: int) -> bool:
        """True when the closed view was an outline this controller owned."""
        session = self.for_surface(surface_id)
        if session is None:
            return False
        self._forget(session)
        self._release(session)
        return True

    def source_closed(self, view) -> None:
        window = view.window()
        session = self.for_source(window.id(), view.buffer_id()) if window else None
        if session is not None:
            self.close(session, window)

    def close_window(self, window_id: int) -> None:
        for session in self.sessions_in(window_id):
            self._forget(session)
            if self.backend.is_alive(session.surface):
                self.backend.close(session.surface)

    def close_all(self) -> None:
        for session in list(self._by_source.values()):
            self._forget(session)
            if self.backend.is_alive(session.surface):
                self.backend.close(session.surface)

    def reconcile(self, window) -> None:
        """Drop outlines whose surface the user closed behind our back."""
        live = {handle.id for handle in self.backend.live_handles(window)}
        for session in self.sessions_in(window.id()):
            if session.surface.id not in live:
                self._forget(session)
                self._release(session, window)

    def settings_changed(self) -> None:
        """Repaint every outline, which is also what re-fits its group."""
        for session in list(self._by_source.values()):
            self._present(session, self._source_view(session))

    # -- content ---------------------------------------------------------

    def refresh(self, session: OutlineSession, source) -> None:
        if source is None or not self.backend.is_alive(session.surface):
            return
        session.headings = scan_outline(self.read_source(source))
        session.active = active_ordinal(session.headings, self.caret_row(source))
        self._present(session, source)

    def refresh_source(self, view) -> None:
        """Repaint now: the source was activated, so its theme may have moved
        and its outline may be sitting behind another file's in the group."""
        window = view.window()
        session = self.for_source(window.id(), view.buffer_id()) if window else None
        if session is None:
            return
        self.refresh(session, view)
        self.backend.reveal(session.surface)

    def refresh_for_source(self, view) -> None:
        """An edit landed; repaint after the configured settle delay."""
        window = view.window()
        session = self.for_source(window.id(), view.buffer_id()) if window else None
        if session is None:
            return
        self.clock.cancel(session.debounce_handle)
        delay = max(1, self.settings_provider().update_delay_ms)
        session.debounce_handle = self.clock.call_later(
            delay, lambda: self.refresh(session, view)
        )

    def sync_caret(self, view) -> None:
        window = view.window()
        session = self.for_source(window.id(), view.buffer_id()) if window else None
        if session is None or not self.backend.is_alive(session.surface):
            return
        active = active_ordinal(session.headings, self.caret_row(view))
        if active == session.active:
            return
        session.active = active
        self._present(session, view)

    def source_renamed(self, view) -> None:
        window = view.window()
        session = self.for_source(window.id(), view.buffer_id()) if window else None
        if session is None:
            return
        name = self._source_name(view)
        if name != session.source_name:
            session.source_name = name
            self.backend.set_title(session.surface, "Outline: {}".format(name))

    def adjust_zoom(self, window, delta: float = 0.0, reset: bool = False) -> bool:
        active = self._active_view(window)
        session = self.for_surface(active.id()) if active is not None else None
        if session is None:
            return False
        session.zoom = 1.0 if reset else max(0.5, min(3.0, session.zoom + delta))
        self._present(session, self._source_view(session, window))
        return True

    def navigate(self, window, token: str, line: int) -> None:
        session = next(
            (
                candidate
                for candidate in self.sessions_in(window.id())
                if candidate.action_token == token
            ),
            None,
        )
        if session is None or not isinstance(line, int):
            return
        heading = next(
            (item for item in session.headings if item.line == line), None
        )
        if heading is None:
            return
        source = self._source_view(session, window)
        if source is None:
            return
        self.reveal_line(source, line)
        session.active = heading.ordinal
        self._present(session, source)

    def _source_view(self, session: OutlineSession, window=None):
        window = window or self.window_for_id(session.window_id)
        if window is None:
            return None
        return next(
            (
                view
                for view in window.views()
                if view.buffer_id() == session.source_buffer_id
            ),
            None,
        )

    def _width(self, headings: Tuple[SourceHeading, ...], zoom: float) -> float:
        """Pixels the outline wants, or 0.0 for the role's default share."""
        if not self.settings_provider().auto_width:
            return 0.0
        return outline_width_px(headings, root_font_px(zoom))

    def _fit(self, session: OutlineSession) -> None:
        """Give the outline's group the width its entries need.

        `LayoutOwner.fit` decides whether the move is allowed, so a divider the
        user has dragged is never moved back.
        """
        window = self.window_for_id(session.window_id)
        if window is None:
            return
        group = self.backend.group_of(session.surface)
        if group is not None:
            self.layout_owner.fit(
                window,
                group,
                GroupRole.OUTLINE,
                self._width(session.headings, session.zoom),
            )

    def _present(self, session: OutlineSession, source) -> None:
        if not self.backend.is_alive(session.surface):
            return
        html = build_outline(session.headings, session.action_token, session.active)
        theme = (
            self.theme_provider(source) if source is not None else ThemeSnapshot()
        )
        # The scheme goes on before the paint: minihtml resolves the phantom's
        # colour variables against the surface's own scheme, not the source's.
        self.backend.apply_theme(session.surface, theme)
        self.backend.update(
            session.surface,
            represent(html, theme, session.zoom, self.base_css, panel=True),
        )
        self._fit(session)
