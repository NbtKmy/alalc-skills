"""JSON file helpers shared by the trace and record commands."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _reject_constant(name: str) -> None:
    raise ValueError(f"non-finite number {name} is not allowed")


def read_json(path: Path) -> Any:
    """Parse a JSON file. NaN/Infinity and lone surrogates (which cannot be saved as UTF-8) raise ValueError."""
    obj = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return obj


def write_json(path: Path, obj: Any) -> None:
    """Write JSON atomically: a failure leaves any existing file untouched."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def collect_json_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in map(Path, paths):
        files.extend(sorted(p.glob("*.json")) if p.is_dir() else [p])
    return files
