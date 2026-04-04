import json

from .models import ActionItem, ParseResult


def format_actions_markdown(actions: list[ActionItem]) -> str:
    """Render extracted actions as a standardized markdown checklist."""

    lines = ["# Action Items", ""]

    for action in actions:
        parts = []
        if action.owner:
            parts.append(f"owner: {action.owner}")
        if action.due_date:
            parts.append(f"due: {action.due_date}")

        suffix = f" ({', '.join(parts)})" if parts else ""
        lines.append(f"- [ ] {action.task}{suffix}")

    if not actions:
        lines.append("_No action items found._")

    lines.append("")
    return "\n".join(lines)


def format_actions_json(result: ParseResult) -> str:
    """Render parse result as JSON for downstream tooling."""

    return json.dumps(
        {
            "total_lines": result.total_lines,
            "candidate_lines": result.candidate_lines,
            "actions": [
                {
                    "task": action.task,
                    "owner": action.owner,
                    "due_date": action.due_date,
                }
                for action in result.actions
            ],
        },
        indent=2,
    )
