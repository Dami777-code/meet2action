# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install (editable with test extras)
pip install -e ".[test]"

# Run all tests
python -m pytest

# Run a single test
python -m pytest tests/test_parser.py::test_parse_actions_extracts_owner_and_due_when_obvious

# Lint / format (Ruff)
ruff check src tests
ruff format src tests

# Manual smoke test
meet2action parse tests/fixtures/notes_sample.txt --out actions.md
meet2action parse tests/fixtures/notes_sample.txt --format json --out actions.json
```

## Architecture

The pipeline is a straight line: **CLI → parser → formatter → file write**.

- `cli.py` — Typer app with a single `parse` command. Input validation (file existence, `.md`/`.txt` extension, `--format` value) happens here before any parsing. `run_parse()` is the testable core of the command.
- `parser.py` — `parse_actions(text) -> ParseResult`. Fully deterministic, regex-based. No NLP. Each line is checked by `_is_candidate_action()` (action-hint keywords, non-action prefix/label blocklist) then passed to `_extract_action_item()` which chains `_extract_owner → _extract_due_date → _normalize_task_text`.
- `formatter.py` — Two pure functions: `format_actions_markdown` and `format_actions_json`. Neither touches I/O.
- `models.py` — Two frozen dataclasses: `ActionItem` (task, owner, due_date) and `ParseResult` (actions list + line counts).

### Key parsing rules to preserve
- Owner is extracted only for `Name to ...`, `Name will ...`, `Name: <action>`, `@Name <action>` patterns.
- Due date requires `by`/`due` + ISO date (validated) or weekday name. Malformed ISO dates (e.g. `2026-3-7`) are silently dropped.
- Lines starting with `Discussion:`, `Status:`, `Note:`, `Attendees:`, `we will discuss`, etc. are suppressed as non-action. Generic colon labels (`Topic:`, `FYI:`, `Background:`) are also suppressed unless the label looks like a proper-name owner.

## Workflow

Before making changes:
- Confirm current branch and git status.
- Propose a short plan first unless explicitly asked for direct edits.
- Do not run full test suites unless necessary; ask first.
- Do not delete branches or perform remote git actions without explicit approval.
- Prefer WSL-native tools and paths.

## Constraints (V1)

- Single `parse` command only — no additional commands.
- No web UI, database, auth, or external integrations.
- No NLP libraries; keep parsing heuristic and deterministic.
- Keep dependencies minimal: `typer` for CLI, `pytest` for tests, `ruff` for linting.
