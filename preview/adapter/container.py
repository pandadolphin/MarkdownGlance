import json
import os.path
from functools import partial
from typing import Optional

import sublime

from ..application.outline import OutlineController
from ..application.render_pipeline import render
from ..application.scheduler import GenerationScheduler
from ..application.session import CloseCause, PreviewSession
from ..application.session_manager import SessionManager
from ..application.usecases import UseCases
from ..assets import AssetCache, AssetResolver, ImageFetcher, NetworkPolicy
from ..domain.contracts import RenderRequest
from ..domain.paths import HOST
from ..presentation.layout import LayoutOwner
from ..presentation.phantom_view import PhantomViewBackend
from ..renderer.stylesheet import root_font_px
from ..renderer.tables import budgets
from .clock import SublimeClock
from .executors import OwnedExecutors
from .settings import SettingsAdapter
from .source_access import caret_row, read_source, reveal_line
from .theme import theme_snapshot

# ST reports no view-resize event, so a maximised or dragged window is noticed
# by polling. Only a change in the table budget triggers a re-render.
VIEWPORT_POLL_MS = 500


def _window(window_id: int):
    return next(
        (window for window in sublime.windows() if window.id() == window_id), None
    )


class Container:
    def __init__(self) -> None:
        self.loaded = False
        self.backend = None
        self.layout = None
        self.manager = None
        self.outline = None
        self.scheduler = None
        self.usecases = None
        self.settings = None
        self.executors = None
        self.resolver = None
        self.clock = None
        self.policy_revision = 0
        self.recent_stages = []
        self._theme_callbacks = {}

    def build(self) -> None:
        if self.loaded:
            return
        self.clock = SublimeClock()
        self.executors = OwnedExecutors()
        self.backend = PhantomViewBackend(self.handle_link)
        self.layout = LayoutOwner()
        self.settings = SettingsAdapter(self._settings_changed)
        cache = AssetCache()
        self.resolver = AssetResolver(
            cache,
            ImageFetcher(),
            self.policy,
            self.executors.network,
            lambda callback: sublime.set_timeout(callback, 0),
            lambda key, waiters: self.scheduler.asset_available(key, waiters),
        )
        self.manager = SessionManager(
            self.backend,
            self.layout,
            self.resolver,
            _window,
            self.detach_theme,
            lambda surface_id: self.outline is not None
            and self.outline.owns_surface(surface_id),
        )
        self.scheduler = GenerationScheduler(
            self.manager.get,
            self.snapshot,
            partial(render, resolver=self.resolver),
            self.present,
            self.present_error,
            self.executors.render,
            self.clock,
            lambda callback: sublime.set_timeout(callback, 0),
        )
        base_css = sublime.load_resource(
            "Packages/MarkdownGlance/resources/preview.css"
        )
        self.outline = OutlineController(
            self.backend,
            self.layout,
            self.clock,
            _window,
            self.settings.get,
            theme_snapshot,
            read_source,
            caret_row,
            reveal_line,
            base_css,
        )
        self.usecases = UseCases(
            self.manager,
            self.scheduler,
            self.backend,
            self.layout,
            self.snapshot,
            self.settings.get,
            theme_snapshot,
            self.observe_theme,
            base_css,
        )
        self.loaded = True
        for window in sublime.windows():
            self.reconcile(window)
        self._watch_viewports()

    def reconcile(self, window) -> None:
        """Both registries sweep the same window; the outline's must run first
        so that its surfaces are still claimed when the preview sweep looks."""
        self.outline.reconcile(window)
        self.usecases.reconcile(window)

    def policy(self) -> NetworkPolicy:
        return NetworkPolicy(self.settings.get(), self.policy_revision)

    def snapshot(self, session: PreviewSession, generation: int) -> RenderRequest:
        self.record_stage("snapshot")
        window = _window(session.window_id)
        if window is None:
            raise RuntimeError("source window is gone")
        source = next(
            (
                view
                for view in window.views()
                if view.buffer_id() == session.source_buffer_id
            ),
            None,
        )
        if source is None:
            raise RuntimeError("source view is gone")
        folders = window.folders()
        session.base_path = (
            os.path.dirname(source.file_name())
            if source.file_name()
            else HOST.normalise(folders[0]) if folders else None
        )
        session.theme = theme_snapshot(source)
        session.settings = self.settings.get()
        viewport_width = self._viewport_width(session)
        session.table_budget = self._table_budget(session, viewport_width)
        return RenderRequest(
            session.id,
            generation,
            source.substr(sublime.Region(0, source.size())),
            session.base_path,
            session.zoom,
            session.settings,
            session.theme,
            session.action_token,
            viewport_width,
        )

    def _viewport_width(self, session: PreviewSession) -> float:
        handle = session.preview_surface
        if handle is None or not self.backend.is_alive(handle):
            return 0.0
        return self.backend.viewport_width(handle)

    def _table_budget(self, session: PreviewSession, viewport_width: float):
        return budgets(
            viewport_width,
            root_font_px(session.zoom),
            session.settings.table_max_columns,
        )

    def _watch_viewports(self) -> None:
        """Re-render a preview whose group has been resized under it."""
        if not self.loaded:
            return
        for session in self.manager.all_sessions():
            if session.table_budget is None:
                continue
            budget = self._table_budget(session, self._viewport_width(session))
            if budget != session.table_budget:
                session.table_budget = budget
                self.scheduler.request_render(session.id, "resize")
        sublime.set_timeout(self._watch_viewports, VIEWPORT_POLL_MS)

    def present(self, session, document) -> None:
        self.record_stage("present")
        self.usecases.present(session, document)

    def present_error(self, session, stage, message) -> None:
        self.record_stage("error:{}".format(stage.value))
        self.usecases.present_error(session, stage, message)

    def _settings_changed(self, render_required: bool, policy_changed: bool) -> None:
        if policy_changed:
            self.policy_revision += 1
        if self.usecases is not None:
            self.usecases.settings_changed(render_required, policy_changed)

    def record_stage(self, stage: str) -> None:
        self.recent_stages.append(stage)
        del self.recent_stages[:-20]

    def observe_theme(self, view, session_id: str) -> None:
        key = "mdglance.theme.{}".format(session_id)

        def changed() -> None:
            sublime.set_timeout(
                lambda: self.loaded and self.usecases.theme_changed(view), 0
            )

        view.settings().add_on_change(key, changed)
        self._theme_callbacks[session_id] = (view, key)

    def detach_theme(self, session: PreviewSession) -> None:
        callback = self._theme_callbacks.pop(session.id, None)
        if callback is not None:
            view, key = callback
            view.settings().clear_on_change(key)

    def handle_link(self, handle, href: str) -> None:
        window = _window(handle.window_id)
        if window is None or self.usecases is None:
            return
        if href.startswith("subl:"):
            command_and_args = href[len("subl:") :].split(" ", 1)
            command = command_and_args[0]
            try:
                args = (
                    json.loads(command_and_args[1])
                    if len(command_and_args) == 2
                    else {}
                )
            except (TypeError, ValueError):
                return
            if command == "mdglance_navigate":
                self.usecases.navigate(
                    window, args.get("token", ""), args.get("slug", "")
                )
            elif command == "mdglance_outline_navigate":
                self.outline.navigate(
                    window, args.get("token", ""), args.get("line", -1)
                )
            elif command == "mdglance_open_relative":
                self.usecases.open_relative(
                    window, args.get("token", ""), args.get("path", -1)
                )
            return
        if href.startswith("#"):
            self.usecases.navigate_for_surface(handle.id, href[1:])
            return
        if href.startswith(("http://", "https://")):
            sublime.run_command("open_url", {"url": href})

    def unload(self) -> None:
        if not self.loaded:
            return
        self.settings.detach()
        self.outline.close_all()
        self.manager.close_all(CloseCause.UNLOAD)
        self.executors.shutdown()
        self.loaded = False


container = Container()
