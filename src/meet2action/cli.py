from __future__ import annotations

from pathlib import Path

import typer

from .formatter import format_actions_markdown
from .parser import parse_actions

app = typer.Typer(
    help="Convert meeting notes into actionable markdown checklists.",
    add_completion=False,
)


@app.callback()
def main() -> None:
    """Meeting-to-Action CLI."""


def run_parse(input_file: Path, out: Path) -> None:
    if not input_file.exists():
        typer.echo(f"Error: input file does not exist: {input_file}")
        raise typer.Exit(code=1)
    if input_file.suffix.lower() not in {".md", ".txt"}:
        typer.echo("Error: input file must be .md or .txt")
        raise typer.Exit(code=1)

    text = input_file.read_text(encoding="utf-8")
    result = parse_actions(text)
    rendered = format_actions_markdown(result.actions)

    out.write_text(rendered, encoding="utf-8")

    typer.echo(
        f"Parsed {result.total_lines} lines, found {result.candidate_lines} candidate lines, "
        f"extracted {len(result.actions)} actions."
    )
    typer.echo(f"Wrote markdown checklist to: {out}")


@app.command()
def parse(
    input_file: Path = typer.Argument(..., help="Path to .md or .txt notes"),
    out: Path = typer.Option(
        Path("actions.md"),
        "--out",
        "-o",
        help="Output markdown path",
    ),
) -> None:
    """Parse a notes file into a markdown checklist."""

    run_parse(input_file, out)


if __name__ == "__main__":
    app()
