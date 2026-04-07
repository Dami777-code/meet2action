# Contributing to meet2action

## Prerequisites

- Python 3.11+
- Git

## Development setup

```bash
git clone https://github.com/Dami777-code/meet2action.git
cd meet2action
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pip install ruff
```

## Running tests

```bash
python -m pytest
```

## Running the linter

```bash
ruff check src tests
ruff format src tests
```

## Submitting a pull request

1. Branch off `main`: `git checkout -b feat/your-feature`
2. Keep changes focused — one feature or fix per PR
3. Add tests for any behavior changes
4. Ensure `pytest` and `ruff check` both pass before pushing
5. Open a PR against `main` with a clear description of what and why

## Reporting issues

Open an issue at https://github.com/Dami777-code/meet2action/issues. Include the command you ran, the input (or a minimal reproduction), and the output you expected vs. what you got.
