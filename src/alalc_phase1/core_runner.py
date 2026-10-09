"""Run japanese-romanization-core for one input string and return its raw JSON result.

This performs no ALA-LC logic. Its output is the immutable Phase 1 baseline.
"""

from __future__ import annotations

from pathlib import Path

from romanizer_core import (
    DictionaryConfig,
    MeCabAnalyzer,
    MeCabAnalyzerConfig,
    Romanizer,
    romanization_to_dict,
)


def run_core(
    text: str,
    dictionary_path: str | Path,
    dictionary_version: str,
    dictionary_name: str | None = None,
) -> dict:
    kwargs = {"path": Path(dictionary_path), "version": dictionary_version}
    if dictionary_name:
        kwargs["name"] = dictionary_name
    analyzer = MeCabAnalyzer(MeCabAnalyzerConfig(dictionary=DictionaryConfig(**kwargs)))
    romanizer = Romanizer.modified_hepburn(analyzer)
    return romanization_to_dict(romanizer.romanize(text))
