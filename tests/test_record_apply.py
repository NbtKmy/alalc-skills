import copy
from datetime import datetime, timedelta, timezone

import pytest

from alalc_phase1.jsonio import write_json
from alalc_phase1.record import ReviewError, apply_review, list_pending, validate_record
from helpers import good_review, make_record, reviewed

NOW = datetime(2026, 10, 9, 1, 30, tzinfo=timezone(timedelta(hours=9)))
ACCEPTED = {"reviewer": "tester", "case_verdict": "accepted"}


def test_apply_review_marks_the_record_reviewed_without_touching_the_trace():
    record = make_record("0001")
    original = copy.deepcopy(record)
    result, warnings = apply_review(record, dict(ACCEPTED), now=NOW)
    assert record == original  # input untouched
    assert result["status"] == "reviewed"
    assert result["human_review"]["reviewed_at"] == "2026-10-09T01:30:00+09:00"
    assert result["human_review"]["reviewer"] == "tester"
    assert result["trace"] == original["trace"]
    assert result["trace_sha256"] == original["trace_sha256"]
    assert validate_record(result)[0] == []


def test_apply_review_fills_only_empty_defaults():
    result, _ = apply_review(make_record("0001"), dict(ACCEPTED), now=NOW)
    hr = result["human_review"]
    assert hr["corrected_output"] is None
    assert hr["decision_overrides"] == [] and hr["missed_issues"] == [] and hr["comment"] is None


def test_apply_review_uses_the_current_time_with_an_offset_by_default():
    result, _ = apply_review(make_record("0001"), dict(ACCEPTED))
    assert datetime.fromisoformat(result["human_review"]["reviewed_at"]).tzinfo is not None


def test_apply_review_keeps_the_reviewers_answers_verbatim():
    review = {
        "reviewer": "山田 太郎",
        "case_verdict": "corrected",
        "corrected_output": "Watakushi wa gakkō e ikimashita ta",
        "decision_overrides": [{"decision_id": "d1", "comment": "原文のまま"}],
        "missed_issues": [{"target_text": "学校", "note": "読み"}],
        "comment": "メモ",
    }
    result, _ = apply_review(make_record("0001"), copy.deepcopy(review), now=NOW)
    for key, value in review.items():
        assert result["human_review"][key] == value


def test_apply_review_rejects_reviewed_at_in_the_review():
    with pytest.raises(ReviewError, match="reviewed_at"):
        apply_review(make_record("0001"), {**ACCEPTED, "reviewed_at": "2026-01-01T00:00:00+00:00"}, now=NOW)


def test_apply_review_rejects_a_non_object_review():
    with pytest.raises(ReviewError):
        apply_review(make_record("0001"), ["accepted"], now=NOW)


def test_apply_review_surfaces_validation_errors():
    with pytest.raises(ReviewError, match="corrected_output"):
        apply_review(make_record("0001"), {**ACCEPTED, "corrected_output": "X"}, now=NOW)
    with pytest.raises(ReviewError, match="reviewer"):
        apply_review(make_record("0001"), {"reviewer": "  ", "case_verdict": "accepted"}, now=NOW)
    with pytest.raises(ReviewError, match="reviewer"):
        apply_review(make_record("0001"), {"case_verdict": "accepted"}, now=NOW)


def test_apply_review_rejects_a_tampered_record_before_anything_else():
    record = make_record("0001")
    record["trace"]["alalc_result"]["proposed_output"] = "Tampered"
    with pytest.raises(ReviewError, match="trace_sha256"):
        apply_review(record, dict(ACCEPTED), now=NOW)


def test_apply_review_returns_warnings():
    review = {**ACCEPTED, "decision_overrides": [{"decision_id": "d1", "decision_correct": False}]}
    _, warnings = apply_review(make_record("0004"), review, now=NOW)
    assert any("accepted" in w for w in warnings)


def test_reviewed_record_is_not_overwritten_without_replace():
    record = reviewed(make_record("0001"), good_review())
    with pytest.raises(ReviewError, match="--replace"):
        apply_review(record, dict(ACCEPTED), now=NOW)


def test_replace_moves_the_previous_review_into_history_oldest_first():
    first, _ = apply_review(make_record("0001"), {"reviewer": "first", "case_verdict": "accepted"}, now=NOW)
    second, _ = apply_review(first, {"reviewer": "second", "case_verdict": "accepted"}, replace=True,
                             now=NOW + timedelta(hours=1))
    third, _ = apply_review(second, {"reviewer": "third", "case_verdict": "accepted"}, replace=True,
                            now=NOW + timedelta(hours=2))
    assert third["human_review"]["reviewer"] == "third"
    assert [h["reviewer"] for h in third["human_review_history"]] == ["first", "second"]
    assert validate_record(third)[0] == []
    assert "human_review_history" not in first


def test_replace_on_a_pending_record_just_applies_the_review():
    result, _ = apply_review(make_record("0001"), dict(ACCEPTED), replace=True, now=NOW)
    assert result["status"] == "reviewed" and "human_review_history" not in result


def test_list_pending_returns_pending_records_in_case_id_order(tmp_path):
    write_json(tmp_path / "B-0002.json", make_record("0002"))
    write_json(tmp_path / "B-0001.json", make_record("0001"))
    write_json(tmp_path / "B-0003.json", reviewed(make_record("0003"), good_review()))
    pending, skipped = list_pending(tmp_path)
    assert [cid for cid, _ in pending] == ["B20261009-002-0001", "B20261009-002-0002"]
    assert [p.name for _, p in pending] == ["B-0001.json", "B-0002.json"]
    assert skipped == []


def test_list_pending_skips_unreadable_and_invalid_records_with_a_reason(tmp_path):
    (tmp_path / "junk.json").write_text("{not json", encoding="utf-8")
    tampered = make_record("0004")
    tampered["trace"]["alalc_result"]["proposed_output"] = "Tampered"
    write_json(tmp_path / "tampered.json", tampered)
    write_json(tmp_path / "ok.json", make_record("0001"))
    pending, skipped = list_pending(tmp_path)
    assert [p.name for _, p in pending] == ["ok.json"]
    reasons = {p.name: r for p, r in skipped}
    assert set(reasons) == {"junk.json", "tampered.json"}
    assert "trace_sha256" in reasons["tampered.json"]
