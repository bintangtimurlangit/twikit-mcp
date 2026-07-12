# twikit-mcp

An **MCP (Model Context Protocol) server** that lets an AI assistant — Claude
Desktop, Claude Code, Cursor, or any MCP client — read and act on **Twitter / X**
through a single authenticated session. **No official X API key required.**

It's built on top of [**twikit**](https://github.com/d60/twikit), an
API-key-free X client for Python. This project just exposes twikit's capabilities
as clean, model-friendly MCP tools.

> ⚠️ It currently depends on a **patched fork** of twikit, because upstream
> twikit's login is broken on current X (the `Couldn't get KEY_BYTE indices`
> bug). The fix has been submitted upstream; once merged this will depend on the
> released package.

---

## Features

26 tools across:

| Area | Tools |
|---|---|
| Session | `whoami` |
| Users | `get_user`, `get_user_by_id`, `search_users`, `get_user_tweets`, `get_user_followers`, `get_user_following`, `follow_user`, `unfollow_user`, `block_user`, `mute_user` |
| Tweets (read) | `get_tweet`, `search_tweets`, `get_home_timeline`, `get_retweeters`, `get_favoriters` |
| Tweets (write) | `post_tweet`, `delete_tweet`, `like_tweet`, `unlike_tweet`, `retweet`, `undo_retweet`, `bookmark_tweet` |
| Trends | `get_trends` |
| Direct messages | `send_direct_message`, `get_dm_history` |

Paginating tools return `{ "items": [...], "count": N, "next_cursor": "..." }`;
pass `next_cursor` back in to page.

---

## Install

```bash
pip install git+https://github.com/bintangtimurlangit/twikit-mcp
```

or from a clone:

```bash
git clone https://github.com/bintangtimurlangit/twikit-mcp
cd twikit-mcp
pip install -e .
```

---

## Authenticate

The server reads credentials from environment variables on first use.

**Preferred — reuse an exported cookie file (most reliable, no password):**

```bash
export TWIKIT_COOKIES_FILE=/absolute/path/to/cookies.json
```

Generate `cookies.json` once with twikit (`client.save_cookies('cookies.json')`)
or a browser cookie exporter.

**Or log in with credentials:**

| Variable | Required | Notes |
|---|---|---|
| `TWIKIT_AUTH_INFO_1` | yes | username / email / phone |
| `TWIKIT_AUTH_INFO_2` | no | secondary identifier (recommended) |
| `TWIKIT_PASSWORD` | yes | account password |
| `TWIKIT_TOTP_SECRET` | no | 2FA / TOTP secret |
| `TWIKIT_COOKIES_FILE` | no | if set, cookies are saved here after login and reused next run |
| `TWIKIT_LANGUAGE` | no | default `en-US` |
| `TWIKIT_PROXY` | no | e.g. `http://user:pass@host:port` |

> Interactive email/2FA challenges can't be answered over stdio — prefer the
> cookie-file method for headless use.

---

## Run

```bash
python -m twikit_mcp      # or:  twikit-mcp
```

### Claude Desktop / Claude Code config

```json
{
  "mcpServers": {
    "twikit": {
      "command": "python",
      "args": ["-m", "twikit_mcp"],
      "env": {
        "TWIKIT_COOKIES_FILE": "/absolute/path/to/cookies.json"
      }
    }
  }
}
```

---

## Responsible use

Automating X may violate its Terms of Service and can get accounts rate-limited
or suspended. Use a purpose-made account, keep volume low, and respect
[twikit's rate-limit notes](https://github.com/d60/twikit/blob/main/ratelimits.md).
Don't use this for spam, harassment, or mass automation.

---

## Credits

- [**twikit**](https://github.com/d60/twikit) by **d60** — the underlying X
  client that does all the heavy lifting (MIT).
- This project (`twikit-mcp`) is MIT-licensed. See [`LICENSE`](LICENSE).
