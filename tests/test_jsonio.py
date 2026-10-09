import pytest

from alalc_phase1 import jsonio


def test_write_then_read_round_trips_japanese(tmp_path):
    path = tmp_path / "out" / "a.json"
    jsonio.write_json(path, {"text": "日本橋", "n": [1, 2]})
    assert jsonio.read_json(path) == {"text": "日本橋", "n": [1, 2]}
    assert "日本橋" in path.read_text(encoding="utf-8")  # ensure_ascii=False
    assert path.read_text(encoding="utf-8").endswith("\n")


def test_failed_replace_keeps_existing_file_and_leaves_no_tmp(tmp_path, monkeypatch):
    path = tmp_path / "a.json"
    jsonio.write_json(path, {"v": 1})
    before = path.read_bytes()

    def boom(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr("alalc_phase1.jsonio.os.replace", boom)
    with pytest.raises(OSError):
        jsonio.write_json(path, {"v": 2})
    monkeypatch.undo()

    assert path.read_bytes() == before
    assert list(tmp_path.glob("*.tmp")) == []


def test_collect_json_files_expands_directories_sorted(tmp_path):
    (tmp_path / "b.json").write_text("{}", encoding="utf-8")
    (tmp_path / "a.json").write_text("{}", encoding="utf-8")
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")
    single = tmp_path / "b.json"
    files = jsonio.collect_json_files([str(tmp_path), str(single)])
    assert [p.name for p in files] == ["a.json", "b.json", "b.json"]
