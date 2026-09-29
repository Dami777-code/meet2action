# Meet2Action

![CI](https://github.com/Dami777-code/meet2action/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/meet2action)
![Python](https://img.shields.io/pypi/pyversions/meet2action)

**Turn messy meeting notes into a clean, actionable checklist.**

Meet2Action is a small Python CLI that parses `.md` and `.txt` meeting notes, identifies clear action items, and exports them as Markdown or JSON. It favors deterministic, inspectable rules over opaque extraction so the output is predictable and easy to validate.

## Why I built it

Meeting notes often contain a mix of decisions, discussion, context, and actual commitments. The useful next step is usually simple: identify what needs to happen, who owns it when obvious, and when it is due when explicitly stated.

Meet2Action is intentionally narrow. It focuses on doing that one job reliably rather than becoming a full meeting-management platform.

## Example

**Input**

```text
- Alice to draft kickoff agenda by 2099-01-15.
Please send vendor shortlist by Friday.
Bob will follow up with legal.
General discussion about roadmap.
```

**Output**

```markdown
# Action Items

- [ ] Draft kickoff agenda (owner: Alice, due: 2099-01-15)
- [ ] Send vendor shortlist (due: Friday)
- [ ] Follow up with legal (owner: Bob)
```

JSON output is also available for downstream workflows and automation.

## What it demonstrates

- Python 3.11+ package and CLI design
- Typer-based command-line UX
- Deterministic parsing and validation
- Markdown and JSON output formats
- Batch and recursive directory processing
- Automated tests with pytest
- Linting with Ruff
- Build/package validation
- GitHub Actions CI
- Clear scope boundaries and failure behavior

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Parse a single notes file:

```bash
meet2action parse notes.md --out actions.md
```

Produce JSON:

```bash
meet2action parse notes.md --format json --out actions.json
```

Parse a directory:

```bash
meet2action parse ./notes
meet2action parse ./notes --recursive
meet2action parse ./notes --format json --out-dir ./parsed
```

Without `--out`, Meet2Action writes the generated file beside the input. Batch directory scans skip default generated `_actions.md` and `_actions.json` outputs so reruns do not parse them again.

## Extraction behavior

The parser is intentionally conservative.

An action candidate needs a clear action cue such as `to`, `will`, `send`, `review`, `prepare`, or `follow up`.

Owners are extracted only from obvious patterns such as:

- `Alice to ...`
- `Alice will ...`
- `Alice: ...`
- `@Alice ...`

Due dates are extracted only from explicit patterns such as:

- `by 2099-01-15`
- `due 2099-01-15`
- `by Monday`
- `due Friday`

Discussion and status context are deliberately ignored when they do not contain a clear action.

## Validation and failure behavior

Expected validation failures return a non-zero exit code and do not write an output file.

```bash
meet2action parse /tmp/missing.txt --out actions.md
# Error: input file does not exist: /tmp/missing.txt
```

```bash
meet2action parse notes.csv --out actions.md
# Error: input file must be .md or .txt
```

If no actionable lines are found, the tool still writes a valid result:

```markdown
# Action Items

_No action items found._
```

## Development

Run the full local validation pass:

```bash
pytest
ruff check .
python -m pip install build
python -m build
```

`python -m build` creates an isolated build environment by default, so the build backend dependencies must be available locally or installable from the current environment.

## Project structure

```text
meet2action/
├── src/meet2action/
│   ├── cli.py
│   ├── formatter.py
│   ├── models.py
│   └── parser.py
└── tests/
    ├── fixtures/
    ├── test_cli_helpers.py
    ├── test_e2e_parse.py
    ├── test_formatter.py
    └── test_parser.py
```

## Scope

Meet2Action is deliberately a focused CLI. It does **not** currently include a web UI, accounts, a database, third-party integrations, audio transcription, OCR/PDF parsing, background jobs, or cloud deployment.

That constraint keeps the project small, testable, and easy to understand.

