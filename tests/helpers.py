"""Shared test helpers. The example batch under examples/batch is the fixture source."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / "examples" / "batch"


def trace_paths() -> list[Path]:
    return sorted((BATCH / "romanized").glob("*.json"))


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_trace(suffix: str) -> dict:
    """Load an example trace by case suffix, e.g. '0001'."""
    return load_json(BATCH / "romanized" / f"B20261009-002-{suffix}.json")
