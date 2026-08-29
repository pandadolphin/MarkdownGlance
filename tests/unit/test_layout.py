import copy
import unittest

from MarkdownGlance.preview.application.ports import GroupRole
from MarkdownGlance.preview.presentation.layout import (
    LayoutOwner,
    rightmost_in_row,
    split_cell,
)


class FakeWindow:
    def __init__(self, layout):
        self._layout = copy.deepcopy(layout)
        self._sheets = {}

    def id(self):
        return 1

    def layout(self):
        return copy.deepcopy(self._layout)

    def set_layout(self, layout):
        self._layout = copy.deepcopy(layout)

    def sheets_in_group(self, group):
        return self._sheets.get(group, [])


ONE = {"cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]]}


class LayoutTest(unittest.TestCase):
    def test_split_one_by_one(self):
        layout, group = split_cell(ONE, 0, 0.5)
        self.assertEqual(group, 1)
        self.assertEqual(layout["cols"], [0.0, 0.5, 1.0])
        self.assertEqual(layout["cells"], [[0, 0, 1, 1], [1, 0, 2, 1]])

    def test_split_nested_span_preserves_other_geometry(self):
        layout = {
            "cols": [0.0, 0.25, 0.5, 1.0],
            "rows": [0.0, 0.5, 1.0],
            "cells": [[0, 0, 3, 1], [0, 1, 1, 2], [1, 1, 2, 2], [2, 1, 3, 2]],
        }
        result, new_group = split_cell(layout, 0, 0.5)
        self.assertEqual(result["cells"][1:], layout["cells"][1:] + [[2, 0, 3, 1]])
        self.assertEqual(new_group, 4)

    def test_existing_coincident_boundary_is_reused(self):
        layout = {
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 0.5, 1.0],
            "cells": [[0, 0, 2, 1], [0, 1, 1, 2], [1, 1, 2, 2]],
        }
        result, _ = split_cell(layout, 0, 0.5)
        self.assertEqual(result["cols"], layout["cols"])

    def test_rightmost_in_row_walks_past_every_neighbour(self):
        layout = {
            "cols": [0.0, 0.3, 0.6, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1], [2, 0, 3, 1]],
        }
        self.assertEqual(rightmost_in_row(layout, 0), 2)
        self.assertEqual(rightmost_in_row(layout, 2), 2)
        self.assertEqual(rightmost_in_row(ONE, 0), 0)

    def test_acquire_beside_never_shares_an_existing_group(self):
        window = FakeWindow(ONE)
        owner = LayoutOwner()
        preview = owner.acquire(window, 0, GroupRole.PREVIEW, "preview")
        outline = owner.acquire_beside(window, 0, GroupRole.OUTLINE, "outline")
        self.assertNotEqual(outline, preview)
        self.assertTrue(owner.is_owned(window, outline))
        self.assertEqual(len(window.layout()["cells"]), 3)

    def test_owner_restores_only_exact_empty_layout(self):
        window = FakeWindow(ONE)
        owner = LayoutOwner()
        group = owner.acquire(window, 0, GroupRole.PREVIEW, "session")
        owner.release(window, group, "session", restore=True)
        self.assertEqual(window.layout(), ONE)

        group = owner.acquire(window, 0, GroupRole.PREVIEW, "session")
        changed = window.layout()
        changed["cols"][1] = 0.6
        window.set_layout(changed)
        owner.release(window, group, "session", restore=True)
        self.assertEqual(window.layout(), changed)
