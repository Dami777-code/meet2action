from dataclasses import dataclass


@dataclass(frozen=True)
class ActionItem:
    """A normalized action item extracted from meeting notes."""

    task: str
    owner: str | None = None
    due_date: str | None = None


@dataclass(frozen=True)
class ParseResult:
    """All extracted actions and lightweight parse stats."""

    actions: list[ActionItem]
    total_lines: int
    candidate_lines: int
