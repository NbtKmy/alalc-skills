import json

import pytest

from alalc_phase1 import cli
from alalc_phase1.record import validate_record
from helpers import BATCH, good_review, load_json, load_trace, make_observation, make_record, reviewed

TRACE_0001 = BATCH / "romanized" / "B20261009-002-0001.json"
CASE_0001 = "B20261009-002-0001"


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def assemble(tmp_path, observation=None, trace_path=TRACE_0001, out=None):
    observation = observation if observation is not None else make_observation(load_trace("0001"))
    obs = write(tmp_path / "observation.json", observation)
    out = out or tmp_path / "observed" / f"{CASE_0001}.json"
    rc = cli.assemble_observation(["--trace", str(trace_path), "--observation", str(obs), "--out", str(out)])
    return rc, out


def test_assemble_observation_writes_a_valid_pending_record(tmp_path):
    rc, out = assemble(tmp_path)
    assert rc == 0
    record = load_json(out)
    assert validate_record(record)[0] == []
    assert record["status"] == "pending"
    assert record["trace"] == load_trace("0001")  # embedded unedited


def test_assemble_observation_prints_warnings_but_writes(tmp_path, capsys):
    observation = make_observation(load_trace("0001"))
    observation["decisions"][0].update(automation_class="deterministic", candidate_layer="llm")
    rc, out = assemble(tmp_path, observation)
    assert rc == 0 and out.exists()
    assert "warn:" in capsys.readouterr().err


def test_assemble_observation_refuses_an_invalid_observation(tmp_path, capsys):
    observation = make_observation(load_trace("0001"))
    observation["decisions"][0]["automation_class"] = "magic"
    rc, out = assemble(tmp_path, observation)
    assert rc == 1 and not out.exists()
    assert "automation_class" in capsys.readouterr().err


def test_assemble_observation_refuses_a_missing_decision(tmp_path, capsys):
    observation = make_observation(load_trace("0001"))
    observation["decisions"].pop()
    rc, out = assemble(tmp_path, observation)
    assert rc == 1 and not out.exists()
    assert "missing decision_id" in capsys.readouterr().err


def test_assemble_observation_refuses_an_invalid_trace(tmp_path, capsys):
    trace = load_trace("0001")
    trace["alalc_result"]["proposed_output"] = "Tampered"
    bad = write(tmp_path / "bad_trace.json", trace)
    rc, out = assemble(tmp_path, trace_path=bad)
    assert rc == 1 and not out.exists()
    assert "delta accounting" in capsys.readouterr().err


@pytest.mark.parametrize("content", ["{not json", "[]", "null"])
def test_assemble_observation_reports_unreadable_or_wrong_shape_inputs(tmp_path, capsys, content):
    obs = tmp_path / "observation.json"
    obs.write_text(content, encoding="utf-8")
    out = tmp_path / "observed" / f"{CASE_0001}.json"
    rc = cli.assemble_observation(["--trace", str(TRACE_0001), "--observation", str(obs), "--out", str(out)])
    assert rc == 1 and not out.exists()
    assert "error:" in capsys.readouterr().err


def test_assemble_observation_reports_a_missing_file(tmp_path, capsys):
    out = tmp_path / "observed" / f"{CASE_0001}.json"
    rc = cli.assemble_observation(["--trace", str(tmp_path / "nope.json"),
                                   "--observation", str(tmp_path / "nope2.json"), "--out", str(out)])
    assert rc == 1
    assert "cannot read" in capsys.readouterr().err


def test_assemble_observation_refuses_an_output_name_that_differs_from_case_id(tmp_path, capsys):
    rc, out = assemble(tmp_path, out=tmp_path / "observed" / "other.json")
    assert rc == 1 and not out.exists()
    assert "case_id" in capsys.readouterr().err


def test_assemble_observation_overwrites_pending_but_not_reviewed(tmp_path, capsys):
    rc, out = assemble(tmp_path)
    assert rc == 0
    assert assemble(tmp_path)[0] == 0  # pending can be regenerated

    write(out, reviewed(load_json(out), good_review()))
    before = out.read_bytes()
    rc, _ = assemble(tmp_path)
    assert rc == 1
    assert out.read_bytes() == before
    assert "reviewed" in capsys.readouterr().err


def test_assemble_observation_refuses_to_overwrite_an_unreadable_existing_file(tmp_path):
    out = tmp_path / "observed" / f"{CASE_0001}.json"
    out.parent.mkdir(parents=True)
    out.write_text("{broken", encoding="utf-8")
    rc, _ = assemble(tmp_path, out=out)
    assert rc == 1
    assert out.read_text(encoding="utf-8") == "{broken"


