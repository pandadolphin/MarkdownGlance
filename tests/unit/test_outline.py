import unittest

from MarkdownGlance.preview.domain.contracts import SourceHeading
from MarkdownGlance.preview.renderer.outline import (
    active_ordinal,
    build_outline,
    scan_outline,
)


class ScanOutlineTest(unittest.TestCase):
    def test_atx_levels_text_and_lines(self):
        headings = scan_outline("# One\n\ntext\n\n### Three\n")
        self.assertEqual(
            headings,
            (
                SourceHeading(1, "One", 0, 0),
                SourceHeading(3, "Three", 1, 4),
            ),
        )

    def test_closing_hashes_and_indent_are_stripped(self):
        headings = scan_outline("   ## Two ##\n")
        self.assertEqual(headings[0], SourceHeading(2, "Two", 0, 0))

    def test_hashtag_and_deep_indent_are_not_headings(self):
        self.assertEqual(scan_outline("#hashtag\n"), ())
        self.assertEqual(scan_outline("    # indented code\n"), ())
        self.assertEqual(scan_outline("####### seven\n"), ())

    def test_empty_atx_heading_keeps_its_level(self):
        self.assertEqual(scan_outline("##\n"), (SourceHeading(2, "", 0, 0),))

    def test_headings_inside_fences_are_ignored(self):
        source = "# Real\n\n```md\n# Fake\n```\n\n~~~\n## Fake\n~~~\n\n## Also real\n"
        self.assertEqual(
            [heading.text for heading in scan_outline(source)], ["Real", "Also real"]
        )

    def test_longer_closing_fence_and_info_string(self):
        source = "````python\n# not a heading\n```\nstill code\n````\n# after\n"
        self.assertEqual([item.text for item in scan_outline(source)], ["after"])

    def test_setext_headings_report_the_text_line(self):
        headings = scan_outline("Title\n=====\n\nSection\n---\n")
        self.assertEqual(
            headings,
            (
                SourceHeading(1, "Title", 0, 0),
                SourceHeading(2, "Section", 1, 3),
            ),
        )

    def test_thematic_break_after_a_blank_line_is_not_setext(self):
        self.assertEqual(scan_outline("text\n\n---\n\nmore\n"), ())

    def test_front_matter_close_is_not_a_setext_underline(self):
        source = "---\ntitle: Doc\ntags: [a]\n---\n\n# Body\n"
        self.assertEqual(scan_outline(source), (SourceHeading(1, "Body", 0, 5),))

    def test_atx_line_is_not_reread_as_setext_text(self):
        headings = scan_outline("# Title\n---\n")
        self.assertEqual(headings, (SourceHeading(1, "Title", 0, 0),))

    def test_table_delimiter_row_is_not_setext(self):
        self.assertEqual(scan_outline("| a | b |\n| --- | --- |\n"), ())


class ActiveOrdinalTest(unittest.TestCase):
    def setUp(self):
        self.headings = scan_outline("# One\n\n## Two\n\ntext\n\n# Three\n")

    def test_a_document_without_headings_has_none(self):
        self.assertIsNone(active_ordinal((), 4))

    def test_caret_takes_the_nearest_heading_above_it(self):
        self.assertEqual(active_ordinal(self.headings, 0), 0)
        self.assertEqual(active_ordinal(self.headings, 4), 1)
        self.assertEqual(active_ordinal(self.headings, 99), 2)

    def test_text_before_the_first_heading_has_no_active_entry(self):
        headings = scan_outline("preamble\n\n# One\n")
        self.assertIsNone(active_ordinal(headings, 0))


class BuildOutlineTest(unittest.TestCase):
    def setUp(self):
        self.headings = scan_outline("# One\n\n## Two\n\n### Three\n")

    def test_entries_carry_the_line_and_the_token(self):
        html = build_outline(self.headings, "tok")
        self.assertIn("mdglance_outline_navigate", html)
        self.assertIn("&quot;line&quot;:2", html)
        self.assertIn("&quot;token&quot;:&quot;tok&quot;", html)
        self.assertIn('class="source-outline-level-3"', html)

    def test_active_entry_and_its_ancestors_are_marked(self):
        html = build_outline(self.headings, "tok", 2)
        self.assertIn("source-outline-level-3 source-outline-active", html)
        self.assertIn("source-outline-level-2 source-outline-ancestor", html)
        self.assertIn("source-outline-level-1 source-outline-ancestor", html)
        self.assertIn("source-outline-has-active", html)

    def test_heading_text_is_escaped(self):
        html = build_outline(scan_outline("# <b>&\n"), "tok")
        self.assertIn("&lt;b&gt;&amp;", html)
        self.assertNotIn("<b>", html)

    def test_empty_document_says_so(self):
        self.assertIn("No headings", build_outline((), "tok"))

    def test_untitled_heading_still_reads(self):
        self.assertIn("(untitled)", build_outline(scan_outline("##\n"), "tok"))
