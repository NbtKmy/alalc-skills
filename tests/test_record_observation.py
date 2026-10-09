import copy
import hashlib
import json

import pytest

from alalc_phase1.record import RECORD_VERSION, build_record, trace_sha256, validate_record
from helpers import load_trace, make_observation, make_record, observation_decision

SUFFIXES = ["0001", "0002", "0003", "0004", "0005", "0006"]


def test_trace_sha256_matches_the_spec_definition():
    expected = hashlib.sha256('{"a":[1,2],"b":"日本"}'.encode("utf-8")).hexdigest()
    assert trace_sha256({"b": "日本", "a": [1, 2]}) == expected


def test_trace_sha256_ignores_key_order():
    trace = load_trace("0001")
    assert trace_sha256(dict(reversed(list(trace.items())))) == trace_sha256(trace)


def test_build_record_is_pending_and_embeds_trace_unedited():
    trace = load_trace("0002")
    record = build_record(trace, make_observation(trace))
    assert record["record_version"] == RECORD_VERSION
    assert record["status"] == "pending" and record["human_review"] is None
    assert record["case_id"] == trace["case_id"]
    assert record["trace"] == trace
    assert record["trace_sha256"] == trace_sha256(trace)


@pytest.mark.parametrize("suffix", SUFFIXES)
def test_pending_records_for_every_example_validate(suffix):
    errors, _ = validate_record(make_record(suffix))
    assert errors == []


def test_zero_decision_case_has_an_empty_observation_and_is_valid():
    trace = load_trace("0003")
    assert trace["decisions"] == []
    record = build_record(trace, {"decisions": []})
    assert validate_record(record)[0] == []


def test_record_survives_a_json_round_trip_with_japanese_text():
    record = make_record("0001")
    reloaded = json.loads(json.dumps(record, ensure_ascii=False, indent=2))
    assert validate_record(reloaded)[0] == []
    assert reloaded["trace_sha256"] == trace_sha256(reloaded["trace"])


def _decision(record, **changes):
    record["observation"]["decisions"][0].update(changes)


ERROR_CASES = [
    ("bad_version", lambda r: r.update(record_version="x"), "record_version"),
    ("bad_status", lambda r: r.update(status="done"), "status"),
    ("pending_with_review", lambda r: r.update(human_review={"reviewer": "a"}), "human_review"),
    ("reviewed_without_review", lambda r: r.update(status="reviewed"), "human_review"),
    ("case_id_mismatch", lambda r: r.update(case_id="other"), "case_id"),
    ("trace_tampered", lambda r: r["trace"]["alalc_result"].update(proposed_output="Tampered"), "trace_sha256"),
    ("missing_decision", lambda r: r["observation"]["decisions"].pop(), "missing decision_id"),
    ("extra_decision", lambda r: r["observation"]["decisions"].append(observation_decision("d99")), "d99"),
    ("duplicate_decision", lambda r: r["observation"]["decisions"].append(copy.deepcopy(r["observation"]["decisions"][0])), "duplicate"),
    ("bad_class", lambda r: _decision(r, automation_class="magic"), "automation_class"),
    ("bad_layer", lambda r: _decision(r, candidate_layer="cloud"), "candidate_layer"),
    ("empty_required_information", lambda r: _decision(r, required_information=[]), "required_information"),
    ("blank_required_item", lambda r: _decision(r, required_information=["  "]), "required_information"),
    ("non_string_required_item", lambda r: _decision(r, required_information=[1]), "required_information"),
    ("bool_as_string", lambda r: _decision(r, core_information_sufficient="true"), "core_information_sufficient"),
    ("bool_as_int", lambda r: _decision(r, external_reference_needed=1), "external_reference_needed"),
    ("notes_not_string", lambda r: _decision(r, automation_notes=None), "automation_notes"),
    ("open_questions_not_list", lambda r: _decision(r, open_questions="x"), "open_questions"),
    ("open_questions_item_not_string", lambda r: _decision(r, open_questions=[3]), "open_questions"),
    ("missing_field", lambda r: r["observation"]["decisions"][0].pop("automation_notes"), "automation_notes"),
    ("decision_not_object", lambda r: r["observation"]["decisions"].__setitem__(0, "d1"), "observation.decisions[0]"),
    ("observation_not_object", lambda r: r.update(observation=[]), "observation"),
]


@pytest.mark.parametrize("name,mutate,expected", ERROR_CASES, ids=[c[0] for c in ERROR_CASES])
def test_invalid_records_are_rejected(name, mutate, expected):
    record = make_record("0001")
    mutate(record)
    errors, _ = validate_record(record)
    assert any(expected in e for e in errors), errors


@pytest.mark.parametrize("bad", [[], None, "x", {}, {"trace": {}}, {"trace": []}, {"trace": {}, "observation": {}}])
def test_malformed_records_report_errors_without_raising(bad):
    errors, _ = validate_record(bad)
    assert errors


def test_unknown_observation_key_is_only_a_warning():
    record = make_record("0004")
    _decision(record, automation_clas="x")
    errors, warnings = validate_record(record)
    assert errors == []
    assert any("automation_clas" in w for w in warnings)


def test_inconsistent_class_and_layer_warns_but_does_not_fail():
    record = make_record("0004")
    _decision(record, automation_class="deterministic", candidate_layer="llm",
              core_information_sufficient=True, external_reference_needed=False)
    errors, warnings = validate_record(record)
    assert errors == []
    assert any("candidate_layer" in w for w in warnings)


def test_deterministic_requires_core_sufficient_and_no_external_reference():
    record = make_record("0004")
    _decision(record, automation_class="deterministic", candidate_layer="core",
              core_information_sufficient=False, external_reference_needed=True)
    _, warnings = validate_record(record)
    assert any("core_information_sufficient" in w for w in warnings)
    assert any("external_reference_needed" in w for w in warnings)


def test_table_driven_with_external_reference_warns():
    record = make_record("0004")
    _decision(record, automation_class="table_driven", candidate_layer="lookup_table",
              external_reference_needed=True)
    assert any("external_reference_needed" in w for w in validate_record(record)[1])


def test_core_sufficient_but_non_core_layer_warns():
    record = make_record("0004")
    _decision(record, automation_class="ai_judgment", candidate_layer="llm",
              core_information_sufficient=True)
    assert any("core_information_sufficient" in w for w in validate_record(record)[1])


@pytest.mark.parametrize(
    "fields",
    [
        dict(automation_class="deterministic", candidate_layer="core", core_information_sufficient=True),
        dict(automation_class="deterministic", candidate_layer="alalc_rules", core_information_sufficient=True),
        dict(automation_class="table_driven", candidate_layer="lookup_table"),
        dict(automation_class="table_driven", candidate_layer="alalc_rules"),
        dict(automation_class="ai_judgment", candidate_layer="llm"),
        dict(automation_class="external_or_human", candidate_layer="human_authority", external_reference_needed=True),
    ],
)
def test_consistent_combinations_produce_no_warnings(fields):
    record = make_record("0004")
    _decision(record, **fields)
    errors, warnings = validate_record(record)
    assert errors == []
    assert [w for w in warnings if not w.startswith("trace:")] == []
