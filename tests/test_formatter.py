import json

from meet2action.formatter import format_actions_json, format_actions_markdown
from meet2action.models import ActionItem, ParseResult


def test_format_actions_markdown_with_metadata() -> None:
    rendered = format_actions_markdown(
        [
            ActionItem(task="Draft kickoff agenda", owner="Alice", due_date="2099-01-15"),
            ActionItem(task="Follow up with legal", owner="Bob"),
        ]
    )

    assert "# Action Items" in rendered
    assert "- [ ] Draft kickoff agenda (owner: Alice, due: 2099-01-15)" in rendered
    assert "- [ ] Follow up with legal (owner: Bob)" in rendered


def test_format_actions_markdown_no_actions() -> None:
    rendered = format_actions_markdown([])
    assert "_No action items found._" in rendered


def test_format_actions_json_shape() -> None:
    result = ParseResult(
        actions=[
            ActionItem(task="Draft kickoff agenda", owner="Alice", due_date="2099-01-15"),
            ActionItem(task="Follow up with legal", owner="Bob"),
        ],
        total_lines=5,
        candidate_lines=3,
    )
    rendered = format_actions_json(result)
    data = json.loads(rendered)

    assert data["total_lines"] == 5
    assert data["candidate_lines"] == 3
    assert len(data["actions"]) == 2
    assert data["actions"][0] == {
        "task": "Draft kickoff agenda",
        "owner": "Alice",
        "due_date": "2099-01-15",
    }
    assert data["actions"][1] == {"task": "Follow up with legal", "owner": "Bob", "due_date": None}


def test_format_actions_json_no_actions() -> None:
    result = ParseResult(actions=[], total_lines=2, candidate_lines=0)
    data = json.loads(format_actions_json(result))

    assert data["actions"] == []
    assert data["total_lines"] == 2
    assert data["candidate_lines"] == 0
