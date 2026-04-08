# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-04-08

### Added
- `--version` / `-V` flag to display the installed package version.
- GitHub Actions CI workflow: lint + test matrix on Python 3.11 and 3.12.
- GitHub Actions PyPI publish workflow triggered on version tags.
- `CONTRIBUTING.md` with setup and PR workflow instructions.
- Project URLs (Homepage, Repository, Issues) in `pyproject.toml`.

### Fixed
- CLI output defaults now behave correctly when `--out` is omitted.
- Batch directory reruns no longer fail on pre-existing output files.

## [1.0.0] - 2025-12-01

### Added
- `meet2action parse` command (single `parse` command, V1 scope).
- Heuristic regex-based parser — no NLP dependencies.
- Owner extraction for `Name to …`, `Name will …`, `Name: <action>`, and `@Name <action>` patterns.
- Multi-owner extraction (comma/and-separated names on a single line).
- Due-date extraction from `by`/`due` + ISO date (validated) or weekday name.
- Markdown checklist output (default) and JSON output (`--format json`).
- `--out` flag to write output to a file instead of stdout.
- `--out-dir` flag to write output files alongside source files.
- `--recursive` flag for batch processing of directories.
- `--dry-run` flag to preview output paths without writing files.
- Collision detection to prevent silent overwrites in batch mode.
- Frozen dataclasses `ActionItem` and `ParseResult` in `models.py`.
- Comprehensive test suite: parser edge cases, formatter, CLI helpers, and end-to-end tests.
- MIT License.

[Unreleased]: https://github.com/Dami777-code/meet2action/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/Dami777-code/meet2action/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Dami777-code/meet2action/releases/tag/v1.0.0
