import ast
import ntpath
import os
import os.path
import pathlib
import posixpath
import unittest
from unittest import mock

from MarkdownGlance.preview.domain.contracts import (
    RenderRequest,
    RenderSettings,
    ThemeSnapshot,
)
from MarkdownGlance.preview.domain.paths import HOST, PathFlavour
from MarkdownGlance.preview.renderer import parse, structure

ROOT = pathlib.Path(__file__).parents[2] / "preview"
WINDOWS = PathFlavour(ntpath)
POSIX = PathFlavour(posixpath)
WINDOWS_HOME = {"USERPROFILE": "C:\\Users\\phil"}
POSIX_HOME = {"HOME": "/mdglance/home/phil"}


class PathFlavourTest(unittest.TestCase):
    def test_host_flavour_follows_the_interpreter_platform(self):
        self.assertIs(HOST.module, os.path)

    def test_relative_sources_join_with_native_separators(self):
        self.assertEqual(
            WINDOWS.resolve("C:\\docs", "images/a b.png"), "C:\\docs\\images\\a b.png"
        )
        self.assertEqual(
            POSIX.resolve("/mdglance/docs", "images/a b.png"),
            "/mdglance/docs/images/a b.png",
        )

    def test_parent_traversal_collapses_before_the_locator_is_used(self):
        self.assertEqual(
            WINDOWS.resolve("C:\\docs\\sub", "../images/a.png"),
            "C:\\docs\\images\\a.png",
        )
        self.assertEqual(
            POSIX.resolve("/mdglance/docs/sub", "../images/a.png"),
            "/mdglance/docs/images/a.png",
        )

    def test_rooted_source_keeps_the_windows_drive_but_replaces_a_posix_base(self):
        self.assertEqual(
            WINDOWS.resolve("C:\\docs", "/mdglance/secret"), "C:\\mdglance\\secret"
        )
        self.assertEqual(
            POSIX.resolve("/mdglance/docs", "/mdglance/secret"), "/mdglance/secret"
        )

    def test_tilde_expands_against_the_platform_home_before_the_base_join(self):
        with mock.patch.dict(os.environ, WINDOWS_HOME):
            self.assertEqual(
                WINDOWS.resolve("C:\\docs", "~/a.png"), "C:\\Users\\phil\\a.png"
            )
        with mock.patch.dict(os.environ, POSIX_HOME):
            self.assertEqual(
                POSIX.resolve("/mdglance/docs", "~/a.png"),
                "/mdglance/home/phil/a.png",
            )

    def test_an_expanded_tilde_reads_as_absolute_so_link_guards_reject_it(self):
        with mock.patch.dict(os.environ, WINDOWS_HOME):
            self.assertTrue(WINDOWS.is_absolute(WINDOWS.expand("~/a.png")))
        with mock.patch.dict(os.environ, POSIX_HOME):
            self.assertTrue(POSIX.is_absolute(POSIX.expand("~/a.png")))

    # Single-separator paths such as "\\a.png" are deliberately absent: ntpath
    # stopped calling them absolute in Python 3.13, so they answer differently
    # on the 3.8 and 3.14 legs of the matrix.
    def test_only_the_matching_flavour_calls_a_locator_absolute(self):
        self.assertTrue(WINDOWS.is_absolute("C:\\docs\\a.png"))
        self.assertFalse(POSIX.is_absolute("C:\\docs\\a.png"))
        self.assertTrue(POSIX.is_absolute("/mdglance/docs/a.png"))
        self.assertFalse(WINDOWS.is_absolute("images/a.png"))
        self.assertFalse(POSIX.is_absolute("images/a.png"))


class RendererPathTest(unittest.TestCase):
    def locator(self, flavour, base_path, source="images/a%20b.png"):
        request = RenderRequest(
            "session",
            7,
            "![x]({})".format(source),
            base_path,
            1.0,
            RenderSettings(),
            ThemeSnapshot(),
            "opaque-token",
        )
        with mock.patch.object(structure, "HOST", flavour):
            return parse(request).asset_keys[0].locator

    def test_local_image_locators_follow_the_host_flavour(self):
        self.assertEqual(self.locator(WINDOWS, "C:\\docs"), "C:\\docs\\images\\a b.png")
        self.assertEqual(
            self.locator(POSIX, "/mdglance/docs"), "/mdglance/docs/images/a b.png"
        )

    def test_tilde_image_sources_reach_the_home_directory(self):
        with mock.patch.dict(os.environ, WINDOWS_HOME):
            self.assertEqual(
                self.locator(WINDOWS, "C:\\docs", "~/a.png"),
                "C:\\Users\\phil\\a.png",
            )
        with mock.patch.dict(os.environ, POSIX_HOME):
            self.assertEqual(
                self.locator(POSIX, "/mdglance/docs", "~/a.png"),
                "/mdglance/home/phil/a.png",
            )

    def test_tilde_expands_even_without_a_base_path(self):
        with mock.patch.dict(os.environ, POSIX_HOME):
            self.assertEqual(
                self.locator(POSIX, None, "~/a.png"), "/mdglance/home/phil/a.png"
            )


class PathSeamTest(unittest.TestCase):
    GUARDED = frozenset(("expanduser", "isabs", "realpath"))

    def test_platform_sensitive_calls_stay_inside_the_paths_module(self):
        for path in ROOT.rglob("*.py"):
            if path.name == "paths.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr in self.GUARDED:
                    self.fail("{} calls {}".format(path, node.attr))
