from __future__ import annotations

import re

from .models import ActionItem, ParseResult

_BULLET_PREFIX = re.compile(r"^\s*[-*+]\s+")
_DUE_PATTERNS = [
    re.compile(r"\bby\s+(\d{4}-\d{2}-\d{2})\b", re.IGNORECASE),
    re.compile(r"\bdue\s+(\d{4}-\d{2}-\d{2})\b", re.IGNORECASE),
    re.compile(
        r"\bby\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdue\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
        re.IGNORECASE,
    ),
]
_ACTION_HINTS = (
    "to ",
    "will ",
    "please ",
    "follow up",
    "send ",
    "draft ",
    "review ",
    "prepare ",
    "finalize ",
    "schedule ",
)


def parse_actions(text: str) -> ParseResult:
    """Parse action items from meeting notes using deterministic rules."""

    lines = [line.rstrip() for line in text.splitlines()]
    actions: list[ActionItem] = []
    candidate_count = 0

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue

        line = _BULLET_PREFIX.sub("", stripped)
        if not _is_candidate_action(line):
            continue

        candidate_count += 1
        action = _extract_action_item(line)
        if action:
            actions.append(action)

    return ParseResult(actions=actions, total_lines=len(lines), candidate_lines=candidate_count)


def _is_candidate_action(line: str) -> bool:
    lowered = line.lower()
    return any(hint in lowered for hint in _ACTION_HINTS)


def _extract_action_item(line: str) -> ActionItem | None:
    owner, remainder = _extract_owner(line)
    due_date, remainder = _extract_due_date(remainder)
    task = _normalize_task_text(remainder)

    if not task:
        return None

    return ActionItem(task=task, owner=owner, due_date=due_date)


def _extract_owner(line: str) -> tuple[str | None, str]:
    match = re.match(r"^([A-Z][a-z]+)\s+to\s+(.+)$", line)
    if match:
        owner = match.group(1)
        return owner, match.group(2)

    match = re.match(r"^([A-Z][a-z]+)\s+will\s+(.+)$", line)
    if match:
        owner = match.group(1)
        return owner, match.group(2)

    return None, line


def _extract_due_date(line: str) -> tuple[str | None, str]:
    for pattern in _DUE_PATTERNS:
        match = pattern.search(line)
        if match:
            due_date = match.group(1)
            remainder = pattern.sub("", line)
            return due_date, remainder
    return None, line


def _normalize_task_text(task: str) -> str:
    normalized = task.strip(" .\t")
    normalized = re.sub(r"\s+", " ", normalized)
    if normalized:
        return normalized[0].upper() + normalized[1:]
    return normalized
