from __future__ import annotations

import argparse
from pathlib import Path

from .formatter import format_actions_markdown
from .parser import parse_actions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meet2action", description="Convert meeting notes into actionable markdown checklists."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser("parse", help="Parse a notes file into markdown checklist")
    parse_cmd.add_argument("input_file", type=Path, help="Path to .md or .txt notes")
    parse_cmd.add_argument(
        "--out",
        "-o",
        type=Path,
        default=Path("actions.md"),
        help="Output markdown path",
    )

    return parser


def run_parse(input_file: Path, out: Path) -> int:
    if not input_file.exists():
        print(f"Error: input file does not exist: {input_file}")
        return 1
    if input_file.suffix.lower() not in {".md", ".txt"}:
        print("Error: input file must be .md or .txt")
        return 1

    text = input_file.read_text(encoding="utf-8")
    result = parse_actions(text)
    rendered = format_actions_markdown(result.actions)

    out.write_text(rendered, encoding="utf-8")

    print(
        f"Parsed {result.total_lines} lines, found {result.candidate_lines} candidate lines, "
        f"extracted {len(result.actions)} actions."
    )
    print(f"Wrote markdown checklist to: {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "parse":
        return run_parse(args.input_file, args.out)

    print("Error: unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
