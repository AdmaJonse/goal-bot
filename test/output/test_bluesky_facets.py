import pytest

from src.output.bluesky import get_tag_indices, parse_tags


class TestBlueskyFacets:

    def test_single_ascii_hashtag(self):
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
        text = "🚨 GOAL 🚨 by #McDavid"

        indices = get_tag_indices(text)

        byte_start = len("🚨 GOAL 🚨 by ".encode("utf-8"))
        byte_end = len("🚨 GOAL 🚨 by #McDavid".encode("utf-8"))

        assert indices == [(byte_start, byte_end)]

    def test_accented_characters(self):
        text = "But à Montréal par #Suzuki"

        indices = get_tag_indices(text)

        byte_start = len("But à Montréal par ".encode("utf-8"))
        byte_end = len("But à Montréal par #Suzuki".encode("utf-8"))

        assert indices == [(byte_start, byte_end)]

    def test_multiple_hashtags(self):
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
        text = "#Goal by #Goal scorer"

        indices = get_tag_indices(text)

        assert len(indices) == 2
        assert indices[0] != indices[1]

        facets = parse_tags(text)
        assert facets[0]["features"][0]["tag"] == "Goal"
        assert facets[1]["features"][0]["tag"] == "Goal"

    def test_facet_byte_ranges_map_correctly(self):
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
        text = "This is a #test"

        byte_start = len("This is a ".encode("utf-8"))
        byte_end = len("This is a #test".encode("utf-8"))

        expected = [(byte_start, byte_end)]
        actual = get_tag_indices(text)

        assert expected == actual

    def test_get_tag_indices_multiple(self):
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
        text = "This text has no tags."
        assert get_tag_indices(text) == []

    def test_parse_tags_single(self):
        text = "This is a #test"

        facets = parse_tags(text)

        assert len(facets) == 1
        assert facets[0]["features"][0]["tag"] == "test"

    def test_parse_tags_multiple(self):
        text = "#Hello world! This is a #test of #tags"

        facets = parse_tags(text)

        tags = [f["features"][0]["tag"] for f in facets]
        assert tags == ["Hello", "test", "tags"]

    def test_parse_tags_none(self):
        text = "This text has no tags."
        assert parse_tags(text) == []
