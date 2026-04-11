from meet2action.parser import parse_actions


def test_parse_actions_extracts_owner_and_due_when_obvious() -> None:
    text = """
- Alice to draft kickoff agenda by 2099-01-15.
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
    assert result.actions[0].due_date == "2099-01-15"

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
Alice to finalize report by 2099-3-7.
Alice to finalize report by 2099-02-30.
Alice to finalize report by 2099-03-07.
"""
    result = parse_actions(text)

    assert len(result.actions) == 3
    assert result.actions[0].due_date is None
    assert result.actions[1].due_date is None
    assert result.actions[2].due_date == "2099-03-07"


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


def test_parse_actions_multi_owner_and_syntax() -> None:
    text = """
Alice and Bob to review the deck.
Alice and Bob will finalize the budget.
"""
    result = parse_actions(text)

    assert len(result.actions) == 2
    assert result.actions[0].owner == "Alice, Bob"
    assert result.actions[0].task == "Review the deck"
    assert result.actions[1].owner == "Alice, Bob"
    assert result.actions[1].task == "Finalize the budget"


def test_parse_actions_multi_owner_csv_syntax() -> None:
    text = """
Alice, Bob to send the report.
Alice, Bob, Carol to prepare slides.
"""
    result = parse_actions(text)

    assert len(result.actions) == 2
    assert result.actions[0].owner == "Alice, Bob"
    assert result.actions[0].task == "Send the report"
    assert result.actions[1].owner == "Alice, Bob, Carol"
    assert result.actions[1].task == "Prepare slides"


def test_parse_actions_single_owner_unaffected_by_multi_owner_patterns() -> None:
    text = """
Alice to draft kickoff agenda.
Bob will follow up with legal.
"""
    result = parse_actions(text)

    assert len(result.actions) == 2
    assert result.actions[0].owner == "Alice"
    assert result.actions[1].owner == "Bob"


def test_parse_actions_we_will_with_action_verb_is_kept() -> None:
    # Lines starting with "we will" + a recognised action verb pass the
    # candidate filter (unlike "we will discuss…" which is suppressed).
    # "We" is a pronoun so owner is None; the verb-stripped remainder becomes
    # the task, preserving clean task text and due date extraction.
    text = """
We will send the invites by Monday.
We will review the proposals by Friday.
"""
    result = parse_actions(text)

    assert len(result.actions) == 2
    assert result.actions[0].owner is None
    assert result.actions[0].task == "Send the invites"
    assert result.actions[0].due_date == "Monday"
    assert result.actions[1].owner is None
    assert result.actions[1].task == "Review the proposals"
    assert result.actions[1].due_date == "Friday"


def test_parse_actions_pronoun_owner_is_not_extracted() -> None:
    # Pronouns matched by the will/to patterns must not appear as owners.
    text = """
They will prepare the slides.
He will finalize the budget by Thursday.
She to send the summary.
"""
    result = parse_actions(text)

    assert len(result.actions) == 3
    for action in result.actions:
        assert action.owner is None


def test_parse_actions_multi_owner_with_due_date() -> None:
    text = """
Alice and Bob to finalize the report by 2099-04-15.
"""
    result = parse_actions(text)

    assert len(result.actions) == 1
    assert result.actions[0].owner == "Alice, Bob"
    assert result.actions[0].task == "Finalize the report"
    assert result.actions[0].due_date == "2099-04-15"


def test_parse_actions_non_proper_name_colon_label_with_action_remainder_is_kept() -> None:
    # Label is not a proper single name and not in the blocklist, but remainder
    # looks like an action task — line should be extracted.
    text = """
Q3 Update: review the budget by Friday.
"""
    result = parse_actions(text)

    assert len(result.actions) == 1
    assert result.actions[0].due_date == "Friday"


def test_parse_actions_non_proper_name_colon_label_with_non_action_remainder_is_dropped() -> None:
    # Label is not a proper single name and not in the blocklist, but remainder
    # does not look like an action task — line should be suppressed.
    text = """
Q3 Update: budget looks healthy.
"""
    result = parse_actions(text)

    assert result.candidate_lines == 0
    assert result.actions == []


def test_parse_actions_we_will_draft_and_update_are_kept() -> None:
    # "draft" and "update" were missing from the we-will allowlist, causing
    # false negatives for these common meeting-note patterns.
    text = """
We will draft the proposal by Friday.
We will update the timeline.
"""
    result = parse_actions(text)

    assert len(result.actions) == 2
    assert result.actions[0].owner is None
    assert result.actions[0].task == "Draft the proposal"
    assert result.actions[0].due_date == "Friday"
    assert result.actions[1].owner is None
    assert result.actions[1].task == "Update the timeline"
    assert result.actions[1].due_date is None


def test_parse_actions_at_prefix_without_task_hint_extracts_no_owner() -> None:
    # @Name whose remainder lacks a recognised task-hint verb: owner is not
    # extracted and the full raw line becomes the task text.
    text = """
@Bob remind Carol about the retro.
"""
    result = parse_actions(text)

    assert len(result.actions) == 1
    assert result.actions[0].owner is None
    assert "@Bob" in result.actions[0].task
