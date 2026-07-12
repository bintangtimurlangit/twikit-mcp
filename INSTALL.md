# Installing twikit-mcp in your MCP client

Copy-paste setup for the most common clients. If yours isn't here, hand your AI
assistant [`llms-install.md`](llms-install.md) and it can wire up any MCP client
from the spec.

- [Step 1 — Get your `auth_token` and `ct0` cookies](#step-1--get-your-auth_token-and-ct0-cookies)
- [Step 2 — Add the server](#step-2--add-the-server)
  - [Claude Code](#claude-code)
  - [Claude Desktop](#claude-desktop)
  - [Cursor](#cursor)
  - [Windsurf](#windsurf)
  - [VS Code (Copilot / MCP)](#vs-code-copilot--mcp)
- [Optional: rate limiting](#optional-disable-or-tune-rate-limiting)
- [Verify](#verify)

Every example runs the server with `uvx` (no manual install). Make sure
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) is installed
(`curl -LsSf https://astral.sh/uv/install.sh | sh`), or swap `uvx --from
git+… twikit-mcp` for a `pip`-installed `twikit-mcp` command.

---

## Step 1 — Get your `auth_token` and `ct0` cookies

X's automated login usually hits a Cloudflare / human-verification challenge, so
this server authenticates with two cookies taken from a browser where you're
already signed in. This is the only reliable method.

1. Log in to <https://x.com> in your browser.
2. Open **DevTools** (F12) → **Application** tab (Chrome/Edge) or **Storage**
   tab (Firefox) → **Cookies** → `https://x.com`.
3. Copy the **Value** of the cookie named **`auth_token`** and the one named
   **`ct0`**.

You'll paste these into the config below.

> 🔐 These are session secrets — anyone with them can act as your account. Keep
> them out of shared repos. They stop working when you log out of that browser
> session; re-copy them if calls start failing.

---

## Step 2 — Add the server

Replace `YOUR_AUTH_TOKEN` and `YOUR_CT0` with the values from Step 1.

### Claude Code

```bash
claude mcp add twikit \
  --env TWIKIT_AUTH_TOKEN=YOUR_AUTH_TOKEN \
  --env TWIKIT_CT0=YOUR_CT0 \
  -- uvx --from git+https://github.com/bintangtimurlangit/twikit-mcp twikit-mcp
```

Add `-s user` to make it available in every project. Check with `claude mcp
list`, remove with `claude mcp remove twikit`.

### Claude Desktop

Edit the config (Settings → Developer → Edit Config, or directly):

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "twikit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/bintangtimurlangit/twikit-mcp", "twikit-mcp"],
      "env": {
        "TWIKIT_AUTH_TOKEN": "YOUR_AUTH_TOKEN",
        "TWIKIT_CT0": "YOUR_CT0"
      }
    }
  }
}
```

Restart Claude Desktop.

### Cursor

Create `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (this project only):

```json
{
  "mcpServers": {
    "twikit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/bintangtimurlangit/twikit-mcp", "twikit-mcp"],
      "env": {
        "TWIKIT_AUTH_TOKEN": "YOUR_AUTH_TOKEN",
        "TWIKIT_CT0": "YOUR_CT0"
      }
    }
  }
}
```

Then enable it in **Settings → MCP**.

### Windsurf

Edit `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "twikit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/bintangtimurlangit/twikit-mcp", "twikit-mcp"],
      "env": {
        "TWIKIT_AUTH_TOKEN": "YOUR_AUTH_TOKEN",
        "TWIKIT_CT0": "YOUR_CT0"
      }
    }
  }
}
```

### VS Code (Copilot / MCP)

Create `.vscode/mcp.json` in your workspace (VS Code uses `servers` and a `type`
field):

```json
{
  "servers": {
    "twikit": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/bintangtimurlangit/twikit-mcp", "twikit-mcp"],
      "env": {
        "TWIKIT_AUTH_TOKEN": "YOUR_AUTH_TOKEN",
        "TWIKIT_CT0": "YOUR_CT0"
      }
    }
  }
}
```

---

## Optional: disable or tune rate limiting

The server throttles to 30 calls/minute by default. Add to the `env` block:

```json
"env": {
  "TWIKIT_AUTH_TOKEN": "YOUR_AUTH_TOKEN",
  "TWIKIT_CT0": "YOUR_CT0",
  "TWIKIT_MCP_RATE_LIMIT": "off"
}
```

or raise the cap with `"TWIKIT_MCP_RATE_LIMIT_PER_MINUTE": "60"`.

---

## Verify

Once connected, ask your assistant to call the **`whoami`** tool — it should
return your account's user id. `rate_limit_status` shows the active throttle.

If tools don't appear, confirm `uv` is on your `PATH`, the config is valid JSON,
and you restarted the client. If tools appear but every call errors, your
`auth_token` / `ct0` are missing or expired — re-copy them (Step 1).
