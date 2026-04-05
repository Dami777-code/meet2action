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
            (f"from meet2action.cli import cli; import sys; sys.argv = {argv}; cli()"),
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


def test_parse_directory_produces_per_file_output(tmp_path: Path) -> None:
    (tmp_path / "meeting1.txt").write_text(
        "Alice to draft kickoff agenda by 2026-03-20.\n", encoding="utf-8"
    )
    (tmp_path / "meeting2.md").write_text("Bob will follow up with legal.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path)], env)

    assert result.returncode == 0
    assert (tmp_path / "meeting1_actions.md").exists()
    assert (tmp_path / "meeting2_actions.md").exists()
    assert "Draft kickoff agenda" in (tmp_path / "meeting1_actions.md").read_text(encoding="utf-8")
    assert "Follow up with legal" in (tmp_path / "meeting2_actions.md").read_text(encoding="utf-8")


def test_parse_directory_json_format(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("Alice and Bob to review the deck.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path), "--format", "json"], env)

    assert result.returncode == 0
    out_file = tmp_path / "notes_actions.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["actions"][0]["owner"] == "Alice, Bob"


def test_parse_directory_with_out_flag_errors(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("Alice to send report.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path), "--out", str(tmp_path / "out.md")], env)

    assert result.returncode == 1
    assert "Error: --out is not valid when input is a directory." in result.stdout


def test_parse_directory_empty_errors(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path)], env)

    assert result.returncode == 1
    assert "No .md or .txt files found in:" in result.stdout


def test_parse_directory_ignores_non_notes_files(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("Alice to send report.\n", encoding="utf-8")
    (tmp_path / "data.csv").write_text("col1,col2\nval1,val2\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path)], env)

    assert result.returncode == 0
    assert (tmp_path / "notes_actions.md").exists()
    assert not (tmp_path / "data_actions.md").exists()


def test_parse_single_file_out_default_unchanged(tmp_path: Path) -> None:
    notes = tmp_path / "notes.txt"
    notes.write_text("Alice to send report.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from meet2action.cli import cli; "
                "import sys; "
                f"sys.argv = {repr(['meet2action', 'parse', str(notes)])}; "
                "cli()"
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert (tmp_path / "actions.md").exists()


# ---------------------------------------------------------------------------
# --recursive
# ---------------------------------------------------------------------------


def test_parse_recursive_finds_files_in_subdirectories(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "top.txt").write_text("Alice to send report.\n", encoding="utf-8")
    (sub / "nested.txt").write_text("Bob will review the deck.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path), "--recursive"], env)

    assert result.returncode == 0
    assert (tmp_path / "top_actions.md").exists()
    assert (sub / "nested_actions.md").exists()


def test_parse_recursive_empty_tree_errors(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path), "--recursive"], env)

    assert result.returncode == 1
    assert "No .md or .txt files found in:" in result.stdout


def test_parse_recursive_with_single_file_errors(tmp_path: Path) -> None:
    notes = tmp_path / "notes.txt"
    notes.write_text("Alice to send report.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(notes), "--recursive"], env)

    assert result.returncode == 1
    assert "Error: --recursive requires a directory input." in result.stdout


# ---------------------------------------------------------------------------
# --out-dir
# ---------------------------------------------------------------------------


def test_parse_out_dir_places_files_in_specified_directory(tmp_path: Path) -> None:
    input_dir = tmp_path / "notes"
    input_dir.mkdir()
    out_dir = tmp_path / "output"
    (input_dir / "meeting.txt").write_text("Alice to draft kickoff agenda.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(input_dir), "--out-dir", str(out_dir)], env)

    assert result.returncode == 0
    assert (out_dir / "meeting_actions.md").exists()
    assert not (input_dir / "meeting_actions.md").exists()


def test_parse_out_dir_creates_directory_if_absent(tmp_path: Path) -> None:
    input_dir = tmp_path / "notes"
    input_dir.mkdir()
    out_dir = tmp_path / "new" / "nested" / "output"
    (input_dir / "meeting.txt").write_text("Alice to draft kickoff agenda.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(input_dir), "--out-dir", str(out_dir)], env)

    assert result.returncode == 0
    assert out_dir.is_dir()
    assert (out_dir / "meeting_actions.md").exists()


def test_parse_out_dir_with_recursive_preserves_relative_structure(tmp_path: Path) -> None:
    input_dir = tmp_path / "notes"
    sub = input_dir / "2026" / "Q1"
    sub.mkdir(parents=True)
    (input_dir / "top.txt").write_text("Alice to send report.\n", encoding="utf-8")
    (sub / "standup.txt").write_text("Bob will review the deck.\n", encoding="utf-8")
    out_dir = tmp_path / "output"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(
        ["parse", str(input_dir), "--recursive", "--out-dir", str(out_dir)], env
    )

    assert result.returncode == 0
    assert (out_dir / "top_actions.md").exists()
    assert (out_dir / "2026" / "Q1" / "standup_actions.md").exists()


def test_parse_out_dir_with_single_file_errors(tmp_path: Path) -> None:
    notes = tmp_path / "notes.txt"
    notes.write_text("Alice to send report.\n", encoding="utf-8")
    out_dir = tmp_path / "output"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(notes), "--out-dir", str(out_dir)], env)

    assert result.returncode == 1
    assert "Error: --out-dir is not valid when input is a single file." in result.stdout


# ---------------------------------------------------------------------------
# Collision detection
# ---------------------------------------------------------------------------


def test_parse_directory_stem_collision_errors_before_any_write(tmp_path: Path) -> None:
    (tmp_path / "notes.md").write_text("Alice to draft agenda.\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("Bob will review deck.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path)], env)

    assert result.returncode == 1
    assert "Error: output path collisions detected:" in result.stdout
    # No output files written
    assert not (tmp_path / "notes_actions.md").exists()


# ---------------------------------------------------------------------------
# --dry-run
# ---------------------------------------------------------------------------


def test_parse_dry_run_single_file_writes_nothing(tmp_path: Path) -> None:
    notes = tmp_path / "notes.txt"
    notes.write_text("Alice to draft kickoff agenda by 2026-03-20.\n", encoding="utf-8")
    out_file = tmp_path / "actions.md"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(notes), "--out", str(out_file), "--dry-run"], env)

    assert result.returncode == 0
    assert not out_file.exists()
    assert "[dry-run] would write markdown checklist to:" in result.stdout
    assert "Draft kickoff agenda" in result.stdout


def test_parse_dry_run_directory_writes_nothing(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("Alice to send report.\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Bob will review deck.\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(["parse", str(tmp_path), "--dry-run"], env)

    assert result.returncode == 0
    assert not (tmp_path / "a_actions.md").exists()
    assert not (tmp_path / "b_actions.md").exists()
    assert "[dry-run]" in result.stdout


def test_parse_dry_run_json_format_writes_nothing(tmp_path: Path) -> None:
    notes = tmp_path / "notes.txt"
    notes.write_text("Alice to draft kickoff agenda by 2026-03-20.\n", encoding="utf-8")
    out_file = tmp_path / "actions.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = _run_console_script(
        ["parse", str(notes), "--out", str(out_file), "--format", "json", "--dry-run"], env
    )

    assert result.returncode == 0
    assert not out_file.exists()
    assert "[dry-run] would write JSON to:" in result.stdout
