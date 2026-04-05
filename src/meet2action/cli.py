from __future__ import annotations

from pathlib import Path

import typer

from .formatter import format_actions_json, format_actions_markdown
from .parser import parse_actions

app = typer.Typer(
    help="Convert meeting notes into actionable markdown checklists.",
    add_completion=False,
)


@app.callback()
def main() -> None:
    """Meeting-to-Action CLI."""


def cli() -> None:
    app()


def run_parse(input_file: Path, out: Path, fmt: str) -> None:
    if not input_file.exists():
        typer.echo(f"Error: input file does not exist: {input_file}")
        raise typer.Exit(code=1)
    if input_file.suffix.lower() not in {".md", ".txt"}:
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

    out.write_text(rendered, encoding="utf-8")

    typer.echo(
        f"Parsed {result.total_lines} lines, found {result.candidate_lines} candidate lines, "
        f"extracted {len(result.actions)} actions."
    )
    typer.echo(f"Wrote {label} to: {out}")


def _derive_output_path(input_file: Path, fmt: str) -> Path:
    ext = "_actions.json" if fmt == "json" else "_actions.md"
    return input_file.parent / (input_file.stem + ext)


def _run_parse_directory(input_dir: Path, fmt: str) -> None:
    files = sorted(
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in {".md", ".txt"}
    )
    if not files:
        typer.echo(f"No .md or .txt files found in: {input_dir}")
        raise typer.Exit(code=1)

    for input_file in files:
        out = _derive_output_path(input_file, fmt)
        run_parse(input_file, out, fmt)


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
) -> None:
    """Parse a notes file (or directory of notes files) into action checklists."""

    if fmt not in {"markdown", "json"}:
        typer.echo(f"Error: unsupported format '{fmt}'. Choose markdown or json.")
        raise typer.Exit(code=1)

    if input_file.is_dir():
        if out is not None:
            typer.echo("Error: --out is not valid when input is a directory.")
            raise typer.Exit(code=1)
        _run_parse_directory(input_file, fmt)
        return

    run_parse(input_file, out if out is not None else Path("actions.md"), fmt)


if __name__ == "__main__":
    cli()
