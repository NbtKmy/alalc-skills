import json

import pytest

from alalc_phase1 import cli
from alalc_phase1.record import validate_record
from helpers import load_json, make_observation, trace_paths


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def observe_all(tmp_path):
    observed = tmp_path / "observed"
    for trace_path in trace_paths():
        trace = load_json(trace_path)
        obs = write(tmp_path / "observation.json", make_observation(trace))
        rc = cli.assemble_observation(
            ["--trace", str(trace_path), "--observation", str(obs), "--out", str(observed / trace_path.name)]
        )
        assert rc == 0, trace_path.name
    return observed


def pending_paths(observed, capsys):
    capsys.readouterr()
    assert cli.list_pending([str(observed)]) == 0
    return [line.split("\t")[1] for line in capsys.readouterr().out.strip().splitlines() if line]


def test_observe_validate_review_revalidate_over_the_example_batch(tmp_path, capsys):
    assert len(trace_paths()) == 6
    observed = observe_all(tmp_path)
    assert cli.validate_record_files([str(observed)]) == 0

    paths = pending_paths(observed, capsys)
    assert len(paths) == 6

    review = write(tmp_path / "review.json", {"reviewer": "tester", "case_verdict": "accepted"})
    for path in paths:
        assert cli.apply_review(["--record", path, "--review", str(review)]) == 0

    assert pending_paths(observed, capsys) == []
    assert cli.validate_record_files([str(observed)]) == 0
    for trace_path in trace_paths():
        record = load_json(observed / trace_path.name)
        assert record["status"] == "reviewed"
        assert record["trace"] == load_json(trace_path)  # never edited by observe or review


def test_review_can_be_interrupted_and_resumed(tmp_path, capsys):
    observed = observe_all(tmp_path)
    review = write(tmp_path / "review.json", {"reviewer": "tester", "case_verdict": "accepted"})
    first = pending_paths(observed, capsys)[0]
    assert cli.apply_review(["--record", first, "--review", str(review)]) == 0
    remaining = pending_paths(observed, capsys)
    assert len(remaining) == 5 and first not in remaining


@pytest.fixture
def one_case(tmp_path):
    """Return (trace_path, observation_dict, out_path) for the first example case."""
    trace_path = trace_paths()[0]
    trace = load_json(trace_path)
    return trace_path, make_observation(trace), tmp_path / "observed" / trace_path.name


def run_assemble(tmp_path, trace_path, observation, out):
    obs = write(tmp_path / "observation.json", observation)
    return cli.assemble_observation(["--trace", str(trace_path), "--observation", str(obs), "--out", str(out)])


def test_failure_decision_id_missing(tmp_path, one_case):
    trace_path, observation, out = one_case
    observation["decisions"].pop()
    assert run_assemble(tmp_path, trace_path, observation, out) != 0 and not out.exists()


def test_failure_enum_value_wrong(tmp_path, one_case):
    trace_path, observation, out = one_case
    observation["decisions"][0]["candidate_layer"] = "somewhere"
    assert run_assemble(tmp_path, trace_path, observation, out) != 0 and not out.exists()


def test_failure_trace_modified_after_observation(tmp_path, one_case, capsys):
    trace_path, observation, out = one_case
    assert run_assemble(tmp_path, trace_path, observation, out) == 0
    record = load_json(out)
    record["trace"]["input"]["text"] = "改変"
    write(out, record)
    assert cli.validate_record_files([str(out)]) != 0
    review = write(tmp_path / "review.json", {"reviewer": "t", "case_verdict": "accepted"})
    assert cli.apply_review(["--record", str(out), "--review", str(review)]) != 0
    assert "trace_sha256" in capsys.readouterr().err


def test_failure_overwriting_a_reviewed_record(tmp_path, one_case):
    trace_path, observation, out = one_case
    assert run_assemble(tmp_path, trace_path, observation, out) == 0
    review = write(tmp_path / "review.json", {"reviewer": "t", "case_verdict": "accepted"})
    assert cli.apply_review(["--record", str(out), "--review", str(review)]) == 0
    before = out.read_bytes()
    assert run_assemble(tmp_path, trace_path, observation, out) != 0
    assert out.read_bytes() == before


def test_failure_accepted_with_corrected_output(tmp_path, one_case):
    trace_path, observation, out = one_case
    assert run_assemble(tmp_path, trace_path, observation, out) == 0
    review = write(tmp_path / "review.json",
                   {"reviewer": "t", "case_verdict": "accepted", "corrected_output": "X"})
    assert cli.apply_review(["--record", str(out), "--review", str(review)]) != 0
    assert load_json(out)["status"] == "pending"


def test_warning_deterministic_with_llm_layer(tmp_path, one_case, capsys):
    trace_path, observation, out = one_case
    observation["decisions"][0].update(automation_class="deterministic", candidate_layer="llm")
    assert run_assemble(tmp_path, trace_path, observation, out) == 0
    err = capsys.readouterr().err
    assert "warn:" in err and "candidate_layer" in err
    assert validate_record(load_json(out))[0] == []
