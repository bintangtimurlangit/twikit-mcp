"""
twikit MCP server
=================

Exposes twikit's Twitter/X capabilities as Model Context Protocol tools so an AI
assistant can read and act on X through a single authenticated session.

Authentication (via environment variables, read on first use)
-------------------------------------------------------------
Preferred — reuse a browser/exported cookie file (no password, most reliable):
    TWIKIT_COOKIES_FILE=/path/to/cookies.json

Or log in with credentials:
    TWIKIT_AUTH_INFO_1   username / email / phone   (required)
    TWIKIT_AUTH_INFO_2   secondary identifier       (optional, recommended)
    TWIKIT_PASSWORD      account password           (required)
    TWIKIT_TOTP_SECRET   2FA/TOTP secret            (optional)

Optional:
    TWIKIT_LANGUAGE      default 'en-US'
    TWIKIT_PROXY         e.g. 'http://user:pass@host:port'
    TWIKIT_COOKIES_FILE  when combined with credentials, cookies are saved here
                         after login and reused on subsequent runs.

Run:
    python -m twikit_mcp
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from twikit import Client

from .serialization import (
    message_to_dict,
    paginated,
    trend_to_dict,
    tweet_to_dict,
    user_to_dict,
)

mcp = FastMCP('twikit')

# --------------------------------------------------------------------------- #
# Lazily-initialised, shared authenticated client
# --------------------------------------------------------------------------- #
_client: Client | None = None
_client_lock = asyncio.Lock()


class AuthError(RuntimeError):
    pass


async def get_client() -> Client:
    """Return a logged-in :class:`twikit.Client`, creating it on first use.

    Serialised behind a lock so concurrent tool calls don't race the one-time
    login.
    """
    global _client
    if _client is not None:
        return _client

    async with _client_lock:
        if _client is not None:
            return _client

        language = os.environ.get('TWIKIT_LANGUAGE', 'en-US')
        proxy = os.environ.get('TWIKIT_PROXY') or None
        client = Client(language=language, proxy=proxy)

        cookies_file = os.environ.get('TWIKIT_COOKIES_FILE')
        auth_1 = os.environ.get('TWIKIT_AUTH_INFO_1')
        password = os.environ.get('TWIKIT_PASSWORD')

        if cookies_file and os.path.exists(cookies_file) and not (auth_1 and password):
            client.load_cookies(cookies_file)
        elif auth_1 and password:
            await client.login(
                auth_info_1=auth_1,
                auth_info_2=os.environ.get('TWIKIT_AUTH_INFO_2'),
                password=password,
                totp_secret=os.environ.get('TWIKIT_TOTP_SECRET'),
                cookies_file=cookies_file,
            )
        else:
            raise AuthError(
                'No credentials configured. Set TWIKIT_COOKIES_FILE, or '
                'TWIKIT_AUTH_INFO_1 + TWIKIT_PASSWORD in the environment.'
            )

        _client = client
        return _client


# --------------------------------------------------------------------------- #
# Session / account
# --------------------------------------------------------------------------- #
@mcp.tool()
async def whoami() -> dict:
    """Return the authenticated account's own user id (confirms the session works)."""
    client = await get_client()
    user_id = await client.user_id()
    return {'user_id': user_id}


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
@mcp.tool()
async def get_user(screen_name: str) -> dict:
    """Look up a user profile by @handle (screen name), e.g. "jack"."""
    client = await get_client()
    user = await client.get_user_by_screen_name(screen_name.lstrip('@'))
    return user_to_dict(user)


@mcp.tool()
async def get_user_by_id(user_id: str) -> dict:
    """Look up a user profile by their numeric user id."""
    client = await get_client()
    user = await client.get_user_by_id(user_id)
    return user_to_dict(user)


@mcp.tool()
async def search_users(query: str, count: int = 20, cursor: str | None = None) -> dict:
    """Search for user accounts matching a query. Paginated via ``cursor``."""
    client = await get_client()
    result = await client.search_user(query, count=count, cursor=cursor)
    return paginated(user_to_dict, result)


