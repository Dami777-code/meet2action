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

    assert result.actions[2].task == "Send vendor shortlist"
    assert result.actions[2].owner is None
    assert result.actions[2].due_date == "Friday"


def test_parse_actions_extracts_owner_from_colon_and_at_prefix() -> None:
    text = """
Alice: review final deck by Monday.
@Bob prepare budget summary.
"""
    result = parse_actions(text)

    assert len(result.actions) == 2
    assert result.actions[0].owner == "Alice"
    assert result.actions[0].task == "Review final deck"
    assert result.actions[0].due_date == "Monday"

    assert result.actions[1].owner == "Bob"
    assert result.actions[1].task == "Prepare budget summary"


def test_parse_actions_reduces_false_positives_for_discussion_lines() -> None:
    text = """
We will discuss hiring plan tomorrow.
Discussion: review roadmap themes.
Status: project is on track.
"""
    result = parse_actions(text)

    assert result.actions == []


def test_parse_actions_due_date_guardrails_keep_invalid_dates_out() -> None:
    text = """
Alice to finalize report by 2026-3-7.
Alice to finalize report by 2026-02-30.
Alice to finalize report by 2026-03-07.
"""
    result = parse_actions(text)

    assert len(result.actions) == 3
    assert result.actions[0].due_date is None
    assert result.actions[1].due_date is None
    assert result.actions[2].due_date == "2026-03-07"




def test_parse_actions_due_date_guardrails_accept_real_leap_day_only() -> None:
    text = """
Alice to submit compliance report by 2024-02-29.
Alice to submit compliance report by 2025-02-29.
"""
    result = parse_actions(text)

    assert len(result.actions) == 2
    assert result.actions[0].due_date == "2024-02-29"
    assert result.actions[1].due_date is None


def test_parse_actions_is_conservative_for_non_action_lines() -> None:
    text = """
Attendees: Alice, Bob
Budget looked healthy.
Risks were reviewed.
"""
    result = parse_actions(text)

    assert result.candidate_lines == 0
    assert result.actions == []


def test_parse_actions_skips_generic_colon_labels() -> None:
    text = """
Topic: pricing
FYI: vendor replied
Background: Q2 plan
"""
    result = parse_actions(text)

    assert result.candidate_lines == 0
    assert result.actions == []


def test_parse_actions_keeps_obvious_owner_colon_actions() -> None:
    text = """
Alice: send updated report by Monday.
"""
    result = parse_actions(text)

    assert len(result.actions) == 1
    assert result.actions[0].owner == "Alice"
    assert result.actions[0].task == "Send updated report"
    assert result.actions[0].due_date == "Monday"
