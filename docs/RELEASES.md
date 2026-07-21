# Releases and versioning

This project uses **Semantic Versioning** ([SemVer 2.0](https://semver.org/)). The canonical version string is **`pyproject.toml`** → `project.version` (mirrored in `[tool.commitizen]`).

Commit messages follow **[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)** (`feat:`, `fix:`, `docs:`, `chore:`, …). That pairs with SemVer: `fix` → PATCH, `feat` → MINOR, breaking changes → MAJOR. [commitizen](https://commitizen-tools.github.io/commitizen/) enforces the format (a `commit-msg` pre-commit hook) and can bump the version.

## Version format

`MAJOR.MINOR.PATCH` — e.g. `0.1.0`, `1.2.3`.

- **MAJOR** — Breaking changes (removed/renamed tools, incompatible env or behavior).
- **MINOR** — Backward-compatible features (new tools, new optional config).
- **PATCH** — Bug fixes and safe corrections that do not change the public contract.

## Publishing (maintainers)

The PyPI distribution name is **`twikit-x-mcp`**. Because twikit is vendored in, the wheel is self-contained — no external Git dependencies to resolve.

Releases are handled by the [`release` workflow](../.github/workflows/release.yml): pushing a `vX.Y.Z` tag runs `uv build` and publishes to PyPI via **Trusted Publishing (OIDC)** — tokenless — then creates a GitHub release. One-time setup: register this repo + `release.yml` as a Trusted Publisher for the `twikit-x-mcp` project on PyPI.

**To cut a release:**

1. Bump the version in **`pyproject.toml`** (and `[tool.commitizen]`) per SemVer — or run `cz bump`.
2. Update **`CHANGELOG.md`**: move items from **`[Unreleased]`** into **`[X.Y.Z] - YYYY-MM-DD`**.
3. Commit with Conventional Commits, e.g. `chore(release): v0.1.1`.
4. Tag and push:

   ```bash
   git tag v0.1.1
   git push origin main --tags
   ```

5. The workflow builds and opens the GitHub release.

## Git tags

Tag stable releases as **`vX.Y.Z`**; prereleases **`vX.Y.Z-beta.N`**.
