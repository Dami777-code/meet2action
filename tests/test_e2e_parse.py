import json
import os
import subprocess
import sys
from pathlib import Path


def _run_cli_command(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _run_console_script(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    argv = repr(["meet2action", *args])
    return _run_cli_command(
        [
            sys.executable,
            "-c",
            (
                "from meet2action.cli import cli; "
                "import sys; "
                f"sys.argv = {argv}; "
                "cli()"
            ),
        ],
        env=env,
    )


def test_parse_command_end_to_end_with_fixture(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/notes_sample.txt")
    out_file = tmp_path / "actions.md"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_cli_command(
        [sys.executable, "-m", "meet2action.cli", "parse", str(fixture), "--out", str(out_file)],
        env,
    )

    assert result.returncode == 0
    assert "extracted 3 actions" in result.stdout
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    assert "- [ ] Draft kickoff agenda (owner: Alice, due: 2026-03-20)" in content
    assert "- [ ] Send vendor shortlist (due: Friday)" in content
    assert "- [ ] Follow up with legal (owner: Bob)" in content


def test_console_script_callable_dispatches_parse_command(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/notes_sample.txt")
    out_file = tmp_path / "actions.md"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(
        ["parse", str(fixture), "--out", str(out_file)],
        env,
    )

    assert result.returncode == 0
    assert "extracted 3 actions" in result.stdout
    assert out_file.exists()


def test_console_script_callable_returns_error_for_missing_input(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    out_file = tmp_path / "actions.md"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(
        ["parse", str(missing), "--out", str(out_file)],
        env,
    )

    assert result.returncode == 1
    assert f"Error: input file does not exist: {missing}" in result.stdout
    assert not out_file.exists()


def test_console_script_callable_returns_error_for_invalid_extension(tmp_path: Path) -> None:
    invalid_input = tmp_path / "notes.csv"
    invalid_input.write_text("Alice to draft kickoff agenda by 2026-03-20.\n", encoding="utf-8")
    out_file = tmp_path / "actions.md"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(
        ["parse", str(invalid_input), "--out", str(out_file)],
        env,
    )

    assert result.returncode == 1
    assert "Error: input file must be .md or .txt" in result.stdout
    assert not out_file.exists()


def test_console_script_callable_format_json_produces_valid_json(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/notes_sample.txt")
    out_file = tmp_path / "actions.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(
        ["parse", str(fixture), "--out", str(out_file), "--format", "json"],
        env,
    )

    assert result.returncode == 0
    assert "extracted 3 actions" in result.stdout
    assert "Wrote JSON to:" in result.stdout
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["total_lines"] == 4
    assert data["candidate_lines"] == 3
    assert len(data["actions"]) == 3
    tasks = [a["task"] for a in data["actions"]]
    assert "Draft kickoff agenda" in tasks
    assert "Send vendor shortlist" in tasks
    assert "Follow up with legal" in tasks


def test_console_script_callable_writes_empty_checklist_when_no_actions_found(
    tmp_path: Path,
) -> None:
    notes = tmp_path / "notes.txt"
    notes.write_text("Discussion: roadmap\nStatus: on track\n", encoding="utf-8")
    out_file = tmp_path / "actions.md"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(
        ["parse", str(notes), "--out", str(out_file)],
        env,
    )

    assert result.returncode == 0
    assert "Parsed 2 lines, found 0 candidate lines, extracted 0 actions." in result.stdout
    assert out_file.exists()
    assert out_file.read_text(encoding="utf-8") == "# Action Items\n\n_No action items found._\n"
