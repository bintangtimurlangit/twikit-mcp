# llms-install.md — install spec for AI agents

You are an AI assistant setting up the **twikit-mcp** server for a user in an MCP
client that this project does **not** have a hand-written guide for (e.g. Zed,
Antigravity, Cline, Roo, or any other). Follow this spec to configure it. Do not
skip the authentication step.

## What this server is

- Name: `twikit-mcp`. A Python MCP server that controls Twitter/X via the
  `twikit` library. No official X API key.
- Transport: **stdio** (the client launches the process; communication is over
  stdin/stdout).
- Source: `git+https://github.com/bintangtimurlangit/twikit-mcp`

## Launch command

Preferred (zero-install, requires [`uv`](https://docs.astral.sh/uv/)):

```
command: uvx
args:    ["--from", "git+https://github.com/bintangtimurlangit/twikit-mcp", "twikit-mcp"]
```

If `uv`/`uvx` is unavailable, install first
(`pip install git+https://github.com/bintangtimurlangit/twikit-mcp` or the pipx
equivalent) and then:

```
command: twikit-mcp   (or)   command: python   args: ["-m", "twikit_mcp"]
```

## Environment variables

Authentication is required or every tool returns an auth error. **Use the
browser-cookie method** (`TWIKIT_AUTH_TOKEN` + `TWIKIT_CT0`). Do not steer the
user toward username/password login — X's automated login almost always fails on
a Cloudflare / human-verification challenge that cannot be solved over stdio.

| Variable | Required | Purpose |
|---|---|---|
| `TWIKIT_AUTH_TOKEN` | ✅ | The `auth_token` cookie from a logged-in x.com browser session |
| `TWIKIT_CT0` | ✅ | The `ct0` cookie from the same session |
| `TWIKIT_LANGUAGE` | optional | Default `en-US` |
| `TWIKIT_PROXY` | optional | e.g. `http://user:pass@host:port` |
| `TWIKIT_MCP_RATE_LIMIT` | optional | `on` (default) / `off` |
| `TWIKIT_MCP_RATE_LIMIT_PER_MINUTE` | optional | Default `30` |

The user must obtain the two cookies themselves (you cannot):

1. Log in to https://x.com in a browser.
2. DevTools → Application/Storage → Cookies → `https://x.com`.
3. Copy the **Value** of `auth_token` and of `ct0`.

These are session secrets — never log or commit them.

## Canonical configuration (JSON)

Most clients accept some variant of this. Translate the keys to the target
client's schema.

```json
{
  "mcpServers": {
    "twikit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/bintangtimurlangit/twikit-mcp", "twikit-mcp"],
      "env": {
        "TWIKIT_AUTH_TOKEN": "<auth_token cookie>",
        "TWIKIT_CT0": "<ct0 cookie>"
      }
    }
  }
}
```

### Known schema differences to map onto

- **Standard (Claude Desktop, Cursor, Windsurf, Cline, Roo):** top-level key is
  `mcpServers`; each entry has `command`, `args`, `env`.
- **VS Code:** top-level key is `servers`; each entry also needs `"type":
  "stdio"`. File: `.vscode/mcp.json`.
- **Zed:** top-level key is `context_servers` in `settings.json`; the entry
  wraps the launch in a `command` object:
  `{"twikit": {"command": {"path": "uvx", "args": [...], "env": {...}}}}`.
- **CLI-driven (Claude Code):**
  `claude mcp add twikit --env TWIKIT_AUTH_TOKEN=<auth_token> --env TWIKIT_CT0=<ct0> -- uvx --from git+https://github.com/bintangtimurlangit/twikit-mcp twikit-mcp`

General rule: you need to express four things in the client's own format —
(1) a **stdio** server, (2) `command` = `uvx`, (3) `args` as above,
(4) the `env` map with `TWIKIT_AUTH_TOKEN` and `TWIKIT_CT0`.

## Steps for you to perform

1. Detect the client and locate its MCP config file (or CLI).
2. Ensure `uv` is installed; if not, either install it or fall back to a
   `pip`/`pipx` install and use `command: twikit-mcp`.
3. Ask the user for their `auth_token` and `ct0` cookies (guide them through the
   3 steps above) — you cannot obtain these yourself.
4. Write the server entry in the client's schema with the correct env.
5. Tell the user to restart/reload the client.

## Verify

Call the **`whoami`** tool — success returns `{ "user_id": "..." }`. Call
`rate_limit_status` to confirm throttle settings. An auth error means the
credentials/cookies env vars are missing or wrong.

## Available tools (27)

`whoami`, `rate_limit_status`, `get_user`, `get_user_by_id`, `search_users`,
`get_user_tweets`, `get_user_followers`, `get_user_following`, `follow_user`,
`unfollow_user`, `block_user`, `mute_user`, `get_tweet`, `search_tweets`,
`get_home_timeline`, `get_retweeters`, `get_favoriters`, `post_tweet`,
`delete_tweet`, `like_tweet`, `unlike_tweet`, `retweet`, `undo_retweet`,
`bookmark_tweet`, `get_trends`, `send_direct_message`, `get_dm_history`.
