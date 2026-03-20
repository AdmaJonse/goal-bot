"""
Unit tests for Bluesky facet parsing utilities.

These tests ensure hashtags are located correctly in byte offsets and
that facet objects produced by `parse_tags` contain the expected data.
"""

from src.output.bluesky import get_tag_indices, parse_tags


class TestBlueskyFacets:
    """
    Tests for tag index calculation and facets parsing.
    """

    def test_single_ascii_hashtag(self):
        """
        Ensure a single ASCII hashtag is located and parsed correctly.
        """
        text = "Goal by #McDavid"

        indices = get_tag_indices(text)
        assert indices == [
            (
                len("Goal by ".encode("utf-8")),
                len("Goal by #McDavid".encode("utf-8")),
            )
        ]

        facets = parse_tags(text)
        assert len(facets) == 1
        assert facets[0]["features"][0]["tag"] == "McDavid"

    def test_emoji_before_hashtag(self):
        """
        Ensure an emoji before a hashtag does not break byte indexing.
        """
        text = "🚨 GOAL 🚨 by #McDavid"

        indices = get_tag_indices(text)

        byte_start = len("🚨 GOAL 🚨 by ".encode("utf-8"))
        byte_end = len("🚨 GOAL 🚨 by #McDavid".encode("utf-8"))

        assert indices == [(byte_start, byte_end)]

    def test_accented_characters(self):
        """
        Ensure accented characters are handled when calculating byte offsets.
        """
        text = "But à Montréal par #Suzuki"

        indices = get_tag_indices(text)

        byte_start = len("But à Montréal par ".encode("utf-8"))
        byte_end = len("But à Montréal par #Suzuki".encode("utf-8"))

        assert indices == [(byte_start, byte_end)]

    def test_multiple_hashtags(self):
        """
        Verify multiple hashtags in a string produce correct byte ranges.
        """
        text = "🚨 #McDavid scores for the #Oilers"

        indices = get_tag_indices(text)

        expected = [
            (
                len("🚨 ".encode("utf-8")),
                len("🚨 #McDavid".encode("utf-8")),
            ),
            (
                len("🚨 #McDavid scores for the ".encode("utf-8")),
                len("🚨 #McDavid scores for the #Oilers".encode("utf-8")),
            ),
        ]

        assert indices == expected

    def test_duplicate_hashtags(self):
        """
        Verify duplicate hashtags are reported separately with distinct ranges.
        """
        text = "#Goal by #Goal scorer"

        indices = get_tag_indices(text)

        assert len(indices) == 2
        assert indices[0] != indices[1]

        facets = parse_tags(text)
        assert facets[0]["features"][0]["tag"] == "Goal"
        assert facets[1]["features"][0]["tag"] == "Goal"

    def test_facet_byte_ranges_map_correctly(self):
        """
        Confirm byte ranges in facet objects map back to the original hashtag.
        """
        text = "🚨 GOAL by #McDavid"

        facets = parse_tags(text)
        assert len(facets) == 1

        facet = facets[0]
        start = facet["index"]["byteStart"]
        end = facet["index"]["byteEnd"]

        extracted = (
            text.encode("utf-8")[start:end]
            .decode("utf-8")
        )

        assert extracted == "#McDavid"

    def test_get_tag_indices_single(self):
        """
        get_tag_indices returns a single range for a single hashtag.
        """
        text = "This is a #test"

        byte_start = len("This is a ".encode("utf-8"))
        byte_end = len("This is a #test".encode("utf-8"))

        expected = [(byte_start, byte_end)]
        actual = get_tag_indices(text)

        assert expected == actual

    def test_get_tag_indices_multiple(self):
        """
        get_tag_indices returns multiple ranges for multiple hashtags.
        """
        text = "#Hello world! This is a #test of #tags"

        expected = [
            (
                len("".encode("utf-8")),
                len("#Hello".encode("utf-8")),
            ),
            (
                len("#Hello world! This is a ".encode("utf-8")),
                len("#Hello world! This is a #test".encode("utf-8")),
            ),
            (
                len("#Hello world! This is a #test of ".encode("utf-8")),
                len("#Hello world! This is a #test of #tags".encode("utf-8")),
            ),
        ]

        actual = get_tag_indices(text)
        assert expected == actual

    def test_get_tag_indices_none(self):
        """
        get_tag_indices returns an empty list when no hashtags are present.
        """
        text = "This text has no tags."
        assert get_tag_indices(text) == []

    def test_parse_tags_single(self):
        """
        parse_tags returns a single facet for a single hashtag.
        """
        text = "This is a #test"

        facets = parse_tags(text)

        assert len(facets) == 1
        assert facets[0]["features"][0]["tag"] == "test"

    def test_parse_tags_multiple(self):
        """
        parse_tags returns facets for each hashtag in the input.
        """
        text = "#Hello world! This is a #test of #tags"

        facets = parse_tags(text)

        tags = [f["features"][0]["tag"] for f in facets]
        assert tags == ["Hello", "test", "tags"]

    def test_parse_tags_none(self):
        """
        parse_tags returns an empty list when no hashtags are present.
        """
        text = "This text has no tags."
        assert parse_tags(text) == []
