from __future__ import annotations

from pathlib import Path

import typer

from .formatter import format_actions_json, format_actions_markdown
from .parser import parse_actions

app = typer.Typer(
    help="Convert meeting notes into actionable markdown checklists.",
    add_completion=False,
)

_NOTES_EXTENSIONS: frozenset[str] = frozenset({".md", ".txt"})


@app.callback()
def main() -> None:
    """Meeting-to-Action CLI."""


def cli() -> None:
    app()


def run_parse(input_file: Path, out: Path, fmt: str, dry_run: bool = False) -> None:
    if not input_file.exists():
        typer.echo(f"Error: input file does not exist: {input_file}")
        raise typer.Exit(code=1)
    if input_file.suffix.lower() not in _NOTES_EXTENSIONS:
        typer.echo("Error: input file must be .md or .txt")
        raise typer.Exit(code=1)

    text = input_file.read_text(encoding="utf-8")
    result = parse_actions(text)

    if fmt == "json":
        rendered = format_actions_json(result)
        label = "JSON"
    else:
        rendered = format_actions_markdown(result.actions)
        label = "markdown checklist"

    typer.echo(
        f"Parsed {result.total_lines} lines, found {result.candidate_lines} candidate lines, "
        f"extracted {len(result.actions)} actions."
    )

    if dry_run:
        typer.echo(f"[dry-run] would write {label} to: {out}")
        typer.echo(rendered)
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
        typer.echo(f"Wrote {label} to: {out}")


def _derive_output_path(
    input_file: Path,
    fmt: str,
    input_dir: Path | None = None,
    out_dir: Path | None = None,
) -> Path:
    ext = "_actions.json" if fmt == "json" else "_actions.md"
    output_name = input_file.stem + ext
    if out_dir is not None and input_dir is not None:
        rel = input_file.parent.relative_to(input_dir)
        return out_dir / rel / output_name
    return input_file.parent / output_name


def _collect_notes_files(input_dir: Path, recursive: bool) -> list[Path]:
    if recursive:
        return sorted(
            f for f in input_dir.rglob("*") if f.is_file() and f.suffix.lower() in _NOTES_EXTENSIONS
        )
    return sorted(
        f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in _NOTES_EXTENSIONS
    )


def _check_output_collisions(
    files: list[Path],
    fmt: str,
    input_dir: Path,
    out_dir: Path | None,
) -> None:
    seen: dict[Path, Path] = {}
    collisions: list[str] = []
    for f in files:
        out_path = _derive_output_path(f, fmt, input_dir, out_dir)
        if out_path in seen:
            collisions.append(f"  {seen[out_path]} and {f} → {out_path}")
        else:
            seen[out_path] = f
    if collisions:
        typer.echo("Error: output path collisions detected:")
        for line in collisions:
            typer.echo(line)
        raise typer.Exit(code=1)


def _run_parse_directory(
    input_dir: Path,
    fmt: str,
    recursive: bool,
    out_dir: Path | None,
    dry_run: bool,
) -> None:
    files = _collect_notes_files(input_dir, recursive)
    if not files:
        typer.echo(f"No .md or .txt files found in: {input_dir}")
        raise typer.Exit(code=1)

    _check_output_collisions(files, fmt, input_dir, out_dir)

    for input_file in files:
        out = _derive_output_path(input_file, fmt, input_dir, out_dir)
        run_parse(input_file, out, fmt, dry_run=dry_run)


@app.command()
def parse(
    input_file: Path = typer.Argument(..., help="Path to .md or .txt notes file, or a directory"),
    out: Path | None = typer.Option(
        None,
        "--out",
        "-o",
        help="Output file path. Not valid when input is a directory.",
    ),
    fmt: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Output format: markdown or json",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recurse into subdirectories. Only valid when input is a directory.",
    ),
    out_dir: Path | None = typer.Option(
        None,
        "--out-dir",
        help=(
            "Output directory for batch runs. Relative folder structure is preserved. "
            "Not valid when input is a single file."
        ),
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print output to stdout without writing any files.",
    ),
) -> None:
    """Parse a notes file (or directory of notes files) into action checklists."""

    if fmt not in {"markdown", "json"}:
        typer.echo(f"Error: unsupported format '{fmt}'. Choose markdown or json.")
        raise typer.Exit(code=1)

    if input_file.is_dir():
        if out is not None:
            typer.echo("Error: --out is not valid when input is a directory.")
            raise typer.Exit(code=1)
        _run_parse_directory(input_file, fmt, recursive=recursive, out_dir=out_dir, dry_run=dry_run)
        return

    # Single-file input
    if recursive:
        typer.echo("Error: --recursive requires a directory input.")
        raise typer.Exit(code=1)
    if out_dir is not None:
        typer.echo("Error: --out-dir is not valid when input is a single file.")
        raise typer.Exit(code=1)

    run_parse(
        input_file,
        out if out is not None else Path("actions.md"),
        fmt,
        dry_run=dry_run,
    )


if __name__ == "__main__":
    cli()
