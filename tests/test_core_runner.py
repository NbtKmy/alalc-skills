import json
import os

import pytest

from alalc_phase1 import cli, core_runner
from helpers import load_trace


def test_missing_dictionary_path_is_an_error(monkeypatch, capsys):
    monkeypatch.delenv("UNIDIC_PATH", raising=False)
    monkeypatch.setenv("UNIDIC_VERSION", "1")
    assert cli.run_core(["--text", "x"]) == 1
    assert "UNIDIC_PATH" in capsys.readouterr().err


def test_missing_dictionary_version_is_an_error(monkeypatch, capsys):
    monkeypatch.setenv("UNIDIC_PATH", "/dict")
    monkeypatch.delenv("UNIDIC_VERSION", raising=False)
    assert cli.run_core(["--text", "x"]) == 1
    assert "UNIDIC_VERSION" in capsys.readouterr().err


def test_arguments_reach_the_core_and_json_is_printed(monkeypatch, capsys):
    calls = []

    def fake(text, path, version, name=None):
        calls.append((text, path, version, name))
        return {"text": text, "romanized_text": "X"}

    monkeypatch.setattr(core_runner, "run_core", fake)
    monkeypatch.setenv("UNIDIC_PATH", "/dict")
    monkeypatch.setenv("UNIDIC_VERSION", "9")
    monkeypatch.delenv("UNIDIC_NAME", raising=False)
    assert cli.run_core(["--text", "誰か"]) == 0
    assert calls == [("誰か", "/dict", "9", None)]
    assert json.loads(capsys.readouterr().out) == {"text": "誰か", "romanized_text": "X"}


@pytest.mark.skipif(
    not (os.environ.get("UNIDIC_PATH") and os.environ.get("UNIDIC_VERSION")),
    reason="UniDic is not configured (UNIDIC_PATH / UNIDIC_VERSION)",
)
def test_real_core_reproduces_the_example_baseline():
    trace = load_trace("0001")
    raw = core_runner.run_core(
        trace["input"]["text"],
        os.environ["UNIDIC_PATH"],
        os.environ["UNIDIC_VERSION"],
        os.environ.get("UNIDIC_NAME"),
    )
    assert raw == trace["core_result"]["raw"]


def test_core_failure_is_reported_as_an_error_not_a_traceback(monkeypatch, capsys):
    def boom(text, path, version, name=None):
        raise RuntimeError("Dictionary not found: /nonexistent")

    monkeypatch.setattr(core_runner, "run_core", boom)
    monkeypatch.setenv("UNIDIC_PATH", "/nonexistent")
    monkeypatch.setenv("UNIDIC_VERSION", "1")
    assert cli.run_core(["--text", "あ"]) == 1
    err = capsys.readouterr().err
    assert "error:" in err and "Dictionary not found" in err
