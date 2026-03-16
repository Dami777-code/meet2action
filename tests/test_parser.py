from meet2action.parser import parse_actions


def test_parse_actions_extracts_owner_and_due_when_obvious() -> None:
    text = """
- Alice to draft kickoff agenda by 2026-03-20.
Bob will follow up with legal.
Please send vendor shortlist by Friday.
Discussion: budget risks.
"""
    result = parse_actions(text)

    assert result.total_lines == 5
    assert result.candidate_lines == 3
    assert len(result.actions) == 3

    assert result.actions[0].task == "Draft kickoff agenda"
    assert result.actions[0].owner == "Alice"
    assert result.actions[0].due_date == "2026-03-20"

    assert result.actions[1].task == "Follow up with legal"
    assert result.actions[1].owner == "Bob"
    assert result.actions[1].due_date is None

    assert result.actions[2].task == "Please send vendor shortlist"
    assert result.actions[2].owner is None
    assert result.actions[2].due_date == "Friday"


def test_parse_actions_is_conservative_for_non_action_lines() -> None:
    text = """
Attendees: Alice, Bob
Budget looked healthy.
Risks were reviewed.
"""
    result = parse_actions(text)

    assert result.candidate_lines == 0
    assert result.actions == []
