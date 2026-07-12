# twikit-mcp

An **MCP (Model Context Protocol) server** that lets an AI assistant — Claude
Desktop, Claude Code, Cursor, or any MCP client — read and act on **Twitter / X**
through a single authenticated session. **No official X API key required.**

> ## Built on twikit
> All the real work — the actual Twitter/X client — is
> [**twikit** by **d60**](https://github.com/d60/twikit). Full credit and rights
> to the original library belong to its author. This project is only a thin MCP
> wrapper around it. ⭐ **Please star the [original repo](https://github.com/d60/twikit).**

It exposes twikit's capabilities as clean, model-friendly MCP tools.

> ⚠️ This repo **bundles a lightly patched copy of twikit** (under
> [`twikit/`](twikit/), MIT — see [`licenses/twikit-LICENSE.txt`](licenses/twikit-LICENSE.txt)),
> because the published twikit is currently broken on X (the `Couldn't get
> KEY_BYTE indices` login bug). The patch only fixes login. When upstream ships a
> fix, the bundled copy can be dropped in favour of the PyPI `twikit` package.

---

## Features

- **27 tools** covering users, tweets (read + write), timelines, trends and DMs.
- **No X API key** — authenticates as a normal account via cookies or login.
- **Built-in rate limiting**, on by default, to help avoid suspension ([configurable](#rate-limiting)).
- **One-line run** with `uvx` (no manual install), or `pip`.

| Area | Tools |
|---|---|
| Session | `whoami`, `rate_limit_status` |
| Users | `get_user`, `get_user_by_id`, `search_users`, `get_user_tweets`, `get_user_followers`, `get_user_following`, `follow_user`, `unfollow_user`, `block_user`, `mute_user` |
| Tweets (read) | `get_tweet`, `search_tweets`, `get_home_timeline`, `get_retweeters`, `get_favoriters` |
| Tweets (write) | `post_tweet`, `delete_tweet`, `like_tweet`, `unlike_tweet`, `retweet`, `undo_retweet`, `bookmark_tweet` |
| Trends | `get_trends` |
| Direct messages | `send_direct_message`, `get_dm_history` |

Paginating tools return `{ "items": [...], "count": N, "next_cursor": "..." }`;
pass `next_cursor` back in to page.

---

## Install

`twikit-mcp` is a **Python** package. The easiest way to run it is with
[`uv`](https://docs.astral.sh/uv/)'s `uvx` (the Python equivalent of `npx` —
downloads and runs in one step, nothing to install first):

```bash
uvx --from git+https://github.com/bintangtimurlangit/twikit-mcp twikit-mcp
```

Alternatives:

```bash
# pipx (isolated install)
pipx install git+https://github.com/bintangtimurlangit/twikit-mcp

# plain pip
pip install git+https://github.com/bintangtimurlangit/twikit-mcp

# from a clone (for development)
git clone https://github.com/bintangtimurlangit/twikit-mcp
cd twikit-mcp && pip install -e .
```

> **Why `git+…` and not `pip install twikit-mcp`?** It isn't published to PyPI
> yet — installing straight from GitHub is the current path. (The package is
> self-contained: twikit is bundled in, so there are no external Git
> dependencies to resolve.)

---

## Connect your MCP client

Per-client, copy-paste setup for **Claude Code, Claude Desktop, Cursor,
Windsurf, VS Code** and more is in **[INSTALL.md](INSTALL.md)**.

Using a client that isn't documented there? Point its AI at
**[llms-install.md](llms-install.md)** — a machine-readable install spec an agent
can follow to wire this server into any MCP client.

---

## Authenticate

X's automated login regularly trips a Cloudflare / "verify you're human"
challenge, so the reliable way to authenticate is to **copy two cookies from a
browser where you're already logged in to x.com**: `auth_token` and `ct0`.

**1. Grab the cookies**

1. Log in to <https://x.com> in your browser.
2. Open DevTools → **Application** (Chrome/Edge) or **Storage** (Firefox) →
   **Cookies** → `https://x.com`.
3. Copy the **Value** of `auth_token` and of `ct0`.

**2. Set them as environment variables**

| Variable | Required | Notes |
|---|---|---|
| `TWIKIT_AUTH_TOKEN` | ✅ | the `auth_token` cookie value |
| `TWIKIT_CT0` | ✅ | the `ct0` cookie value |
| `TWIKIT_LANGUAGE` | | default `en-US` |
| `TWIKIT_PROXY` | | e.g. `http://user:pass@host:port` |

> 🔐 Treat these like a password — they grant access to your account. Don't
> commit them anywhere. They rotate when you log out of that browser session, so
> refresh them if requests start failing.

See [INSTALL.md](INSTALL.md) for exactly where these go in each client's config.

### Rate limiting

To reduce the risk of rate-limit errors or account suspension, the server
throttles tool calls **by default** (token bucket, 30 calls/minute).

| Variable | Default | Notes |
|---|---|---|
| `TWIKIT_MCP_RATE_LIMIT` | `on` | Set to `off` (or `0`/`false`) to **disable** throttling entirely |
| `TWIKIT_MCP_RATE_LIMIT_PER_MINUTE` | `30` | Max tool calls per minute |

Call the `rate_limit_status` tool to see the active configuration.

---

## Run manually

```bash
python -m twikit_mcp      # or:  twikit-mcp
```

You normally won't run it by hand — your MCP client launches it. See
[INSTALL.md](INSTALL.md) for client setup.

---

## Responsible use

Automating X may violate its Terms of Service and can get accounts rate-limited
or suspended. Use a purpose-made account, keep volume low, and respect
[twikit's rate-limit notes](https://github.com/d60/twikit/blob/main/ratelimits.md).
Don't use this for spam, harassment, or mass automation.

---

## Contributing

Contributions welcome! This project uses
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for
commits, PR titles and issue titles — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Credits

- [**twikit**](https://github.com/d60/twikit) by **d60** — the underlying X
  client that does all the heavy lifting (MIT). A patched copy is bundled here
  under [`twikit/`](twikit/); its license is preserved at
  [`licenses/twikit-LICENSE.txt`](licenses/twikit-LICENSE.txt). ⭐ Please star the
  [original repo](https://github.com/d60/twikit).
- This project (`twikit-mcp`) is MIT-licensed. See [`LICENSE`](LICENSE).
