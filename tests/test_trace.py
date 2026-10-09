import copy

import pytest

from alalc_phase1.trace import TRACE_VERSION, build_trace, validate, validate_safe
from helpers import load_json, load_trace, trace_paths

SUFFIXES = ["0001", "0002", "0003", "0004", "0005", "0006"]


@pytest.mark.parametrize("suffix", SUFFIXES)
def test_example_traces_have_no_errors(suffix):
    errors, _ = validate_safe(load_trace(suffix))
    assert errors == []


def test_example_batch_warnings_match_pre_migration_baseline():
    warnings = {p.name: validate_safe(load_json(p))[1] for p in trace_paths()}
    assert warnings["B20261009-002-0001.json"] == [
        "d1: information_used cites input.item_supplied_reading but it is empty"
    ]
    assert all(w == [] for name, w in warnings.items() if not name.endswith("0001.json"))


def test_tampered_proposed_output_fails_delta_accounting():
    trace = copy.deepcopy(load_trace("0001"))
    trace["alalc_result"]["proposed_output"] = "Tampered"
    errors, _ = validate(trace)
    assert any("delta accounting" in e for e in errors)


@pytest.mark.parametrize("bad", [{}, [], None, "text", {"trace_version": TRACE_VERSION}])
def test_validate_safe_reports_malformed_trace_without_raising(bad):
    errors, warnings = validate_safe(bad)
    assert errors and warnings == []


@pytest.mark.parametrize("suffix", SUFFIXES)
def test_build_trace_reproduces_example(suffix):
    trace = load_trace(suffix)
    case = {"id": trace["case_id"], **trace["input"]}
    raw = trace["core_result"]["raw"]
    judgment = {
        "proposed_output": trace["alalc_result"]["proposed_output"],
        "variants": trace["alalc_result"]["variants"],
        "decisions": trace["decisions"],
        "unresolved": trace["unresolved"],
    }
    rebuilt = build_trace(case, raw, judgment, trace["core_result"].get("reading_raw"))
    assert rebuilt == trace


@pytest.mark.parametrize("bad_id", [1, None, "", "   ", ["d1"]])
def test_non_string_or_blank_decision_id_is_an_error(bad_id):
    trace = copy.deepcopy(load_trace("0001"))
    trace["decisions"][0]["decision_id"] = bad_id
    errors, _ = validate_safe(trace)
    assert any("decision_id" in e for e in errors), errors


@pytest.mark.parametrize("bad_case_id", [1, None, "", "   ", "a/b", "a\\b"])
def test_case_id_must_be_a_plain_non_empty_string(bad_case_id):
    trace = copy.deepcopy(load_trace("0001"))
    trace["case_id"] = bad_case_id
    errors, _ = validate_safe(trace)
    assert any("case_id" in e for e in errors), errors