@mcp.tool()
async def get_user_tweets(
    user_id: str,
    tweet_type: Literal['Tweets', 'Replies', 'Media', 'Likes'] = 'Tweets',
    count: int = 40,
    cursor: str | None = None,
) -> dict:
    """Get a user's tweets. ``tweet_type`` selects the tab. Paginated via ``cursor``."""
    client = await get_client()
    result = await client.get_user_tweets(user_id, tweet_type, count=count, cursor=cursor)
    return paginated(tweet_to_dict, result)


@mcp.tool()
async def get_user_followers(user_id: str, count: int = 20, cursor: str | None = None) -> dict:
    """List accounts that follow the given user id. Paginated via ``cursor``."""
    client = await get_client()
    result = await client.get_user_followers(user_id, count=count, cursor=cursor)
    return paginated(user_to_dict, result)


@mcp.tool()
async def get_user_following(user_id: str, count: int = 20, cursor: str | None = None) -> dict:
    """List accounts the given user id follows. Paginated via ``cursor``."""
    client = await get_client()
    result = await client.get_user_following(user_id, count=count, cursor=cursor)
    return paginated(user_to_dict, result)


@mcp.tool()
async def follow_user(user_id: str) -> dict:
    """Follow the account with the given user id."""
    client = await get_client()
    user = await client.follow_user(user_id)
    return user_to_dict(user)


@mcp.tool()
async def unfollow_user(user_id: str) -> dict:
    """Unfollow the account with the given user id."""
    client = await get_client()
    user = await client.unfollow_user(user_id)
    return user_to_dict(user)


@mcp.tool()
async def block_user(user_id: str) -> dict:
    """Block the account with the given user id."""
    client = await get_client()
    await client.block_user(user_id)
    return {'ok': True, 'user_id': user_id, 'action': 'block'}


@mcp.tool()
async def mute_user(user_id: str) -> dict:
    """Mute the account with the given user id."""
    client = await get_client()
    await client.mute_user(user_id)
    return {'ok': True, 'user_id': user_id, 'action': 'mute'}


# --------------------------------------------------------------------------- #
# Tweets: read
# --------------------------------------------------------------------------- #
@mcp.tool()
async def get_tweet(tweet_id: str) -> dict:
    """Fetch a single tweet by its id, including engagement counts and media."""
    client = await get_client()
    tweet = await client.get_tweet_by_id(tweet_id)
    return tweet_to_dict(tweet)


@mcp.tool()
async def search_tweets(
    query: str,
    product: Literal['Top', 'Latest', 'Media'] = 'Latest',
    count: int = 20,
    cursor: str | None = None,
) -> dict:
    """Search tweets. ``product`` = Top | Latest | Media. Paginated via ``cursor``.

    Supports X search operators, e.g. 'from:nasa filter:media -is:retweet'.
    """
    client = await get_client()
    result = await client.search_tweet(query, product, count=count, cursor=cursor)
    return paginated(tweet_to_dict, result)


@mcp.tool()
async def get_home_timeline(
    kind: Literal['for_you', 'following'] = 'for_you',
    count: int = 20,
    cursor: str | None = None,
) -> dict:
    """Get the authenticated user's home timeline ('for_you' or 'following')."""
    client = await get_client()
    if kind == 'following':
        result = await client.get_latest_timeline(count=count, cursor=cursor)
    else:
        result = await client.get_timeline(count=count, cursor=cursor)
    return paginated(tweet_to_dict, result)


@mcp.tool()
async def get_retweeters(tweet_id: str, count: int = 40, cursor: str | None = None) -> dict:
    """List accounts that retweeted the given tweet. Paginated via ``cursor``."""
    client = await get_client()
    result = await client.get_retweeters(tweet_id, count=count, cursor=cursor)
    return paginated(user_to_dict, result)


