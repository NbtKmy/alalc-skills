"""Phase1Observation records: format, hashing, validation and assembly."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from alalc_phase1.trace import validate_safe

RECORD_VERSION = "alalc-phase1-observation/0.1.0"
STATUSES = ("pending", "reviewed")
AUTOMATION_CLASSES = ("deterministic", "table_driven", "ai_judgment", "external_or_human")
CANDIDATE_LAYERS = ("core", "alalc_rules", "lookup_table", "llm", "human_authority")
CASE_VERDICTS = ("accepted", "corrected")
OBSERVATION_FIELDS = (
    "automation_class",
    "candidate_layer",
    "required_information",
    "core_information_sufficient",
    "external_reference_needed",
    "automation_notes",
    "open_questions",
)

# Layers that usually go with each class (spec 4.5). A mismatch is a warning, not an error.
_LAYERS_FOR_CLASS = {
    "deterministic": ("core", "alalc_rules"),
    "table_driven": ("lookup_table", "alalc_rules"),
    "ai_judgment": ("llm",),
    "external_or_human": ("human_authority",),
}
_NON_CORE_LAYERS = ("lookup_table", "llm", "human_authority")


def trace_sha256(trace: dict) -> str:
    text = json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_record(trace: dict, observation: dict) -> dict:
    """Wrap a trace and an observation into a pending record. The trace is embedded unedited."""
    return {
        "record_version": RECORD_VERSION,
        "case_id": trace.get("case_id"),
        "status": "pending",
        "trace_sha256": trace_sha256(trace),
        "trace": trace,
        "observation": observation,
        "human_review": None,
    }


def _is_text_list(value: Any, *, non_empty: bool) -> bool:
    if not isinstance(value, list) or (non_empty and not value):
        return False
    return all(isinstance(v, str) and (v.strip() or not non_empty) for v in value)


def _check_observation_fields(
    obs: Any, where: str, *, partial: bool, extra_keys: tuple[str, ...] = ()
) -> tuple[list[str], list[str]]:
    if not isinstance(obs, dict):
        return [f"{where}: not an object"], []
    errors: list[str] = []
    warnings: list[str] = []
    for key in OBSERVATION_FIELDS:
        if key not in obs:
            if not partial:
                errors.append(f"{where}: missing {key}")
            continue
        value = obs[key]
        if key == "automation_class" and not (isinstance(value, str) and value in AUTOMATION_CLASSES):
            errors.append(f"{where}: automation_class must be one of {list(AUTOMATION_CLASSES)}, got {value!r}")
        elif key == "candidate_layer" and not (isinstance(value, str) and value in CANDIDATE_LAYERS):
            errors.append(f"{where}: candidate_layer must be one of {list(CANDIDATE_LAYERS)}, got {value!r}")
        elif key == "required_information" and not _is_text_list(value, non_empty=True):
            errors.append(f"{where}: required_information must be a non-empty list of non-blank strings")
        elif key in ("core_information_sufficient", "external_reference_needed") and not isinstance(value, bool):
            errors.append(f"{where}: {key} must be true or false, got {value!r}")
        elif key == "automation_notes" and not isinstance(value, str):
            errors.append(f"{where}: automation_notes must be a string")
        elif key == "open_questions" and not _is_text_list(value, non_empty=False):
            errors.append(f"{where}: open_questions must be a list of strings")
    for key in obs:
        if key not in OBSERVATION_FIELDS and key not in extra_keys:
            warnings.append(f"{where}: unknown key {key!r}")
    return errors, warnings


def _consistency_warnings(decision_id: str, d: dict) -> list[str]:
    warnings: list[str] = []
    cls, layer = d["automation_class"], d["candidate_layer"]
    expected = _LAYERS_FOR_CLASS[cls]
    if layer not in expected:
        warnings.append(
            f"{decision_id}: automation_class {cls} usually pairs with candidate_layer "
            f"{' / '.join(expected)}, got {layer}"
        )
    if cls == "deterministic":
        if not d["core_information_sufficient"]:
            warnings.append(f"{decision_id}: deterministic but core_information_sufficient is false")
        if d["external_reference_needed"]:
            warnings.append(f"{decision_id}: deterministic but external_reference_needed is true")
    if cls == "table_driven" and d["external_reference_needed"]:
        warnings.append(f"{decision_id}: table_driven but external_reference_needed is true")
    if d["core_information_sufficient"] and layer in _NON_CORE_LAYERS:
        warnings.append(
            f"{decision_id}: core_information_sufficient is true but candidate_layer is {layer}"
        )
    return warnings


def validate_record(record: Any) -> tuple[list[str], list[str]]:
    if not isinstance(record, dict):
        return ["record is not a JSON object"], []
    errors: list[str] = []
    warnings: list[str] = []

    if record.get("record_version") != RECORD_VERSION:
        errors.append(f"record_version != {RECORD_VERSION}")

    status = record.get("status")
    human_review = record.get("human_review")
    if status not in STATUSES:
        errors.append(f"status must be one of {list(STATUSES)}, got {status!r}")
    elif status == "pending" and human_review is not None:
        errors.append("human_review must be null when status is pending")
    elif status == "reviewed" and human_review is None:
        errors.append("human_review is required when status is reviewed")

    trace = record.get("trace")
    if not isinstance(trace, dict):
        errors.append("trace is missing or not an object")
        return errors, warnings

    if record.get("trace_sha256") != trace_sha256(trace):
        errors.append("trace_sha256 does not match trace (the trace was modified)")
    trace_errors, trace_warnings = validate_safe(trace)
    errors += [f"trace: {m}" for m in trace_errors]
    warnings += [f"trace: {m}" for m in trace_warnings]

    if record.get("case_id") != trace.get("case_id"):
        errors.append(
            f"case_id {record.get('case_id')!r} does not match trace case_id {trace.get('case_id')!r}"
        )

    trace_decisions = trace.get("decisions")
    trace_ids = [
        d["decision_id"]
        for d in (trace_decisions if isinstance(trace_decisions, list) else [])
        if isinstance(d, dict) and isinstance(d.get("decision_id"), str)
    ]

    observation = record.get("observation")
    if not isinstance(observation, dict) or not isinstance(observation.get("decisions"), list):
        errors.append("observation must be an object with a decisions list")
        return errors, warnings
    for key in observation:
        if key != "decisions":
            warnings.append(f"observation: unknown key {key!r}")

    seen: list[str] = []
    for i, d in enumerate(observation["decisions"]):
        where = f"observation.decisions[{i}]"
        if not isinstance(d, dict):
            errors.append(f"{where}: not an object")
            continue
        did = d.get("decision_id")
        if not isinstance(did, str):
            errors.append(f"{where}: missing decision_id")
            continue
        where = f"{where} ({did})"
        if did in seen:
            errors.append(f"{where}: duplicate decision_id {did}")
        seen.append(did)
        field_errors, field_warnings = _check_observation_fields(
            d, where, partial=False, extra_keys=("decision_id",)
        )
        errors += field_errors
        warnings += field_warnings
        if not field_errors:
            warnings += _consistency_warnings(did, d)

    for did in trace_ids:
        if did not in seen:
            errors.append(f"observation is missing decision_id {did} from the trace")
    for did in sorted(set(seen) - set(trace_ids)):
        errors.append(f"observation has decision_id {did} that is not in the trace")

    return errors, warnings
