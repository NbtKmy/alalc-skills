"""Phase1Observation records: format, hashing, validation and assembly."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from alalc_phase1.jsonio import read_json
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


_REVIEW_KEYS = (
    "reviewer",
    "reviewed_at",
    "case_verdict",
    "corrected_output",
    "decision_overrides",
    "missed_issues",
    "comment",
)
_OVERRIDE_KEYS = ("decision_id", "decision_correct", "corrected_after", "observation", "comment")


def _is_text_or_none(value: Any) -> bool:
    return value is None or isinstance(value, str)


def _check_override(o: Any, where: str, trace_ids: list[str], verdict: Any) -> tuple[list[str], list[str]]:
    if not isinstance(o, dict):
        return [f"{where}: not an object"], []
    errors: list[str] = []
    warnings: list[str] = []
    did = o.get("decision_id")
    if not isinstance(did, str):
        errors.append(f"{where}: missing decision_id")
    elif did not in trace_ids:
        errors.append(f"{where}: decision_id {did} is not in the trace")
    if "decision_correct" in o and not isinstance(o["decision_correct"], bool):
        errors.append(f"{where}: decision_correct must be true or false")
    if "corrected_after" in o and not _is_text_or_none(o["corrected_after"]):
        errors.append(f"{where}: corrected_after must be a string or null")
    if "comment" in o and not _is_text_or_none(o["comment"]):
        errors.append(f"{where}: comment must be a string or null")
    if "observation" in o:
        obs_errors, obs_warnings = _check_observation_fields(
            o["observation"], f"{where}.observation", partial=True
        )
        errors += obs_errors
        warnings += obs_warnings
    for key in o:
        if key not in _OVERRIDE_KEYS:
            warnings.append(f"{where}: unknown key {key!r}")
    if verdict == "accepted" and o.get("decision_correct") is False:
        warnings.append(f"{where}: case_verdict is accepted but {did} is marked decision_correct=false")
    return errors, warnings


def _check_human_review(hr: Any, where: str, trace: dict, trace_ids: list[str]) -> tuple[list[str], list[str]]:
    if not isinstance(hr, dict):
        return [f"{where}: not an object"], []
    errors: list[str] = []
    warnings: list[str] = []
    for key in _REVIEW_KEYS:
        if key not in hr:
            errors.append(f"{where}: missing {key}")
    for key in hr:
        if key not in _REVIEW_KEYS:
            warnings.append(f"{where}: unknown key {key!r}")

    reviewer = hr.get("reviewer")
    if "reviewer" in hr and not (isinstance(reviewer, str) and reviewer.strip()):
        errors.append(f"{where}: reviewer must be a non-blank string")

    if "reviewed_at" in hr:
        try:
            parsed = datetime.fromisoformat(hr["reviewed_at"])
        except (TypeError, ValueError):
            errors.append(f"{where}: reviewed_at must be an ISO 8601 timestamp, got {hr['reviewed_at']!r}")
        else:
            if parsed.tzinfo is None:
                errors.append(f"{where}: reviewed_at must include a UTC offset, got {hr['reviewed_at']!r}")

    verdict = hr.get("case_verdict")
    if "case_verdict" in hr and verdict not in CASE_VERDICTS:
        errors.append(f"{where}: case_verdict must be one of {list(CASE_VERDICTS)}, got {verdict!r}")
    if "corrected_output" in hr:
        corrected = hr["corrected_output"]
        alalc_result = trace.get("alalc_result")
        proposed = alalc_result.get("proposed_output") if isinstance(alalc_result, dict) else None
        if verdict == "accepted" and corrected is not None:
            errors.append(f"{where}: corrected_output must be null when case_verdict is accepted")
        elif verdict == "corrected":
            if not (isinstance(corrected, str) and corrected.strip()):
                errors.append(f"{where}: corrected_output is required when case_verdict is corrected")
            elif corrected.strip() == (proposed.strip() if isinstance(proposed, str) else proposed):
                errors.append(
                    f"{where}: corrected_output must differ from alalc_result.proposed_output "
                    "(leading and trailing whitespace does not count)"
                )

    if "decision_overrides" in hr:
        overrides = hr["decision_overrides"]
        if not isinstance(overrides, list):
            errors.append(f"{where}: decision_overrides must be a list")
        else:
            seen: list[str] = []
            for i, o in enumerate(overrides):
                o_errors, o_warnings = _check_override(o, f"{where}.decision_overrides[{i}]", trace_ids, verdict)
                errors += o_errors
                warnings += o_warnings
                did = o.get("decision_id") if isinstance(o, dict) else None
                if isinstance(did, str):
                    if did in seen:
                        errors.append(f"{where}.decision_overrides[{i}]: duplicate decision_id {did}")
                    seen.append(did)

    if "missed_issues" in hr:
        issues = hr["missed_issues"]
        if not isinstance(issues, list):
            errors.append(f"{where}: missed_issues must be a list")
        else:
            for i, issue in enumerate(issues):
                if not (
                    isinstance(issue, dict)
                    and isinstance(issue.get("target_text"), str)
                    and isinstance(issue.get("note"), str)
                ):
                    errors.append(f"{where}.missed_issues[{i}]: needs string target_text and note")

    if "comment" in hr and not _is_text_or_none(hr["comment"]):
        errors.append(f"{where}: comment must be a string or null")
    return errors, warnings


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

    if status == "reviewed" and human_review is not None:
        r_errors, r_warnings = _check_human_review(human_review, "human_review", trace, trace_ids)
        errors += r_errors
        warnings += r_warnings

    if "human_review_history" in record:
        history = record["human_review_history"]
        if status != "reviewed":
            errors.append("human_review_history is only allowed when status is reviewed")
        if not isinstance(history, list):
            errors.append("human_review_history must be a list")
        else:
            for i, past in enumerate(history):
                h_errors, h_warnings = _check_human_review(
                    past, f"human_review_history[{i}]", trace, trace_ids
                )
                errors += h_errors
                warnings += h_warnings

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


class ReviewError(ValueError):
    """The review could not be applied. The message holds one problem per line."""


def apply_review(
    record: dict,
    review: dict,
    *,
    replace: bool = False,
    now: datetime | None = None,
) -> tuple[dict, list[str]]:
    """Return a new reviewed record and its warnings. The input record is not modified."""
    if not isinstance(review, dict):
        raise ReviewError("review is not a JSON object")
    if "reviewed_at" in review:
        raise ReviewError("review must not contain reviewed_at; it is set automatically")

    errors, _ = validate_record(record)
    if errors:
        raise ReviewError("\n".join(errors))

    updated = copy.deepcopy(record)
    if updated["status"] == "reviewed":
        if not replace:
            raise ReviewError("record is already reviewed; use --replace to re-review it")
        updated.setdefault("human_review_history", []).append(updated["human_review"])

    when = (now or datetime.now().astimezone()).isoformat(timespec="seconds")
    human_review = {
        "reviewer": review.get("reviewer"),
        "reviewed_at": when,
        "case_verdict": review.get("case_verdict"),
        "corrected_output": None,
        "decision_overrides": [],
        "missed_issues": [],
        "comment": None,
    }
    human_review.update({k: v for k, v in review.items() if k not in ("reviewer", "case_verdict")})
    updated["human_review"] = human_review
    updated["status"] = "reviewed"

    errors, warnings = validate_record(updated)
    if errors:
        raise ReviewError("\n".join(errors))
    return updated, warnings


def list_pending(directory: Path) -> tuple[list[tuple[str, Path]], list[tuple[Path, str]]]:
    """Pending records under directory in case_id order (a repeated case_id is skipped), plus (path, reason) for skipped files."""
    pending: list[tuple[str, Path]] = []
    skipped: list[tuple[Path, str]] = []
    first_seen: dict[str, Path] = {}
    for path in sorted(Path(directory).glob("*.json")):
        try:
            record = read_json(path)
        except (OSError, ValueError) as exc:
            skipped.append((path, f"cannot read: {exc}"))
            continue
        errors, _ = validate_record(record)
        if errors:
            skipped.append((path, errors[0]))
            continue
        case_id = record["case_id"]
        if case_id in first_seen:
            skipped.append((path, f"duplicate case_id {case_id} (first seen in {first_seen[case_id].name})"))
            continue
        first_seen[case_id] = path
        if record["status"] == "pending":
            pending.append((case_id, path))
    pending.sort(key=lambda item: item[0])
    return pending, skipped
