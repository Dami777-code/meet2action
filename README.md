# Meeting-to-Action (Project C)

Meeting-to-Action is a small CLI tool that converts raw meeting notes (`.md` or `.txt`) into a clean, actionable checklist containing tasks, optional owners, and optional due dates.

## V1 Scope

- One CLI command: `parse`
- Input: one local `.md` or `.txt` file
- Extraction of action items from bullets and sentences
- Optional extraction of owner and due date only when obvious
- Output: one markdown file with a standardized checklist format
- Basic terminal summary
- Unit tests for parser and formatter

## Out of Scope (V1)

- Web UI
- Database
- Authentication/authorization
- Third-party integrations
- Audio transcription
- OCR/PDF parsing
- Multilingual support
- Advanced NLP confidence scoring
- Background jobs
- Cloud deployment

## Requirements

- Python 3.11+

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
meet2action parse notes.md --out actions.md
```

## Example Input

```text
- Alice to draft kickoff agenda by 2026-03-20.
Please send vendor shortlist by Friday.
Bob will follow up with legal.
General discussion about roadmap.
```

## Example Output

```markdown
# Action Items

- [ ] Draft kickoff agenda (owner: Alice, due: 2026-03-20)
- [ ] Send vendor shortlist (due: Friday)
- [ ] Follow up with legal (owner: Bob)
```


## Extraction rules (V1)

The parser uses deterministic, conservative rules:

- Action candidates are lines with clear action cues (for example: `to`, `will`, `send`, `review`, `prepare`, `follow up`).
- Owner is extracted only for obvious formats:
  - `Alice to ...`
  - `Alice will ...`
  - `Alice: ...`
  - `@Alice ...`
- Due date is extracted only for obvious formats:
  - `by YYYY-MM-DD` or `due YYYY-MM-DD` (must be a real calendar date)
  - `by Monday` or `due Friday` (weekday names)
- Discussion/status context lines (for example `Discussion:` or `We will discuss ...`) are intentionally ignored to reduce false positives.
- Generic context labels like `Topic:`, `FYI:`, and `Background:` are ignored unless they clearly match an obvious action-owner pattern.
- Leading `Please` is removed from task text when present as politeness.

## Project Layout

```text
meet2action/
├── src/meet2action/
│   ├── cli.py
│   ├── formatter.py
│   ├── models.py
│   └── parser.py
└── tests/
    ├── fixtures/notes_sample.txt
    ├── test_e2e_parse.py
    ├── test_formatter.py
    └── test_parser.py
```
