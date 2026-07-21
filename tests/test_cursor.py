"""
Pagination cursor extraction tests for the vendored twikit fork.

X changed the shape of ``TimelineTimelineCursor`` entries: the cursor moved from
``content.itemContent.value`` to ``content.value``. The old code indexed the
former unconditionally and raised ``KeyError: 'itemContent'`` on the new payloads
(most visibly in ``get_tweet_by_id`` on long-form posts).

Cursors also arrive under two different wrapper keys — ``content`` for top-level
timeline entries, ``item`` for the nested "show more replies" cursor.

``Client._extract_cursor_value`` reads every combination. These tests pin that
behaviour so a future refactor can't quietly reintroduce the KeyError.
"""

import pytest

from twikit.client.client import Client

# _extract_cursor_value doesn't touch `self`; call it unbound to avoid
# constructing a Client (which would need auth cookies).
extract = Client._extract_cursor_value


@pytest.mark.parametrize("wrapper", ["content", "item"])
def test_reads_old_cursor_shape(wrapper):
    entry = {"entryId": "cursor-bottom-0", wrapper: {"itemContent": {"value": "OLD"}}}
    assert extract(None, entry) == "OLD"


@pytest.mark.parametrize("wrapper", ["content", "item"])
def test_reads_new_cursor_shape(wrapper):
    entry = {"entryId": "cursor-bottom-0", wrapper: {"value": "NEW"}}
    assert extract(None, entry) == "NEW"


def test_reads_show_more_replies_cursor():
    """The nested reply cursor wraps under `item`, not `content`."""
    reply = {"entryId": "cursor-showmorethreads-0", "item": {"itemContent": {"value": "SR"}}}
    assert extract(None, reply) == "SR"


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
    [
        {"entryId": "cursor-bottom-0", "content": {"foo": "bar"}},
        {"entryId": "cursor-bottom-0"},
        {"entryId": "cursor-bottom-0", "content": None},
        {"entryId": "cursor-bottom-0", "content": None, "item": {"value": "NEW"}},
    ],
    ids=["unknown-shape", "no-content-key", "null-content", "null-content-with-item"],
)
def test_handles_missing_or_null_wrappers(entry):
    """A null `content` must not raise — X sends an explicit null here."""
    expected = "NEW" if entry.get("item") else None
    assert extract(None, entry) == expected


def test_new_shape_would_have_raised_under_the_old_code():
    """Regression guard: the exact expression the fix replaced still fails."""
    entry = {"entryId": "cursor-bottom-0", "content": {"value": "NEW"}}
    with pytest.raises(KeyError, match="itemContent"):
        entry["content"]["itemContent"]["value"]
    assert extract(None, entry) == "NEW"
