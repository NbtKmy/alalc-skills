"""Command-line entry points. Each function takes argv and returns the process exit status."""

from __future__ import annotations

import argparse
import functools
import json
import os
import sys
from pathlib import Path

from alalc_phase1.jsonio import collect_json_files, read_json, write_json
from alalc_phase1.record import (
    ReviewError,
    apply_review as apply_review_to_record,
    build_record,
    list_pending as list_pending_records,
    validate_record,
)
from alalc_phase1.trace import build_trace, validate_safe


class CliError(Exception):
    """A user-facing failure: printed as 'error: <message>', exit status 1."""


def _command(func):
    @functools.wraps(func)
    def wrapper(argv: list[str] | None = None) -> int:
        try:
            return func(argv)
        except (CliError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    return wrapper


def _load_json(path):
    try:
        return read_json(Path(path))
    except (OSError, ValueError) as exc:
        raise CliError(f"cannot read {path}: {exc}") from exc


def _validate_files(paths: list[str], validate) -> int:
    failed = 0
    for path in collect_json_files(paths):
        try:
            errors, warnings = validate(read_json(path))
        except (OSError, ValueError) as exc:
            errors, warnings = [f"cannot read: {exc}"], []
        print(f"{'FAIL' if errors else 'ok'}  {path.name}")
        for msg in errors:
            print(f"    error: {msg}")
        for msg in warnings:
            print(f"    warn:  {msg}")
        failed += bool(errors)
    return 1 if failed else 0


@_command
def validate_trace(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alalc-validate-trace",
        description="Validate ALA-LC romanization traces against the quality gates.",
    )
    parser.add_argument("paths", nargs="+", help="Trace JSON files or directories")
    args = parser.parse_args(argv)
    return _validate_files(args.paths, validate_safe)


@_command
def assemble_trace(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alalc-assemble-trace",
        description="Assemble and validate a trace from a case, the raw core JSON and the AI judgment.",
    )
    parser.add_argument("--case", required=True, help="Case JSON file (id, text, optional metadata)")
    parser.add_argument("--core-raw", required=True, help="Raw JSON printed by alalc-run-core")
    parser.add_argument(
        "--reading-raw",
        help="Raw JSON of alalc-run-core on item_supplied_reading (required when the case has one)",
    )
    parser.add_argument("--judgment", required=True, help="AI judgment JSON file")
    parser.add_argument("--out", required=True, help="Trace output path")
    args = parser.parse_args(argv)

    case = _load_json(args.case)
    raw = _load_json(args.core_raw)
    judgment = _load_json(args.judgment)
    reading_raw = _load_json(args.reading_raw) if args.reading_raw else None
    try:
        trace = build_trace(case, raw, judgment, reading_raw)
    except (KeyError, TypeError, AttributeError) as exc:
        raise CliError(f"malformed input: {type(exc).__name__}: {exc}") from exc

    errors, warnings = validate_safe(trace)
    for msg in warnings:
        print(f"warn:  {msg}", file=sys.stderr)
    if errors:
        for msg in errors:
            print(f"error: {msg}", file=sys.stderr)
        return 1

    out = Path(args.out)
    write_json(out, trace)
    print(f"wrote {out}")
    return 0


@_command
def run_core(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alalc-run-core",
        description="Run japanese-romanization-core for one input and print its raw JSON.",
    )
    parser.add_argument("--text", required=True, help="Exact Japanese input text")
    parser.add_argument(
        "--dictionary-path",
        default=os.environ.get("UNIDIC_PATH"),
        help="UniDic dictionary path (or set UNIDIC_PATH)",
    )
    parser.add_argument(
        "--dictionary-version",
        default=os.environ.get("UNIDIC_VERSION"),
        help="UniDic dictionary version (or set UNIDIC_VERSION)",
    )
    parser.add_argument(
        "--dictionary-name",
        default=os.environ.get("UNIDIC_NAME"),
        help="Optional dictionary name, e.g. unidic-cwj (or set UNIDIC_NAME)",
    )
    args = parser.parse_args(argv)
    if not args.dictionary_path:
        raise CliError("Missing UniDic path: use --dictionary-path or UNIDIC_PATH")
    if not args.dictionary_version:
        raise CliError("Missing UniDic version: use --dictionary-version or UNIDIC_VERSION")

    from alalc_phase1 import core_runner  # needs MeCab, so imported only when this command runs

    result = core_runner.run_core(
        args.text, args.dictionary_path, args.dictionary_version, args.dictionary_name
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _print_messages(errors: list[str], warnings: list[str]) -> None:
    for msg in warnings:
        print(f"warn:  {msg}", file=sys.stderr)
    for msg in errors:
        print(f"error: {msg}", file=sys.stderr)


@_command
def assemble_observation(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alalc-assemble-observation",
        description="Embed a trace and an observation into a pending Phase1Observation record.",
    )
    parser.add_argument("--trace", required=True, help="Trace JSON (romanized/<case_id>.json)")
    parser.add_argument("--observation", required=True, help='JSON of the form {"decisions": [...]}')
    parser.add_argument("--out", required=True, help="Record output path (observed/<case_id>.json)")
    args = parser.parse_args(argv)

    trace = _load_json(args.trace)
    observation = _load_json(args.observation)

    trace_errors, _ = validate_safe(trace)
    if trace_errors:
        _print_messages([f"trace: {m}" for m in trace_errors], [])
        return 1

    record = build_record(trace, observation)
    errors, warnings = validate_record(record)
    _print_messages(errors, warnings)
    if errors:
        return 1

    out = Path(args.out)
    if out.stem != record["case_id"]:
        raise CliError(f"output file name {out.name} must be {record['case_id']}.json (the case_id)")
    if out.exists():
        existing = _load_json(out)
        if isinstance(existing, dict) and existing.get("status") == "reviewed":
            raise CliError(f"{out} is already reviewed; refusing to overwrite it")
    write_json(out, record)
    print(f"wrote {out}")
    return 0


@_command
def validate_record_files(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alalc-validate-record", description="Validate Phase1Observation records."
    )
    parser.add_argument("paths", nargs="+", help="Record JSON files or directories")
    args = parser.parse_args(argv)
    return _validate_files(args.paths, validate_record)


@_command
def list_pending(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alalc-list-pending",
        description="List pending records as '<case_id><TAB><path>' in case_id order.",
    )
    parser.add_argument("observed_dir", help="Directory of observed/<case_id>.json records")
    args = parser.parse_args(argv)
    directory = Path(args.observed_dir)
    if not directory.is_dir():
        raise CliError(f"{directory} is not a directory")
    pending, skipped = list_pending_records(directory)
    for path, reason in skipped:
        print(f"skip: {path}: {reason}", file=sys.stderr)
    for case_id, path in pending:
        print(f"{case_id}\t{path}")
    return 0


@_command
def apply_review(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alalc-apply-review",
        description="Add a human review to a record, validate it and save it.",
    )
    parser.add_argument("--record", required=True, help="Record JSON (observed/<case_id>.json)")
    parser.add_argument("--review", required=True, help="Review JSON (human_review without reviewed_at)")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Re-review an already reviewed record; the previous review moves to human_review_history",
    )
    args = parser.parse_args(argv)

    record = _load_json(args.record)
    review = _load_json(args.review)
    try:
        updated, warnings = apply_review_to_record(record, review, replace=args.replace)
    except ReviewError as exc:
        _print_messages(str(exc).splitlines(), [])
        return 1
    _print_messages([], warnings)
    write_json(Path(args.record), updated)
    print(f"wrote {args.record}")
    return 0
