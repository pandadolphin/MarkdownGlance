import bisect
import json
from dataclasses import dataclass
from typing import Dict, Set, Tuple

from ..application.ports import GroupRole

EPSILON = 1e-6


ROLE_SHARE = {GroupRole.PREVIEW: 0.5, GroupRole.TOC: 0.35}


@dataclass
class OwnedGroup:
    group: int
    previous_layout: dict
    fingerprint: str
    holders: Set[str]


def fingerprint(layout: dict) -> str:
    return json.dumps(layout, sort_keys=True, separators=(",", ":"))


def split_cell(layout: dict, cell_index: int, new_share: float) -> Tuple[dict, int]:
    cols = list(layout["cols"])
    rows = list(layout["rows"])
    cells = [list(cell) for cell in layout["cells"]]
    c0, r0, c1, r1 = cells[cell_index]
    x0, x1 = cols[c0], cols[c1]
    x_new = x1 - (x1 - x0) * new_share
    insertion = bisect.bisect_left(cols, x_new)
    existing = insertion < len(cols) and abs(cols[insertion] - x_new) < EPSILON
    if not existing:
        cols.insert(insertion, x_new)
        for cell in cells:
            for position in (0, 2):
                if cell[position] >= insertion:
                    cell[position] += 1
    c0_after, r0_after, c1_after, r1_after = cells[cell_index]
    if not c0_after < insertion < c1_after:
        raise ValueError("split boundary does not fall inside anchor cell")
    cells[cell_index] = [c0_after, r0_after, insertion, r1_after]
    cells.append([insertion, r0_after, c1_after, r1_after])
    return {"cols": cols, "rows": rows, "cells": cells}, len(cells) - 1


class LayoutOwner:
    def __init__(self) -> None:
        self._owned: Dict[int, Dict[int, OwnedGroup]] = {}

    def acquire(
        self, window, anchor_group: int, role: GroupRole, session_id: str
    ) -> int:
        layout = window.layout()
        anchor = layout["cells"][anchor_group]
        _, r0, c1, r1 = anchor
        right_group = next(
            (
                index
                for index, cell in enumerate(layout["cells"])
                if cell[0] == c1 and cell[1] == r0 and cell[3] == r1
            ),
            None,
        )
        owned = self._owned.setdefault(window.id(), {})
        if right_group is not None:
            if right_group in owned:
                owned[right_group].holders.add(session_id)
            return right_group
        previous = layout
        updated, new_group = split_cell(layout, anchor_group, ROLE_SHARE[role])
        window.set_layout(updated)
        owned[new_group] = OwnedGroup(
            new_group, previous, fingerprint(updated), {session_id}
        )
        return new_group

    def is_owned(self, window, group: int) -> bool:
        return group in self._owned.get(window.id(), {})

    def release(
        self, window, group: int, session_id: str, restore: bool = True
    ) -> None:
        groups = self._owned.get(window.id(), {})
        owned = groups.get(group)
        if owned is None:
            return
        owned.holders.discard(session_id)
        if owned.holders:
            return
        may_restore = (
            restore
            and not window.sheets_in_group(group)
            and fingerprint(window.layout()) == owned.fingerprint
        )
        groups.pop(group, None)
        if may_restore:
            window.set_layout(owned.previous_layout)
        if not groups:
            self._owned.pop(window.id(), None)

    def invalidate(self, window) -> None:
        self._owned.pop(window.id(), None)
