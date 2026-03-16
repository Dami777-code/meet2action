from __future__ import annotations

import re
from datetime import date

from .models import ActionItem, ParseResult

_BULLET_PREFIX = re.compile(r"^\s*[-*+]\s+")
_WEEKDAY = r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
_DUE_PATTERNS = [
    re.compile(r"\b(by|due)\s+(\d{4}-\d{2}-\d{2})\b", re.IGNORECASE),
    re.compile(rf"\b(by|due)\s+({_WEEKDAY})\b", re.IGNORECASE),
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
    "@",
    ":",
)
_NON_ACTION_PREFIXES = (
    "discussion:",
    "discuss ",
    "we will discuss",
    "we discussed",
    "status:",
    "note:",
    "attendees:",
)
_NON_ACTION_LABELS = {
    "topic",
    "fyi",
    "background",
    "context",
    "status",
    "note",
    "notes",
    "discussion",
    "attendees",
}
_OWNER_PATTERNS = [
    re.compile(r"^([A-Z][a-z]+)\s+to\s+(.+)$"),
    re.compile(r"^([A-Z][a-z]+)\s+will\s+(.+)$"),
]

_OWNER_PREFIX_PATTERNS = [
    re.compile(r"^([A-Z][a-z]+):\s+(.+)$"),
    re.compile(r"^@([A-Z][a-z]+)\s+(.+)$"),
]

_TASK_START_HINTS = (
    "send ",
    "review ",
    "prepare ",
    "draft ",
    "finalize ",
    "schedule ",
    "follow up",
    "update ",
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
    if lowered.startswith(_NON_ACTION_PREFIXES):
        return False

    if _is_non_action_colon_label(line):
        return False

    if lowered.startswith("we will ") and not any(
        token in lowered
        for token in (
            "send ",
            "review ",
            "prepare ",
            "finalize ",
            "schedule ",
            "follow up",
        )
    ):
        return False

    return any(hint in lowered for hint in _ACTION_HINTS)


def _is_non_action_colon_label(line: str) -> bool:
    label_match = re.match(r"^([^:]{1,40}):\s*(.+)$", line)
    if not label_match:
        return False

    label = label_match.group(1).strip()
    remainder = label_match.group(2).strip()
    if not label or not remainder:
        return True

    if label.lower() in _NON_ACTION_LABELS:
        return True

    if re.match(r"^[A-Z][a-z]+$", label):
        return False

    return not _looks_like_action_task(remainder)


def _extract_action_item(line: str) -> ActionItem | None:
    owner, remainder = _extract_owner(line)
    due_date, remainder = _extract_due_date(remainder)
    task = _normalize_task_text(remainder)

    if not task:
        return None

    return ActionItem(task=task, owner=owner, due_date=due_date)


def _extract_owner(line: str) -> tuple[str | None, str]:
    for pattern in _OWNER_PATTERNS:
        match = pattern.match(line)
        if match:
            return match.group(1), match.group(2)

    for pattern in _OWNER_PREFIX_PATTERNS:
        match = pattern.match(line)
        if match:
            remainder = match.group(2)
            if _looks_like_action_task(remainder):
                return match.group(1), remainder

    return None, line


def _looks_like_action_task(text: str) -> bool:
    lowered = text.strip().lower()
    return any(lowered.startswith(hint) for hint in _TASK_START_HINTS)


def _extract_due_date(line: str) -> tuple[str | None, str]:
    for pattern in _DUE_PATTERNS:
        match = pattern.search(line)
        if match:
            due_date = match.group(2)
            if pattern is _DUE_PATTERNS[0] and not _is_valid_iso_date(due_date):
                continue
            start, end = match.span()
            remainder = f"{line[:start]} {line[end:]}".strip()
            return due_date, remainder
    return None, line


def _is_valid_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _normalize_task_text(task: str) -> str:
    normalized = task.strip(" .\t")
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"^please\s+", "", normalized, flags=re.IGNORECASE)
    normalized = normalized.strip(" .\t")

    if normalized:
        return normalized[0].upper() + normalized[1:]
    return normalized
