from meet2action.formatter import format_actions_markdown
from meet2action.models import ActionItem


def test_format_actions_markdown_with_metadata() -> None:
    rendered = format_actions_markdown(
        [
            ActionItem(task="Draft kickoff agenda", owner="Alice", due_date="2026-03-20"),
            ActionItem(task="Follow up with legal", owner="Bob"),
        ]
    )

    assert "# Action Items" in rendered
    assert "- [ ] Draft kickoff agenda (owner: Alice, due: 2026-03-20)" in rendered
    assert "- [ ] Follow up with legal (owner: Bob)" in rendered


def test_format_actions_markdown_no_actions() -> None:
    rendered = format_actions_markdown([])
    assert "_No action items found._" in rendered