@mcp.tool()
async def get_favoriters(tweet_id: str, count: int = 40, cursor: str | None = None) -> dict:
    """List accounts that liked the given tweet. Paginated via ``cursor``."""
    client = await get_client()
    result = await client.get_favoriters(tweet_id, count=count, cursor=cursor)
    return paginated(user_to_dict, result)


# --------------------------------------------------------------------------- #
# Tweets: write
# --------------------------------------------------------------------------- #
@mcp.tool()
async def post_tweet(
    text: str,
    reply_to: str | None = None,
    is_note_tweet: bool = False,
) -> dict:
    """Post a tweet. Set ``reply_to`` to a tweet id to reply. ``is_note_tweet``
    allows long-form (>280 char) posts on eligible accounts."""
    client = await get_client()
    tweet = await client.create_tweet(
        text=text, reply_to=reply_to, is_note_tweet=is_note_tweet
    )
    return tweet_to_dict(tweet)


@mcp.tool()
async def delete_tweet(tweet_id: str) -> dict:
    """Delete one of your own tweets by id."""
    client = await get_client()
    await client.delete_tweet(tweet_id)
    return {'ok': True, 'tweet_id': tweet_id, 'action': 'delete'}


@mcp.tool()
async def like_tweet(tweet_id: str) -> dict:
    """Like (favorite) a tweet by id."""
    client = await get_client()
    await client.favorite_tweet(tweet_id)
    return {'ok': True, 'tweet_id': tweet_id, 'action': 'like'}


@mcp.tool()
async def unlike_tweet(tweet_id: str) -> dict:
    """Remove your like from a tweet by id."""
    client = await get_client()
    await client.unfavorite_tweet(tweet_id)
    return {'ok': True, 'tweet_id': tweet_id, 'action': 'unlike'}


@mcp.tool()
async def retweet(tweet_id: str) -> dict:
    """Retweet a tweet by id."""
    client = await get_client()
    await client.retweet(tweet_id)
    return {'ok': True, 'tweet_id': tweet_id, 'action': 'retweet'}


@mcp.tool()
async def undo_retweet(tweet_id: str) -> dict:
    """Undo a retweet by tweet id."""
    client = await get_client()
    await client.delete_retweet(tweet_id)
    return {'ok': True, 'tweet_id': tweet_id, 'action': 'undo_retweet'}


@mcp.tool()
async def bookmark_tweet(tweet_id: str) -> dict:
    """Bookmark a tweet by id."""
    client = await get_client()
    await client.bookmark_tweet(tweet_id)
    return {'ok': True, 'tweet_id': tweet_id, 'action': 'bookmark'}


# --------------------------------------------------------------------------- #
# Trends
# --------------------------------------------------------------------------- #
@mcp.tool()
async def get_trends(
    category: Literal['trending', 'for-you', 'news', 'sports', 'entertainment'] = 'trending',
    count: int = 20,
) -> dict:
    """Get current trends for a category."""
    client = await get_client()
    trends = await client.get_trends(category, count=count)
    return {'items': [trend_to_dict(t) for t in trends], 'count': len(trends)}


# --------------------------------------------------------------------------- #
# Direct messages
# --------------------------------------------------------------------------- #
@mcp.tool()
async def send_direct_message(user_id: str, text: str, reply_to: str | None = None) -> dict:
    """Send a direct message to a user id. ``reply_to`` is an optional message id."""
    client = await get_client()
    message = await client.send_dm(user_id, text, reply_to=reply_to)
    return message_to_dict(message)


@mcp.tool()
async def get_dm_history(user_id: str, max_id: str | None = None) -> dict:
    """Get direct-message history with a user id. ``max_id`` pages older messages."""
    client = await get_client()
    result = await client.get_dm_history(user_id, max_id=max_id)
    return paginated(message_to_dict, result)


def main() -> None:
    """Entry point: run the MCP server over stdio."""
    mcp.run()


if __name__ == '__main__':
    main()
