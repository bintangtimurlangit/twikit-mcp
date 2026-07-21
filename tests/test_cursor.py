"""
Pagination cursor extraction tests for the vendored twikit fork.

X changed the shape of ``TimelineTimelineCursor`` entries: the cursor moved from
``content.itemContent.value`` to ``content.value``. The old code indexed the
former unconditionally and raised ``KeyError: 'itemContent'`` on the new payloads
(most visibly in ``get_tweet_by_id`` on long-form posts).

``Client._extract_cursor_value`` reads both shapes. These tests pin that
behaviour so a future refactor can't quietly reintroduce the KeyError.
"""

import pytest

from twikit.client.client import Client

# _extract_cursor_value doesn't touch `self`; call it unbound to avoid
# constructing a Client (which would need auth cookies).
extract = Client._extract_cursor_value


def test_reads_old_cursor_shape():
    entry = {"entryId": "cursor-bottom-0", "content": {"itemContent": {"value": "OLD"}}}
    assert extract(None, entry) == "OLD"


def test_reads_new_cursor_shape():
    entry = {"entryId": "cursor-bottom-0", "content": {"value": "NEW"}}
    assert extract(None, entry) == "NEW"


def test_old_shape_wins_when_both_present():
    entry = {
        "entryId": "cursor-bottom-0",
        "content": {"itemContent": {"value": "OLD"}, "value": "NEW"},
    }
    assert extract(None, entry) == "OLD"


@pytest.mark.parametrize(
    "item_content",
    [{}, None, {"value": ""}],
    ids=["empty-dict", "null", "empty-string-value"],
)
def test_falls_through_to_new_shape_when_old_is_unusable(item_content):
    entry = {"entryId": "cursor-bottom-0", "content": {"itemContent": item_content, "value": "NEW"}}
    assert extract(None, entry) == "NEW"


@pytest.mark.parametrize(
    "entry",
    [{"entryId": "cursor-bottom-0", "content": {"foo": "bar"}}, {"entryId": "cursor-bottom-0"}],
    ids=["unknown-shape", "no-content-key"],
)
def test_returns_none_when_no_cursor_found(entry):
    assert extract(None, entry) is None


def test_new_shape_would_have_raised_under_the_old_code():
    """Regression guard: the exact expression the fix replaced still fails."""
    entry = {"entryId": "cursor-bottom-0", "content": {"value": "NEW"}}
    with pytest.raises(KeyError, match="itemContent"):
        entry["content"]["itemContent"]["value"]
    assert extract(None, entry) == "NEW"
