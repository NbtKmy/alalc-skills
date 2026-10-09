import pytest

from alalc_phase1.record import validate_record
from helpers import good_review, make_record, reviewed

RECORD = make_record("0001")  # decisions d1, d2, d3
PROPOSED = RECORD["trace"]["alalc_result"]["proposed_output"]


def check(human_review):
    return validate_record(reviewed(RECORD, human_review))


def test_accepted_review_is_valid():
    assert check(good_review())[0] == []


def test_corrected_review_is_valid():
    errors, _ = check(good_review(case_verdict="corrected", corrected_output=PROPOSED + "!"))
    assert errors == []


def test_override_with_partial_observation_is_valid():
    review = good_review(
        case_verdict="corrected",
        corrected_output=PROPOSED + "!",
        decision_overrides=[
            {
                "decision_id": "d1",
                "decision_correct": False,
                "corrected_after": "Dare ka",
                "observation": {"automation_class": "ai_judgment", "candidate_layer": "llm"},
                "comment": "context needed",
            }
        ],
        missed_issues=[{"target_text": "学校", "note": "reading check"}],
        comment="ok",
    )
    errors, warnings = check(review)
    assert errors == []
    assert [w for w in warnings if not w.startswith("trace:")] == []


def test_override_may_contain_only_a_decision_id():
    assert check(good_review(decision_overrides=[{"decision_id": "d2"}]))[0] == []


ERROR_CASES = [
    ("reviewer_empty", dict(reviewer=""), "reviewer"),
    ("reviewer_blank", dict(reviewer="   "), "reviewer"),
    ("reviewer_not_string", dict(reviewer=3), "reviewer"),
    ("reviewed_at_garbage", dict(reviewed_at="yesterday"), "reviewed_at"),
    ("reviewed_at_naive", dict(reviewed_at="2026-10-09T01:30:00"), "reviewed_at"),
    ("verdict_unknown", dict(case_verdict="maybe"), "case_verdict"),
    ("accepted_with_correction", dict(corrected_output="X"), "corrected_output"),
    ("corrected_without_output", dict(case_verdict="corrected", corrected_output=None), "corrected_output"),
    ("corrected_empty_output", dict(case_verdict="corrected", corrected_output=""), "corrected_output"),
    ("corrected_same_as_proposal", dict(case_verdict="corrected", corrected_output=PROPOSED), "corrected_output"),
    ("override_unknown_decision", dict(decision_overrides=[{"decision_id": "d99"}]), "d99"),
    ("override_duplicate", dict(decision_overrides=[{"decision_id": "d1"}, {"decision_id": "d1"}]), "duplicate"),
    ("override_without_id", dict(decision_overrides=[{"decision_correct": False}]), "decision_id"),
    ("override_not_object", dict(decision_overrides=["d1"]), "decision_overrides[0]"),
    ("override_correct_not_bool", dict(decision_overrides=[{"decision_id": "d1", "decision_correct": "no"}]), "decision_correct"),
    ("override_after_not_string", dict(decision_overrides=[{"decision_id": "d1", "corrected_after": 5}]), "corrected_after"),
    ("override_comment_not_string", dict(decision_overrides=[{"decision_id": "d1", "comment": 5}]), "comment"),
    ("override_observation_bad_enum", dict(decision_overrides=[{"decision_id": "d1", "observation": {"automation_class": "magic"}}]), "automation_class"),
    ("override_observation_not_object", dict(decision_overrides=[{"decision_id": "d1", "observation": "x"}]), "observation"),
    ("overrides_not_list", dict(decision_overrides={}), "decision_overrides"),
    ("missed_issue_without_note", dict(missed_issues=[{"target_text": "x"}]), "note"),
    ("missed_issues_not_list", dict(missed_issues="x"), "missed_issues"),
    ("comment_not_string", dict(comment=5), "comment"),
]


@pytest.mark.parametrize("name,changes,expected", ERROR_CASES, ids=[c[0] for c in ERROR_CASES])
def test_invalid_human_reviews_are_rejected(name, changes, expected):
    errors, _ = check(good_review(**changes))
    assert any(expected in e for e in errors), errors


@pytest.mark.parametrize("missing", ["reviewer", "reviewed_at", "case_verdict", "corrected_output",
                                     "decision_overrides", "missed_issues", "comment"])
def test_missing_required_keys_are_rejected(missing):
    review = good_review()
    del review[missing]
    errors, _ = check(review)
    assert any(missing in e for e in errors), errors


def test_human_review_must_be_an_object():
    record = reviewed(RECORD, "accepted")
    errors, _ = validate_record(record)
    assert any("human_review" in e for e in errors)


def test_accepted_with_a_disagreeing_override_warns():
    review = good_review(decision_overrides=[{"decision_id": "d1", "decision_correct": False}])
    errors, warnings = check(review)
    assert errors == []
    assert any("accepted" in w and "d1" in w for w in warnings)


def test_unknown_review_keys_warn():
    errors, warnings = check(good_review(extra="x"))
    assert errors == [] and any("extra" in w for w in warnings)
    errors, warnings = check(good_review(decision_overrides=[{"decision_id": "d1", "decison_correct": False}]))
    assert errors == [] and any("decison_correct" in w for w in warnings)


def test_history_entries_are_validated():
    record = reviewed(RECORD, good_review())
    record["human_review_history"] = [good_review(reviewer="earlier")]
    assert validate_record(record)[0] == []
    record["human_review_history"] = [good_review(case_verdict="maybe")]
    errors, _ = validate_record(record)
    assert any("human_review_history[0]" in e and "case_verdict" in e for e in errors)
    record["human_review_history"] = "x"
    assert any("human_review_history" in e for e in validate_record(record)[0])


def test_history_is_not_allowed_on_a_pending_record():
    record = make_record("0001")
    record["human_review_history"] = [good_review()]
    errors, _ = validate_record(record)
    assert any("human_review_history" in e for e in errors)