def test_validate_record_files_reports_ok_and_fail(tmp_path, capsys):
    write(tmp_path / "a.json", make_record("0001"))
    tampered = make_record("0004")
    tampered["trace"]["alalc_result"]["proposed_output"] = "Tampered"
    write(tmp_path / "b.json", tampered)
    assert cli.validate_record_files([str(tmp_path / "a.json")]) == 0
    assert cli.validate_record_files([str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "ok  a.json" in out and "FAIL  b.json" in out and "trace_sha256" in out


def test_list_pending_prints_case_id_and_path_and_reports_skips(tmp_path, capsys):
    write(tmp_path / "b.json", make_record("0002"))
    write(tmp_path / "a.json", make_record("0001"))
    write(tmp_path / "done.json", reviewed(make_record("0003"), good_review()))
    (tmp_path / "junk.json").write_text("{", encoding="utf-8")
    assert cli.list_pending([str(tmp_path)]) == 0
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines == [f"B20261009-002-0001\t{tmp_path / 'a.json'}", f"B20261009-002-0002\t{tmp_path / 'b.json'}"]
    assert "skip:" in captured.err and "junk.json" in captured.err


def test_list_pending_requires_an_existing_directory(tmp_path, capsys):
    assert cli.list_pending([str(tmp_path / "missing")]) == 1
    assert "error:" in capsys.readouterr().err


def review_file(tmp_path, review):
    return write(tmp_path / "review.json", review)


def test_apply_review_updates_the_record_in_place(tmp_path, capsys):
    rc, out = assemble(tmp_path)
    review = review_file(tmp_path, {"reviewer": "tester", "case_verdict": "accepted"})
    assert cli.apply_review(["--record", str(out), "--review", str(review)]) == 0
    record = load_json(out)
    assert record["status"] == "reviewed" and record["human_review"]["reviewer"] == "tester"
    assert validate_record(record)[0] == []
    assert record["trace"] == load_trace("0001")


def test_apply_review_refuses_a_reviewed_record_without_replace(tmp_path, capsys):
    _, out = assemble(tmp_path)
    review = review_file(tmp_path, {"reviewer": "first", "case_verdict": "accepted"})
    assert cli.apply_review(["--record", str(out), "--review", str(review)]) == 0
    before = out.read_bytes()
    review = review_file(tmp_path, {"reviewer": "second", "case_verdict": "accepted"})
    assert cli.apply_review(["--record", str(out), "--review", str(review)]) == 1
    assert out.read_bytes() == before
    assert "--replace" in capsys.readouterr().err


def test_apply_review_replace_keeps_history(tmp_path):
    _, out = assemble(tmp_path)
    for name in ("first", "second"):
        review = review_file(tmp_path, {"reviewer": name, "case_verdict": "accepted"})
        args = ["--record", str(out), "--review", str(review)]
        assert cli.apply_review(args + (["--replace"] if name == "second" else [])) == 0
    record = load_json(out)
    assert record["human_review"]["reviewer"] == "second"
    assert [h["reviewer"] for h in record["human_review_history"]] == ["first"]


def test_apply_review_with_an_invalid_review_leaves_the_record_unchanged(tmp_path, capsys):
    _, out = assemble(tmp_path)
    before = out.read_bytes()
    for bad in (
        {"reviewer": "t", "case_verdict": "accepted", "corrected_output": "X"},
        {"reviewer": "  ", "case_verdict": "accepted"},
        {"reviewer": "t", "case_verdict": "corrected"},
    ):
        review = review_file(tmp_path, bad)
        assert cli.apply_review(["--record", str(out), "--review", str(review)]) == 1
        assert out.read_bytes() == before
    assert "error:" in capsys.readouterr().err


def test_apply_review_aborts_when_the_embedded_trace_was_modified(tmp_path, capsys):
    _, out = assemble(tmp_path)
    record = load_json(out)
    record["trace"]["alalc_result"]["proposed_output"] = "Tampered"
    write(out, record)
    before = out.read_bytes()
    review = review_file(tmp_path, {"reviewer": "t", "case_verdict": "accepted"})
    assert cli.apply_review(["--record", str(out), "--review", str(review)]) == 1
    assert out.read_bytes() == before
    assert "trace_sha256" in capsys.readouterr().err


def test_apply_review_reports_unreadable_files(tmp_path, capsys):
    review = review_file(tmp_path, {"reviewer": "t", "case_verdict": "accepted"})
    assert cli.apply_review(["--record", str(tmp_path / "missing.json"), "--review", str(review)]) == 1
    assert "cannot read" in capsys.readouterr().err
