import subprocess
import sys
from pathlib import Path


def test_parse_command_end_to_end_with_fixture(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/notes_sample.txt")
    out_file = tmp_path / "actions.md"

    result = subprocess.run(
        [sys.executable, "-m", "meet2action.cli", "parse", str(fixture), "--out", str(out_file)],
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": "src"},
    )

    assert result.returncode == 0
    assert "extracted 3 actions" in result.stdout
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    assert "- [ ] Draft kickoff agenda (owner: Alice, due: 2026-03-20)" in content
    assert "- [ ] Please send vendor shortlist (due: Friday)" in content
    assert "- [ ] Follow up with legal (owner: Bob)" in content
