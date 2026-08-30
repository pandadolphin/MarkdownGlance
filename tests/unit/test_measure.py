import unittest

from MarkdownGlance.preview.domain.contracts import Heading, SourceHeading
from MarkdownGlance.preview.renderer.measure import (
    mono_columns,
    outline_width_px,
    sans_width_em,
    toc_width_px,
)

REM = 16


def headings(*items):
    return [
        Heading(level, text, "s{}".format(index), index, 0.0)
        for index, (level, text) in enumerate(items)
    ]


def source_headings(*items):
    return [
        SourceHeading(level, text, index, index)
        for index, (level, text) in enumerate(items)
    ]


class SansWidthTest(unittest.TestCase):
    def test_estimate_stays_within_a_tenth_of_the_real_advance(self):
        # Summed from the font metrics of the stacks in `preview.css`, in em at
        # 1rem: the wider of Ubuntu and Arial, which agree to within a percent.
        for text, real in (
            ("One Sublime Text default changes", 15.31),
            ("Network and privacy", 9.19),
        ):
            estimate = sans_width_em(text)
            self.assertGreaterEqual(estimate, real, text)
            self.assertLess(estimate, real * 1.1, text)

    def test_wide_characters_are_one_em_each(self):
        self.assertEqual(sans_width_em("目录"), 2.0)

    def test_empty_text_has_no_width(self):
        self.assertEqual(sans_width_em(""), 0.0)

    def test_mono_columns_count_cjk_twice(self):
        self.assertEqual(mono_columns("ab"), 2)
        self.assertEqual(mono_columns("目录"), 4)


class TocWidthTest(unittest.TestCase):
    def test_width_follows_the_longest_entry_not_the_count(self):
        one = toc_width_px(headings((1, "Features")), REM)
        many = toc_width_px(
            headings((1, "Features"), (1, "Tables"), (1, "License")), REM
        )
        self.assertEqual(one, many)
        self.assertLess(one, toc_width_px(headings((1, "Features and more")), REM))

    def test_a_deeper_heading_pays_for_its_indent(self):
        self.assertGreater(
            toc_width_px(headings((3, "Manually")), REM),
            toc_width_px(headings((1, "Manually")), REM),
        )

    def test_nothing_to_measure_asks_for_nothing(self):
        self.assertEqual(toc_width_px([], REM), 0.0)
        self.assertEqual(toc_width_px(headings((1, "Features")), 0), 0.0)

    def test_zoom_scales_the_width(self):
        entries = headings((2, "Network and privacy"))
        self.assertAlmostEqual(toc_width_px(entries, 32), toc_width_px(entries, 16) * 2)


class OutlineWidthTest(unittest.TestCase):
    def test_the_marker_and_the_indent_are_counted(self):
        deep = outline_width_px(source_headings((3, "Manually")), REM)
        shallow = outline_width_px(source_headings((1, "Manually")), REM)
        # Two levels of indent (2.3rem) and two more `#` in the marker.
        self.assertAlmostEqual(deep - shallow, 2.3 * REM + 2 * 10)

    def test_an_untitled_heading_is_measured_by_its_placeholder(self):
        self.assertEqual(
            outline_width_px(source_headings((1, "")), REM),
            outline_width_px(source_headings((1, "(untitled)")), REM),
        )

    def test_no_headings_asks_for_nothing(self):
        self.assertEqual(outline_width_px([], REM), 0.0)
