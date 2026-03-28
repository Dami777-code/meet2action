# AGENTS.md

Guidance for contributors and coding agents working in this repository.

## Project Goal

Build a focused CLI tool that converts meeting notes into actionable markdown checklists.

## Current Phase

Bootstrap and planning. Avoid premature complexity.

## V1 Boundaries (must respect)

- Single CLI command: `parse`
- Input is a single local `.md` or `.txt` file
- Extract actions from bullets and sentences
- Extract owner and due date only when obvious
- Produce one standardized markdown output file
- Print a concise terminal summary
- Include unit tests for parser and formatter

## Out of Scope for V1

Do not implement:

- Web frontend or APIs
- Databases
- Auth
- Integrations
- Audio transcription / OCR / PDF parsing
- Multilingual handling
- Advanced NLP models or confidence scoring
- Background workers
- Deployment/IaC

## Technical Preferences

- Python 3.11+
- Typer for CLI
- pytest for tests
- Ruff for linting/formatting
- Keep dependencies minimal
- Prefer straightforward deterministic parsing heuristics over complex NLP

## Architecture Target

- `src/meet2action/cli.py`
- `src/meet2action/parser.py`
- `src/meet2action/formatter.py`
- `src/meet2action/models.py`

## Development Practices

- Keep changes small and reviewable.
- Add tests with behavior changes.
- Document CLI behavior in README examples.
- If uncertain, choose simple and explicit logic.
