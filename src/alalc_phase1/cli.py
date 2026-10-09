"""Command-line entry points. Each function takes argv and returns the process exit status."""

from __future__ import annotations

import argparse
import functools
import json
import os
import sys
from pathlib import Path

from alalc_phase1.jsonio import collect_json_files, read_json, write_json
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
