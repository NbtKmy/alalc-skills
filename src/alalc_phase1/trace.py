"""ALA-LC romanization trace: format constants, validation and assembly."""

from __future__ import annotations

import re
from typing import Any

TRACE_VERSION = "alalc-romanization-trace/0.1.0"
ACTIONS = {"changed", "verified_no_change", "variant_added", "lookup_required"}
RESULTS = {"applied", "considered_not_applied", "not_applicable"}
RULE_ID = re.compile(r"^ALA-LC-\d+(\.\d+)*$")


def validate(trace: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if trace.get("trace_version") != TRACE_VERSION:
        errors.append(f"trace_version != {TRACE_VERSION}")

    text = trace["input"]["text"]
    raw = trace["core_result"]["raw"]
    core_output = trace["core_result"]["output"]
    if raw.get("text") != text:
        errors.append("core_result.raw.text differs from input.text")
    if raw.get("romanized_text") != core_output:
        errors.append("core_result.output differs from core_result.raw.romanized_text")

    reading = trace["input"].get("item_supplied_reading")
    reading_raw = trace["core_result"].get("reading_raw")
    if reading and reading_raw is None:
        errors.append("item_supplied_reading is set but core_result.reading_raw is missing")
    if reading_raw is not None:
        if not reading:
            errors.append("core_result.reading_raw present without item_supplied_reading")
        elif reading_raw.get("text") != reading:
            errors.append("core_result.reading_raw.text differs from item_supplied_reading")

    alalc = trace["alalc_result"]
    proposed = alalc["proposed_output"]
    decisions = trace["decisions"]
    unresolved_refs = {u.get("ref") for u in trace.get("unresolved", [])}

    seen_ids: set[str] = set()
    running = core_output
    for d in decisions:
        did = d["decision_id"]
        if did in seen_ids:
            errors.append(f"{did}: duplicate decision_id")
        seen_ids.add(did)

        action = d["action"]
        if action not in ACTIONS:
            errors.append(f"{did}: unknown action {action!r}")

        target = d["target"]
        if text[target["start"] : target["end"]] != target["text"]:
            errors.append(f"{did}: target offsets do not match input text")

        evaluations = d["rule_evaluations"]
        for ev in evaluations:
            if not RULE_ID.match(ev["rule"]):
                errors.append(f"{did}: bad rule id {ev['rule']!r}")
            if ev["result"] not in RESULTS:
                errors.append(f"{did}: unknown rule result {ev['result']!r}")
        for cand in d.get("candidates", []):
            if not RULE_ID.match(cand["rule"]):
                errors.append(f"{did}: bad candidate rule id {cand['rule']!r}")

        for field in ("item_supplied_reading", "context_before", "context_after", "kind"):
            if f"input.{field}" in d.get("information_used", []) and not trace["input"].get(field):
                warnings.append(f"{did}: information_used cites input.{field} but it is empty")

        applied = [ev for ev in evaluations if ev["result"] == "applied"]
        if action == "changed":
            if not applied:
                errors.append(f"{did}: changed without an applied ALA-LC rule")
            if d["before"] not in running:
                errors.append(f"{did}: before {d['before']!r} not found in running output")
            else:
                running = running.replace(d["before"], d["after"], 1)
        elif action == "lookup_required":
            if d["after"] is not None:
                errors.append(f"{did}: lookup_required must have after=null")
            if did not in unresolved_refs:
                errors.append(f"{did}: lookup_required has no matching unresolved entry")
        elif action == "verified_no_change":
            if d["before"] != d["after"]:
                errors.append(f"{did}: verified_no_change but before != after")
            if not any(ev["result"] == "considered_not_applied" for ev in evaluations):
                warnings.append(
                    f"{did}: verified_no_change with no competing rule considered; "
                    "likely routine confirmation (SKILL.md section 5)"
                )

    if running != proposed:
        errors.append(
            f"delta accounting: core output plus changed decisions gives {running!r}, "
            f"proposed_output is {proposed!r}"
        )

    has_changed = any(d["action"] == "changed" for d in decisions)
    accepted = alalc["core_output_accepted_without_change"]
    if accepted != (proposed == core_output and not has_changed):
        errors.append("core_output_accepted_without_change is inconsistent")

    if proposed and not proposed[0].isupper() and proposed[0].isalpha():
        warnings.append("proposed_output does not start with a capital (project policy P1)")

    for v in alalc["variants"]:
        if v["output"] == proposed:
            errors.append("variant equals proposed_output")

    return errors, warnings


INPUT_DEFAULTS = {
    "kind": "unknown",
    "context_before": None,
    "context_after": None,
    "item_supplied_reading": None,
    "notes": None,
    "metadata": {},
}


def validate_safe(trace: Any) -> tuple[list[str], list[str]]:
    """validate(), but a malformed trace yields an error message instead of an exception."""
    if not isinstance(trace, dict):
        return ["trace is not a JSON object"], []
    try:
        return validate(trace)
    except (KeyError, TypeError, AttributeError, IndexError) as exc:
        return [f"malformed trace: {type(exc).__name__}: {exc}"], []


def build_trace(
    case: dict, raw: dict, judgment: dict, reading_raw: dict | None = None
) -> dict:
    """Assemble a trace. The core JSON is embedded verbatim as core_result.raw."""
    proposed = judgment["proposed_output"]
    decisions = judgment["decisions"]
    unchanged = proposed == raw["romanized_text"] and not any(
        d["action"] == "changed" for d in decisions
    )
    trace = {
        "trace_version": TRACE_VERSION,
        "case_id": case["id"],
        "input": {**INPUT_DEFAULTS, **{k: v for k, v in case.items() if k != "id"}},
        "core_result": {"output": raw["romanized_text"], "raw": raw},
        "alalc_result": {
            "proposed_output": proposed,
            "variants": judgment.get("variants", []),
            "core_output_accepted_without_change": unchanged,
        },
        "decisions": decisions,
        "unresolved": judgment.get("unresolved", []),
    }
    if reading_raw is not None:
        trace["core_result"]["reading_raw"] = reading_raw
    return trace
