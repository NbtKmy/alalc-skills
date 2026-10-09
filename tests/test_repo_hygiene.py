import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "skills" / "alalc-romanize" / "rules"
RULES = sorted(RULES_DIR.glob("*.md"))
TEXT_SUFFIXES = {".md", ".py", ".toml", ".json", ".jsonl", ".txt"}
SKIP_DIRS = {".venv", ".git", ".pytest_cache", "__pycache__", ".superpowers"}


def tracked_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or set(path.relative_to(ROOT).parts) & SKIP_DIRS:
            continue
        if path.name == "uv.lock":
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in {".gitignore", "LICENSE"}:
            yield path


def test_there_are_thirteen_rule_files():
    assert len(RULES) == 13


@pytest.mark.parametrize("path", RULES, ids=lambda p: p.name)
def test_every_rule_file_opens_with_the_unofficial_restatement_notice(path):
    head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:15])
    assert "Unofficial restatement." in head
    assert "NOTICE.md" in head


def test_rule_files_exist_in_one_place_only():
    names = {p.name for p in RULES}
    for path in ROOT.rglob("*.md"):
        if set(path.relative_to(ROOT).parts) & SKIP_DIRS:
            continue
        if path.name in names:
            assert path.parent == RULES_DIR, f"rule file copied to {path.relative_to(ROOT)}"


def test_no_personal_information_or_environment_specific_paths():
    forbidden = [re.compile(p) for p in (r"/Users/", r"@hotmail", r"@gmail", r"/home/[a-z]")]
    this_file = Path(__file__).resolve()
    for path in tracked_text_files():
        if path.resolve() == this_file:
            continue  # this file spells out the forbidden patterns
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in forbidden:
            assert not pattern.search(text), f"{path.relative_to(ROOT)} matches {pattern.pattern}"


def test_the_retired_environment_variable_is_gone():
    this_file = Path(__file__).resolve()
    for path in tracked_text_files():
        if path.resolve() == this_file:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert "ROMANIZER_CORE_DIR" not in text, path.relative_to(ROOT)


def test_skills_do_not_call_python_directly_or_use_script_paths():
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        assert "python3 " not in text and "python <skill_dir>" not in text, skill
        assert "scripts/" not in text, skill


def test_every_command_a_skill_mentions_is_registered():
    scripts = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]
    names = {"alalc-romanize", "alalc-observe", "alalc-review", "alalc-skills", "alalc-romanization-trace"}
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        for command in set(re.findall(r"\balalc-[a-z-]+\b", skill.read_text(encoding="utf-8"))):
            if command in names:
                continue  # skill / project names, not commands
            assert command in scripts, f"{skill.parent.name} mentions unknown command {command}"
