# Changelog

---

## [0.1.0] - 2026-07-21

### Fixed

- Compatible con el nuevo formato de `TimelineTimelineCursor` utilizado por X.
- Se agregó `Client._extract_cursor_value()` para soportar ambos formatos:
  - `content.itemContent.value`
  - `content.value`
- Se eliminó el `KeyError: 'itemContent'` al obtener artículos largos mediante `Client.get_tweet_by_id()`.

### Notes

Este cambio mantiene compatibilidad con versiones anteriores de X sin romper implementaciones existentes.


################################################################################################################

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0/). For **how** we version, tag, and publish, see [docs/RELEASES.md](./docs/RELEASES.md).

## [Unreleased]

### Added

- Standardized project scaffolding: `.editorconfig`, `.env.example`, Ruff (lint + format), mypy config, Conventional Commits (commitizen), pre-commit hooks, CI + release workflows, `.yml` issue templates, and a `docs/` guide set.

### Changed

- **Renamed to `twikit-x-mcp`** — the PyPI distribution, the GitHub repo, and the CLI command are all `twikit-x-mcp` (plain `twikit-mcp` was already taken on PyPI by another project). The Python import module is `twikit_x_mcp`.

## [0.1.0] - 2026-07-13

### Added

- Initial release: MCP server exposing **twikit's** Twitter / X capabilities to AI assistants over stdio — **no official X API key required** (authenticates via `auth_token` + `ct0` cookies).
- **27 tools** across session, users, tweets (read + write), timelines, trends, and DMs.
- Built-in token-bucket **rate limiting** (30 calls/min by default), configurable via `TWIKIT_MCP_RATE_LIMIT` / `TWIKIT_MCP_RATE_LIMIT_PER_MINUTE`.
- Bundles a lightly patched copy of [twikit](https://github.com/d60/twikit) under `twikit/` to fix the X login bug, pending an upstream fix.

[Unreleased]: https://github.com/bintangtimurlangit/twikit-x-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bintangtimurlangit/twikit-x-mcp/releases/tag/v0.1.0
