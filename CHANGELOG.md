# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0/). For **how** we version, tag, and publish, see [docs/RELEASES.md](./docs/RELEASES.md).

## [Unreleased]

## [0.1.0] - 2026-07-21

### Added

- Standardized project scaffolding: `.editorconfig`, `.env.example`, Ruff (lint + format), mypy config, Conventional Commits (commitizen), pre-commit hooks, CI + release workflows, `.yml` issue templates, and a `docs/` guide set.
- Initial release: MCP server exposing **twikit's** Twitter / X capabilities to AI assistants over stdio — **no official X API key required** (authenticates via `auth_token` + `ct0` cookies).
- **27 tools** across session, users, tweets (read + write), timelines, trends, and DMs.
- Built-in token-bucket **rate limiting** (30 calls/min by default), configurable via `TWIKIT_MCP_RATE_LIMIT` / `TWIKIT_MCP_RATE_LIMIT_PER_MINUTE`.
- Bundles a lightly patched copy of [twikit](https://github.com/d60/twikit) under `twikit/` to fix the X login bug, pending an upstream fix.

### Changed

- The PyPI distribution, GitHub repository, and CLI command are named `twikit-x-mcp`. The Python import module is `twikit_x_mcp`.

[Unreleased]: https://github.com/bintangtimurlangit/twikit-x-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bintangtimurlangit/twikit-x-mcp/releases/tag/v0.1.0
