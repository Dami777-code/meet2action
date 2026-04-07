"""Unit tests for the three private CLI helper functions in cli.py."""

import pytest
import typer

from meet2action.cli import (
    _check_output_collisions,
    _collect_notes_files,
    _derive_output_path,
)

# ---------------------------------------------------------------------------
# _derive_output_path
# ---------------------------------------------------------------------------


def test_derive_output_path_markdown_no_out_dir(tmp_path):
    f = tmp_path / "notes.txt"
    assert _derive_output_path(f, "markdown") == tmp_path / "notes_actions.md"


def test_derive_output_path_json_no_out_dir(tmp_path):
    f = tmp_path / "meeting.md"
    assert _derive_output_path(f, "json") == tmp_path / "meeting_actions.json"


def test_derive_output_path_with_out_dir_flat(tmp_path):
    input_dir = tmp_path / "notes"
    f = input_dir / "session.txt"
    out_dir = tmp_path / "output"
    result = _derive_output_path(f, "markdown", input_dir=input_dir, out_dir=out_dir)
    assert result == out_dir / "session_actions.md"


def test_derive_output_path_with_out_dir_preserves_subdirectory(tmp_path):
    input_dir = tmp_path / "notes"
    f = input_dir / "week1" / "monday.txt"
    out_dir = tmp_path / "output"
    result = _derive_output_path(f, "markdown", input_dir=input_dir, out_dir=out_dir)
    assert result == out_dir / "week1" / "monday_actions.md"


def test_derive_output_path_out_dir_without_input_dir_raises(tmp_path):
    f = tmp_path / "notes.txt"
    out_dir = tmp_path / "output"
    with pytest.raises(AssertionError):
        _derive_output_path(f, "markdown", input_dir=None, out_dir=out_dir)


# ---------------------------------------------------------------------------
# _collect_notes_files
# ---------------------------------------------------------------------------


def test_collect_notes_files_flat_returns_only_md_and_txt(tmp_path):
    (tmp_path / "a.txt").touch()
    (tmp_path / "b.md").touch()
    (tmp_path / "ignore.py").touch()
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.txt").touch()  # nested — must NOT appear in flat mode
    result = _collect_notes_files(tmp_path, recursive=False)
    assert result == sorted([tmp_path / "a.txt", tmp_path / "b.md"])


def test_collect_notes_files_recursive_includes_nested(tmp_path):
    (tmp_path / "root.txt").touch()
    sub = tmp_path / "deep"
    sub.mkdir()
    (sub / "nested.md").touch()
    (sub / "skip.log").touch()
    result = _collect_notes_files(tmp_path, recursive=True)
    assert result == sorted([tmp_path / "root.txt", sub / "nested.md"])


def test_collect_notes_files_extension_match_is_case_insensitive(tmp_path):
    (tmp_path / "upper.TXT").touch()
    (tmp_path / "mixed.Md").touch()
    result = _collect_notes_files(tmp_path, recursive=False)
    assert len(result) == 2


def test_collect_notes_files_empty_dir_returns_empty_list(tmp_path):
    assert _collect_notes_files(tmp_path, recursive=False) == []


def test_collect_notes_files_result_is_sorted(tmp_path):
    for name in ("z.txt", "a.md", "m.txt"):
        (tmp_path / name).touch()
    result = _collect_notes_files(tmp_path, recursive=False)
    assert result == sorted(result)


# ---------------------------------------------------------------------------
# _check_output_collisions
# ---------------------------------------------------------------------------


def test_check_output_collisions_no_collision_passes_silently(tmp_path):
    a = tmp_path / "alpha.txt"
    b = tmp_path / "beta.txt"
    # Must not raise — different stems → different output paths
    _check_output_collisions([a, b], "markdown", tmp_path, None)


def test_check_output_collisions_raises_on_duplicate_input(tmp_path):
    f = tmp_path / "notes.txt"
    f.touch()
    with pytest.raises(typer.Exit):
        _check_output_collisions([f, f], "markdown", tmp_path, None)


def test_check_output_collisions_raises_on_md_txt_same_stem(tmp_path):
    # notes.txt and notes.md both produce notes_actions.md → collision
    a = tmp_path / "notes.txt"
    b = tmp_path / "notes.md"
    with pytest.raises(typer.Exit):
        _check_output_collisions([a, b], "markdown", tmp_path, None)


def test_check_output_collisions_no_false_positive_with_out_dir(tmp_path):
    input_dir = tmp_path / "src"
    sub_a = input_dir / "a"
    sub_b = input_dir / "b"
    sub_a.mkdir(parents=True)
    sub_b.mkdir(parents=True)
    f1 = sub_a / "notes.txt"
    f2 = sub_b / "notes.txt"
    out_dir = tmp_path / "out"
    # Different subdirs → different relative paths → no collision
    _check_output_collisions([f1, f2], "markdown", input_dir, out_dir)


# ---------------------------------------------------------------------------
# --version
# ---------------------------------------------------------------------------


def test_version_flag_exits_zero_and_prints_version() -> None:
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    argv = repr(["meet2action", "--version"])
    cmd = f"from meet2action.cli import cli; import sys; sys.argv = {argv}; cli()"
    result = subprocess.run(
        [sys.executable, "-c", cmd],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "meet2action 1.0.0"
