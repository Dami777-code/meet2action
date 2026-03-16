from .models import ActionItem


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
