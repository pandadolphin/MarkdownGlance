import os.path
from typing import Callable, Optional

from ..domain.contracts import (
    DiagnosticStage,
    PreviewDocument,
    PreviewMode,
    RenderSettings,
    ThemeSnapshot,
)
from ..domain.paths import HOST
from ..renderer.errors import error_card
from ..renderer.stylesheet import represent
from ..renderer.toc import build_toc, toc_required
from .ports import GroupRole
from .session import CloseCause, PreviewSession, SessionState


class UseCases:
    def __init__(
        self,
        manager,
        scheduler,
        backend,
        layout_owner,
        source_snapshot: Callable[[PreviewSession, int], object],
        settings_provider: Callable[[], RenderSettings],
        theme_provider: Callable[[object], ThemeSnapshot],
        theme_observer: Callable[[object, str], None],
        base_css: str,
    ) -> None:
        self.manager = manager
        self.scheduler = scheduler
        self.backend = backend
        self.layout_owner = layout_owner
        self.source_snapshot = source_snapshot
        self.settings_provider = settings_provider
        self.theme_provider = theme_provider
        self.theme_observer = theme_observer
        self.base_css = base_css

    def _is_markdown(self, view) -> bool:
        return bool(view and view.match_selector(0, "text.html.markdown"))

    def _source_name(self, view) -> str:
        return view.name() or os.path.basename(view.file_name() or "") or "Untitled"

    def _base_path(self, view, window) -> Optional[str]:
        if view.file_name():
            return os.path.dirname(view.file_name())
        folders = window.folders() if window is not None else []
        return HOST.normalise(folders[0]) if folders else None

    def _session_for_active(self, window) -> Optional[PreviewSession]:
        sheet = window.active_sheet()
        if sheet is not None:
            session = self.manager.for_surface(sheet.id())
            if session is not None:
                return session
            view = sheet.view()
            if view is not None:
                return self.manager.for_source(window.id(), view.buffer_id())
        return None

    def _session_for_action_token(self, window, token: str) -> Optional[PreviewSession]:
        if not token:
            return None
        return next(
            (
                session
                for session in self.manager.sessions_in(window.id())
                if session.action_token == token
            ),
            None,
        )

    def _create(self, window, source, mode: PreviewMode) -> PreviewSession:
        source_group, _ = window.get_view_index(source)
        session = self.manager.new_session(
            window.id(),
            source.buffer_id(),
            source.sheet().id(),
            source_group,
            self._source_name(source),
            mode,
        )
        session.settings = self.settings_provider()
        session.theme = self.theme_provider(source)
        self.theme_observer(source, session.id)
        session.base_path = self._base_path(source, window)
        group = source_group
        if mode == PreviewMode.SIDE_BY_SIDE:
            group = self.layout_owner.acquire(
                window, source_group, GroupRole.PREVIEW, session.id
            )
            if self.layout_owner.is_owned(window, group):
                session.layout_groups.add(group)
        session.preview_surface = self.backend.create(
            window, group, "Preview: {}".format(session.source_name), session.id
        )
        self.backend.set_role(session.preview_surface, "preview")
        self.manager.bind_surfaces(session)
        session.state = SessionState.RENDERING
        self.backend.focus(session.preview_surface)
        self.scheduler.request_render(session.id, "open")
        return session

    def open_side_by_side(self, window, source=None) -> None:
        self.reconcile(window)
        source = source or window.active_view()
        if not self._is_markdown(source):
            return
        existing = self.manager.for_source(window.id(), source.buffer_id())
        if existing is not None:
            if existing.mode != PreviewMode.SIDE_BY_SIDE:
                self.switch_mode(existing, PreviewMode.SIDE_BY_SIDE)
            elif existing.preview_surface is not None:
                self.backend.focus(existing.preview_surface)
            return
        self._create(window, source, PreviewMode.SIDE_BY_SIDE)

    def toggle_full_screen(self, window) -> None:
        self.reconcile(window)
        session = self._session_for_active(window)
        if session is None:
            source = window.active_view()
            if self._is_markdown(source):
                self._create(window, source, PreviewMode.FULL_SCREEN)
            return
        active = window.active_sheet()
        if session.mode == PreviewMode.SIDE_BY_SIDE:
            self.switch_mode(session, PreviewMode.FULL_SCREEN)
        elif (
            session.preview_surface is not None
            and active.id() == session.preview_surface.id
        ):
            source = self._find_source(session)
            self.backend.close(session.preview_surface)
            self.manager.close(session, CloseCause.PREVIEW_CLOSED_BY_USER)
            if source is not None:
                window.focus_view(source)
        elif session.preview_surface is not None:
            self.backend.focus(session.preview_surface)

    def switch_mode(self, session: PreviewSession, mode: PreviewMode) -> None:
        if session.mode == mode or session.preview_surface is None:
            return
        window = self.manager.window_for_id(session.window_id)
        if window is None:
            return
        session.state = SessionState.MOVING
        handles = [
            handle
            for handle in (session.preview_surface, session.toc_surface)
            if handle
        ]
        for handle in handles:
            self.backend.move(handle, session.source_group)
        for group in sorted(session.layout_groups, reverse=True):
            self.layout_owner.release(window, group, session.id, restore=True)
        session.layout_groups.clear()

        if mode == PreviewMode.SIDE_BY_SIDE:
            preview_group = self.layout_owner.acquire(
                window, session.source_group, GroupRole.PREVIEW, session.id
            )
            if self.layout_owner.is_owned(window, preview_group):
                session.layout_groups.add(preview_group)
            self.backend.move(session.preview_surface, preview_group)
            anchor = preview_group
        else:
            self.backend.move(session.preview_surface, session.source_group)
            anchor = session.source_group

        if session.toc_surface is not None:
            toc_group = self.layout_owner.acquire(
                window, anchor, GroupRole.TOC, session.id
            )
            if self.layout_owner.is_owned(window, toc_group):
                session.layout_groups.add(toc_group)
            self.backend.move(session.toc_surface, toc_group)
            self.backend.reveal(session.toc_surface)
        session.mode = mode
        self.backend.focus(session.preview_surface)
        session.state = (
            SessionState.VISIBLE if session.last_document else SessionState.RENDERING
        )
        self.represent(session)

    def _ensure_toc(self, session: PreviewSession) -> None:
        if session.toc_surface is not None or session.preview_surface is None:
            return
        window = self.manager.window_for_id(session.window_id)
        if window is None:
            return
        preview_group = self.backend.group_of(session.preview_surface)
        if preview_group is None:
            return
        toc_group = self.layout_owner.acquire(
            window, preview_group, GroupRole.TOC, session.id
        )
        if self.layout_owner.is_owned(window, toc_group):
            session.layout_groups.add(toc_group)
        session.toc_surface = self.backend.create(
            window, toc_group, "TOC: {}".format(session.source_name), session.id
        )
        self.backend.set_role(session.toc_surface, "toc")
        self.manager.bind_surfaces(session)
        self.backend.reveal(session.toc_surface)
        self.backend.focus(session.preview_surface)

    def present(self, session: PreviewSession, document: PreviewDocument) -> None:
        if session.preview_surface is None or not self.backend.is_alive(
            session.preview_surface
        ):
            return
        ratios = {heading.slug: heading.position_ratio for heading in document.headings}
        self.backend.set_heading_ratios(session.preview_surface, ratios)
        self.backend.update(
            session.preview_surface,
            represent(document.body_html, session.theme, session.zoom, self.base_css),
        )
        if toc_required(
            len(self.source_snapshot(session, document.generation).markdown),
            document.headings,
            session.settings.toc_minimum_length,
            session.settings.toc_minimum_headings,
        ):
            self._ensure_toc(session)
            self._present_toc(session)
        elif session.toc_surface is not None:
            handle = session.toc_surface
            self.backend.close(handle)
            self.manager.drop_toc(session)

    def _present_toc(
        self, session: PreviewSession, active_slug: Optional[str] = None
    ) -> None:
        if session.toc_surface is None or session.last_document is None:
            return
        html = build_toc(
            session.last_document.headings, session.action_token, active_slug
        )
        self.backend.update(
            session.toc_surface,
            represent(html, session.theme, session.zoom, self.base_css),
        )
        self.backend.reveal(session.toc_surface)

    def present_error(
        self, session: PreviewSession, stage: DiagnosticStage, message: str
    ) -> None:
        if session.preview_surface is None:
            return
        previous = session.last_document.body_html if session.last_document else ""
        body = "{}{}".format(error_card(stage, message), previous)
        self.backend.update(
            session.preview_surface,
            represent(body, session.theme, session.zoom, self.base_css),
        )

    def represent(self, session: PreviewSession) -> None:
        if session.last_document is not None:
            self.backend.update(
                session.preview_surface,
                represent(
                    session.last_document.body_html,
                    session.theme,
                    session.zoom,
                    self.base_css,
                ),
            )
            self._present_toc(session)

    def adjust_zoom(self, window, delta: float = 0.0, reset: bool = False) -> None:
        session = self._session_for_active(window)
        if session is None:
            return
        session.zoom = 1.0 if reset else max(0.5, min(3.0, session.zoom + delta))
        self.represent(session)

    def navigate(self, window, token: str, slug: str) -> None:
        session = self._session_for_action_token(window, token)
        if (
            session is None
            or session.preview_surface is None
            or session.last_document is None
            or not any(
                heading.slug == slug for heading in session.last_document.headings
            )
        ):
            return
        if self.backend.navigate(session.preview_surface, slug):
            self._present_toc(session, slug)

    def navigate_for_surface(self, surface_id: int, slug: str) -> None:
        session = self.manager.for_surface(surface_id)
        if (
            session is not None
            and session.preview_surface is not None
            and session.last_document is not None
            and any(heading.slug == slug for heading in session.last_document.headings)
            and self.backend.navigate(session.preview_surface, slug)
        ):
            self._present_toc(session, slug)

    def open_relative(self, window, token: str, path: int) -> None:
        session = self._session_for_action_token(window, token)
        if (
            session is None
            or session.last_document is None
            or not isinstance(path, int)
            or path < 0
            or path >= len(session.last_document.links)
        ):
            return
        target = HOST.expand(session.last_document.links[path])
        if session.base_path is None or HOST.is_absolute(target):
            return
        window.open_file(HOST.resolve(session.base_path, target))

    def source_modified(self, view) -> None:
        window = view.window()
        session = (
            self.manager.for_source(window.id(), view.buffer_id()) if window else None
        )
        if session is not None:
            self.scheduler.request_render(session.id, "edit")

    def source_saved(self, view) -> None:
        window = view.window()
        session = (
            self.manager.for_source(window.id(), view.buffer_id()) if window else None
        )
        if session is not None:
            session.base_path = self._base_path(view, window)
            session.source_name = self._source_name(view)
            if session.preview_surface:
                self.backend.set_title(
                    session.preview_surface, "Preview: {}".format(session.source_name)
                )
            self.scheduler.request_render(session.id, "save")

    def source_closed(self, view) -> None:
        window = view.window()
        session = (
            self.manager.for_source(window.id(), view.buffer_id()) if window else None
        )
        if session is not None:
            self.manager.close(session, CloseCause.SOURCE_CLOSED)

    def surface_closed(self, view) -> None:
        self.manager.surface_closed(view.id())

    def window_closed(self, window) -> None:
        self.manager.close_window(window.id())

    def reconcile(self, window) -> None:
        self.manager.reconcile(window)

    def _find_source(self, session: PreviewSession):
        window = self.manager.window_for_id(session.window_id)
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

    def settings_changed(self, render_required: bool, policy_changed: bool) -> None:
        settings = self.settings_provider()
        for session in list(self.manager._by_id.values()):
            session.settings = settings
            if render_required or policy_changed:
                self.scheduler.request_render(session.id, "settings")

    def theme_changed(self, view) -> None:
        window = view.window()
        session = (
            self.manager.for_source(window.id(), view.buffer_id()) if window else None
        )
        if session is not None:
            session.theme = self.theme_provider(view)
            self.represent(session)
