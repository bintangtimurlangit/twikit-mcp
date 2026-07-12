"""Helpers to turn twikit's rich objects into plain JSON-friendly dicts.

MCP tools must return serializable data, whereas twikit returns ``User`` /
``Tweet`` / ``Trend`` / ``Message`` objects. We deliberately project a compact,
stable subset of fields so the model gets useful, low-noise context instead of
the full raw API payload.
"""
from __future__ import annotations

from typing import Any


def _get(obj: Any, name: str, default: Any = None) -> Any:
    # twikit exposes many fields as properties that index into a raw ``_legacy``
    # dict and raise KeyError when X omits the field (see issue #417). Treat any
    # such failure as "field not present" so serialization never blows up.
    try:
        value = getattr(obj, name, default)
    except Exception:
        return default
    return value


def user_to_dict(user: Any) -> dict:
    if user is None:
        return None
    return {
        'id': _get(user, 'id'),
        'screen_name': _get(user, 'screen_name'),
        'name': _get(user, 'name'),
        'description': _get(user, 'description'),
        'location': _get(user, 'location'),
        'url': _get(user, 'url'),
        'verified': _get(user, 'verified'),
        'is_blue_verified': _get(user, 'is_blue_verified'),
        'protected': _get(user, 'protected'),
        'followers_count': _get(user, 'followers_count'),
        'following_count': _get(user, 'following_count'),
        'statuses_count': _get(user, 'statuses_count'),
        'media_count': _get(user, 'media_count'),
        'favourites_count': _get(user, 'favourites_count'),
        'listed_count': _get(user, 'listed_count'),
        'created_at': _get(user, 'created_at'),
        'profile_image_url': _get(user, 'profile_image_url'),
        'profile_banner_url': _get(user, 'profile_banner_url'),
        'pinned_tweet_ids': _get(user, 'pinned_tweet_ids'),
        'can_dm': _get(user, 'can_dm'),
    }


def _media_to_dict(media: Any) -> dict:
    return {
        'id': _get(media, 'id'),
        'type': _get(media, 'type'),
        'url': _get(media, 'url') or _get(media, 'media_url'),
        'display_url': _get(media, 'display_url'),
    }


def tweet_to_dict(tweet: Any, *, include_user: bool = True) -> dict:
    if tweet is None:
        return None
    media = _get(tweet, 'media') or []
    data = {
        'id': _get(tweet, 'id'),
        'text': _get(tweet, 'text'),
        'created_at': _get(tweet, 'created_at'),
        'lang': _get(tweet, 'lang'),
        'in_reply_to': _get(tweet, 'in_reply_to'),
        'is_quote_status': _get(tweet, 'is_quote_status'),
        'favorite_count': _get(tweet, 'favorite_count'),
        'retweet_count': _get(tweet, 'retweet_count'),
        'reply_count': _get(tweet, 'reply_count'),
        'quote_count': _get(tweet, 'quote_count'),
        'view_count': _get(tweet, 'view_count'),
        'bookmark_count': _get(tweet, 'bookmark_count'),
        'possibly_sensitive': _get(tweet, 'possibly_sensitive'),
        'hashtags': _get(tweet, 'hashtags'),
        'urls': _get(tweet, 'urls'),
        'media': [_media_to_dict(m) for m in media] if media else [],
    }
    if include_user:
        data['user'] = user_to_dict(_get(tweet, 'user'))
    quote = _get(tweet, 'quote')
    if quote is not None:
        data['quoted_tweet'] = tweet_to_dict(quote, include_user=include_user)
    return data


def trend_to_dict(trend: Any) -> dict:
    return {
        'name': _get(trend, 'name'),
        'tweets_count': _get(trend, 'tweets_count'),
        'domain_context': _get(trend, 'domain_context'),
        'grouped_trends': _get(trend, 'grouped_trends'),
    }


def message_to_dict(message: Any) -> dict:
    if message is None:
        return None
    return {
        'id': _get(message, 'id'),
        'text': _get(message, 'text'),
        'time': _get(message, 'time'),
        'sender_id': _get(message, 'sender_id'),
        'recipient_id': _get(message, 'recipient_id'),
        'attachment': _get(message, 'attachment'),
    }


def paginated(items_serializer, result: Any) -> dict:
    """Serialize a twikit ``Result[...]`` into ``{items, next_cursor}``.

    ``next_cursor`` can be passed back into the same tool to fetch the next page.
    """
    items = [items_serializer(item) for item in result]
    return {
        'items': items,
        'count': len(items),
        'next_cursor': getattr(result, 'next_cursor', None),
    }
