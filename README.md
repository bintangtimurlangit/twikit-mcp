# twikit-x-mcp

[![PyPI](https://img.shields.io/pypi/v/twikit-x-mcp?style=flat-square)](https://pypi.org/project/twikit-x-mcp/)
[![license](https://img.shields.io/github/license/bintangtimurlangit/twikit-x-mcp?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/bintangtimurlangit/twikit-x-mcp/ci.yml?branch=main&style=flat-square)](https://github.com/bintangtimurlangit/twikit-x-mcp/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)](pyproject.toml)
[![GitHub Repo](https://img.shields.io/badge/GitHub-twikit--x--mcp-24292f?style=flat-square&logo=github)](https://github.com/bintangtimurlangit/twikit-x-mcp)

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

**Full reference:** [Documentation](./docs/README.md) · **Setup:** [INSTALL.md](INSTALL.md) · **Changelog:** [CHANGELOG.md](./CHANGELOG.md) · **Versioning & releases:** [docs/RELEASES.md](./docs/RELEASES.md)

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

### Tool annotations

Per the [MCP annotations spec](https://modelcontextprotocol.io/) — side effects at a glance. Write tools act on your **real** account.

| Tools | Read-only | Idempotent | Destructive |
|-------|:---------:|:----------:|:-----------:|
| `whoami`, `rate_limit_status`, `get_user`, `get_user_by_id`, `search_users`, `get_user_tweets`, `get_user_followers`, `get_user_following`, `get_tweet`, `search_tweets`, `get_home_timeline`, `get_retweeters`, `get_favoriters`, `get_trends`, `get_dm_history` | ✓ | ✓ | – |
| `follow_user` / `unfollow_user`, `block_user`, `mute_user`, `like_tweet` / `unlike_tweet`, `retweet` / `undo_retweet`, `bookmark_tweet` | – | ✓ | – |
| `post_tweet`, `send_direct_message` | – | – | – |
| `delete_tweet` | – | ✓ | ✓ |

---

## Install

Install and run with `uvx`:

```bash
uvx twikit-x-mcp
```

> **Note:** the Python import module is `twikit_x_mcp` (underscore), per Python
> convention. The distribution is self-contained — twikit is bundled in, so there
> are no external Git dependencies to resolve.

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
python -m twikit_x_mcp      # or:  twikit-x-mcp
```

You normally won't run it by hand — your MCP client launches it. See
[INSTALL.md](INSTALL.md) for client setup.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `Couldn't get KEY_BYTE indices` on login | The published twikit's login bug — this repo bundles a patched copy under `twikit/`, so make sure you're running this package, not a separate `twikit` install. |
| Auth errors / `401` / empty `whoami` | `TWIKIT_AUTH_TOKEN` or `TWIKIT_CT0` is missing, wrong, or expired. Re-copy both cookies from a logged-in x.com browser session. |
| Frequent rate-limit errors | Throttling is on by default (30/min). Check `rate_limit_status`; lower `TWIKIT_MCP_RATE_LIMIT_PER_MINUTE`, or slow down. Aggressive use can get an account suspended. |
| A "verify you're human" / Cloudflare challenge | Use the cookie method (above) rather than username/password login. |
| Server not found by the client | Verify the `command`/`args` (uvx/pipx/pip) and that `TWIKIT_*` env vars are in the client's `env` block — see [INSTALL.md](INSTALL.md). |

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

**Security & conduct:** [SECURITY.md](SECURITY.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

---

## Credits

- [**twikit**](https://github.com/d60/twikit) by **d60** — the underlying X
  client that does all the heavy lifting (MIT). A patched copy is bundled here
  under [`twikit/`](twikit/); its license is preserved at
  [`licenses/twikit-LICENSE.txt`](licenses/twikit-LICENSE.txt). ⭐ Please star the
  [original repo](https://github.com/d60/twikit).
- This project (`twikit-x-mcp`) is MIT-licensed. See [`LICENSE`](LICENSE).

---

## Disclaimer

This is an **unofficial** project. It is **not affiliated with, authorized, maintained, sponsored, or endorsed by X Corp. (Twitter)**.

It authenticates as your own account using session cookies and drives X through **twikit** — an unofficial client — so a tool can break when X changes its site. Automating X may violate its Terms of Service and can get accounts rate-limited or suspended.

You are responsible for using this software in compliance with [X's Terms of Service](https://x.com/en/tos) and applicable law. Use a purpose-made account, keep volume low, and don't use it for spam, harassment, or mass automation. All product names, logos, and brands are property of their respective owners.
