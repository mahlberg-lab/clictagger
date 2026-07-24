import re
import unittest

from clictagger.region.changes import tagger_changes
from clictagger.taggedtext import TaggedText


def _body_html(tt, **markup_kwargs):
    """Return just the region markup, without <style>/<script>/legend chrome."""
    html = tt.markup(**markup_kwargs)._repr_html_()
    html = re.sub(r"<style>.*?</style>", "", html, flags=re.DOTALL)
    html = re.sub(r"<script>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r'<ul class="legend">.*?</ul>', "", html, flags=re.DOTALL)
    return html


class TestZeroWidthRegionMarkup(unittest.TestCase):
    maxDiff = None

    def test_deleted_paragraph_emits_empty_span(self):
        # A removed paragraph produces a zero-width changes.changed region;
        # markup must emit an empty <span> so the :empty CSS rule can render a marker.
        previous = "First paragraph.\n\nBrand new paragraph.\n\nThird paragraph."
        current = "First paragraph.\n\nThird paragraph."
        tt = TaggedText(current)
        tagger_changes(tt.regions, tt.content, previous)
        self.assertEqual(tt.regions["changes.changed"], [(18, 18)])

        body = _body_html(tt, highlight=["changes.changed"])
        # Find every empty span that mentions changes-changed
        empty_spans = re.findall(
            r'<span[^>]*class="[^"]*changes-changed[^"]*"[^>]*></span>', body
        )
        self.assertEqual(len(empty_spans), 1, body)

        empty_span = empty_spans[0]
        # The empty span carries the surrounding regions in both title and class
        # so hovering / styling still reflects context.
        self.assertIn("changes.changed", empty_span)
        self.assertIn("chapter.paragraph:2", empty_span)
        self.assertIn("chapter-paragraph", empty_span)

    def test_deleted_character_emits_empty_span(self):
        # A single-character deletion also produces a zero-width region.
        previous = "Second paragraph!"
        current = "Second paragraph"
        tt = TaggedText(current)
        tagger_changes(tt.regions, tt.content, previous)
        self.assertEqual(tt.regions["changes.changed"], [(16, 16)])

        body = _body_html(tt, highlight=["changes.changed"])
        self.assertRegex(
            body, r'<span[^>]*class="[^"]*changes-changed[^"]*"[^>]*></span>'
        )

    def test_non_zero_width_region_wraps_content(self):
        # A change that has content between open/close should wrap the text,
        # not emit the empty-span marker for that region.
        previous = "Second paragraph."
        current = "Second paragraph, with extra words."
        tt = TaggedText(current)
        tagger_changes(tt.regions, tt.content, previous)
        self.assertEqual(tt.regions["changes.changed"], [(16, 34)])

        body = _body_html(tt, highlight=["changes.changed"])
        # The changed text should appear wrapped in a non-empty changes-changed span
        self.assertRegex(
            body,
            r'<span[^>]*class="[^"]*changes-changed[^"]*"[^>]*>'
            r"[^<]*, with extra words[^<]*</span>",
        )
        # No empty changes-changed span should be produced for this case
        self.assertNotRegex(
            body, r'<span[^>]*class="[^"]*changes-changed[^"]*"[^>]*></span>'
        )


if __name__ == "__main__":
    unittest.main()
