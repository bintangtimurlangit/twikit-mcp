# Contributing to twikit-mcp

Thanks for helping out! A few lightweight conventions keep the history and
tracker readable.

## Conventional Commits

This project follows the
[**Conventional Commits 1.0.0**](https://www.conventionalcommits.org/en/v1.0.0/)
specification for **commit messages, pull-request titles, and issue titles**.

Format:

```
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Use for |
|---|---|
| `feat` | A new feature or tool |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or fixing tests |
| `perf` | Performance improvement |
| `build` | Build system, packaging, or dependencies |
| `ci` | CI configuration |
| `chore` | Maintenance that doesn't touch src or tests |
| `style` | Formatting only (no code meaning change) |
| `revert` | Reverts a previous commit |

### Scope

Optional, in parentheses, naming the area touched — e.g. `feat(tools):`,
`fix(ratelimit):`, `docs(install):`.

### Breaking changes

Append `!` after the type/scope **and/or** add a `BREAKING CHANGE:` footer:

```
feat(auth)!: require TWIKIT_COOKIES_FILE to be absolute

BREAKING CHANGE: relative cookie paths are no longer resolved.
```

### Examples

```
feat(tools): add get_list_tweets tool
fix(ratelimit): re-anchor clock after sleep so rate isn't doubled
docs(install): add Windsurf setup
build(deps): pin mcp>=1.2.0
test(serialization): cover KeyError-raising tweet properties
```

## Pull requests

- Title must be a valid Conventional Commit line (a squash-merge uses it as the
  commit subject).
- Describe **what** changed and **why**; link issues with `Closes #123`.
- Run the tests before opening: `python -m pytest tests/` (or run each
  `tests/test_*.py` directly).

## Issues

- Prefix issue titles with a Conventional Commit type so intent is clear, e.g.
  `fix: whoami returns null on fresh cookies` or
  `feat: support uploading media in post_tweet`.
- Include your client (Claude Code / Cursor / …), how you installed, and any
  error output.

## Credit

This project wraps [twikit](https://github.com/d60/twikit) by **d60**. Please
also consider contributing library-level fixes upstream.
