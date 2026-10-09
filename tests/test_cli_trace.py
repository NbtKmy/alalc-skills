import json

from alalc_phase1 import cli
from helpers import BATCH, load_trace


def test_validate_trace_ok_on_example_directory(capsys):
    rc = cli.validate_trace([str(BATCH / "romanized")])
    out = capsys.readouterr().out
    assert rc == 0
    assert "ok  B20261009-002-0001.json" in out
    assert "warn:  d1: information_used cites input.item_supplied_reading but it is empty" in out
    assert "FAIL" not in out


def test_validate_trace_fails_on_broken_trace(tmp_path, capsys):
    trace = load_trace("0001")
    trace["alalc_result"]["proposed_output"] = "Tampered"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(trace, ensure_ascii=False), encoding="utf-8")
    assert cli.validate_trace([str(bad)]) == 1
    out = capsys.readouterr().out
    assert "FAIL  bad.json" in out and "delta accounting" in out


def test_validate_trace_reports_unreadable_files_without_traceback(tmp_path, capsys):
    notjson = tmp_path / "x.json"
    notjson.write_text("{not json", encoding="utf-8")
    notobject = tmp_path / "y.json"
    notobject.write_text("[1, 2]", encoding="utf-8")
    missing = tmp_path / "missing.json"
    rc = cli.validate_trace([str(notjson), str(notobject), str(missing)])
    out = capsys.readouterr().out
    assert rc == 1
    assert out.count("FAIL") == 3


def _write_inputs(tmp_path, trace):
    case = {"id": trace["case_id"], **trace["input"]}
    judgment = {
        "proposed_output": trace["alalc_result"]["proposed_output"],
        "variants": trace["alalc_result"]["variants"],
        "decisions": trace["decisions"],
        "unresolved": trace["unresolved"],
    }
    files = {
        "case": tmp_path / "case.json",
        "raw": tmp_path / "raw.json",
        "judgment": tmp_path / "judgment.json",
    }
    files["case"].write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
    files["raw"].write_text(json.dumps(trace["core_result"]["raw"], ensure_ascii=False), encoding="utf-8")
    files["judgment"].write_text(json.dumps(judgment, ensure_ascii=False), encoding="utf-8")
    return files


def test_assemble_trace_writes_the_example_trace(tmp_path):
    trace = load_trace("0001")
    files = _write_inputs(tmp_path, trace)
    out = tmp_path / "out" / "t.json"
    rc = cli.assemble_trace(
        ["--case", str(files["case"]), "--core-raw", str(files["raw"]),
         "--judgment", str(files["judgment"]), "--out", str(out)]
    )
    assert rc == 0
    assert json.loads(out.read_text(encoding="utf-8")) == trace


def test_assemble_trace_with_item_supplied_reading(tmp_path):
    trace = load_trace("0005")
    files = _write_inputs(tmp_path, trace)
    reading = tmp_path / "reading.json"
    reading.write_text(json.dumps(trace["core_result"]["reading_raw"], ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "t.json"
    rc = cli.assemble_trace(
        ["--case", str(files["case"]), "--core-raw", str(files["raw"]),
         "--reading-raw", str(reading), "--judgment", str(files["judgment"]), "--out", str(out)]
    )
    assert rc == 0
    assert json.loads(out.read_text(encoding="utf-8")) == trace


def test_assemble_trace_refuses_invalid_trace_and_writes_nothing(tmp_path, capsys):
    trace = load_trace("0001")
    trace["alalc_result"]["proposed_output"] = "Tampered"
    files = _write_inputs(tmp_path, trace)
    out = tmp_path / "t.json"
    rc = cli.assemble_trace(
        ["--case", str(files["case"]), "--core-raw", str(files["raw"]),
         "--judgment", str(files["judgment"]), "--out", str(out)]
    )
    assert rc == 1
    assert not out.exists()
    assert "delta accounting" in capsys.readouterr().err


def test_assemble_trace_reports_malformed_judgment_without_traceback(tmp_path, capsys):
    trace = load_trace("0001")
    files = _write_inputs(tmp_path, trace)
    files["judgment"].write_text("{}", encoding="utf-8")  # no proposed_output / decisions
    out = tmp_path / "t.json"
    rc = cli.assemble_trace(
        ["--case", str(files["case"]), "--core-raw", str(files["raw"]),
         "--judgment", str(files["judgment"]), "--out", str(out)]
    )
    assert rc == 1 and not out.exists()
    assert "error:" in capsys.readouterr().err
