# alalc-skills

Claude Code (and OpenCode) skills for **ALA-LC Japanese romanization**, built to find out how much of the ALA-LC rules can be applied without AI.

| Skill | What it does |
|---|---|
| `alalc-romanize` | Runs `japanese-romanization-core` (MeCab + UniDic) first, keeps its result as the baseline, then applies the ALA-LC rules and writes an auditable trace per case |
| `alalc-observe` | For each decision in a trace, records how far it could be automated (deterministic / table-driven / AI judgment / external or human) |
| `alalc-review` | Walks a person through the pending records and saves their Human Review |

The code is a Python package (`alalc_phase1`) run with [uv](https://docs.astral.sh/uv/). The skills only hold the instructions; the deterministic work (validation, hashing, assembly) is done by commands.

> **The rule files are an unofficial restatement.** `skills/alalc-romanize/rules/` paraphrases the *ALA-LC Romanization Table: Japanese (2022)*. It is not the official table, the original always takes precedence, and it is not covered by the MIT license. See [NOTICE.md](NOTICE.md).

## Requirements

- [uv](https://docs.astral.sh/uv/) and Python 3.13 or later (uv can install it)
- A local UniDic-CWJ dictionary (not bundled; download it yourself, see [UniDic dictionary](#unidic-dictionary))
- Claude Code or OpenCode

## Install

```bash
git clone https://github.com/NbtKmy/alalc-skills.git
cd alalc-skills
uv sync
```

Make the three skills visible to your agent by copying or symlinking them:

```bash
mkdir -p ~/work/.claude/skills        # your working directory
ln -s "$PWD"/skills/* ~/work/.claude/skills/
```

Set these environment variables (for Claude Code, in the `env` block of `.claude/settings.local.json`):

```text
ALALC_HOME=/absolute/path/to/alalc-skills
UNIDIC_PATH=/absolute/path/to/unidic-cwj-...
UNIDIC_VERSION=...
UNIDIC_NAME=unidic-cwj        # optional
```

### UniDic dictionary

The core analyzes text with MeCab and a UniDic dictionary. `uv sync` installs MeCab itself (the `mecab-python3` wheel), but **not the dictionary**: UniDic is not bundled and nothing downloads it for you.

1. Download **UniDic-CWJ** (contemporary written Japanese) from NINJAL: <https://clrd.ninjal.ac.jp/unidic/>, and unzip it anywhere you like. Read its license first.
2. The unzipped folder (for example `unidic-cwj-202512`) is the dictionary. It contains files such as `dicrc`, `sys.dic` and `matrix.bin`.
3. Point the environment variables at **your** copy. The path differs for every user, so use an absolute path and do not use `~` (it is not expanded in `settings.local.json`):
   - `UNIDIC_PATH`: the unzipped folder, e.g. `/path/to/dictionaries/unidic-cwj-202512`
   - `UNIDIC_VERSION`: the version string of the dictionary, e.g. `202512` (the number in the folder name)
   - `UNIDIC_NAME`: optional label, e.g. `unidic-cwj`

   The values are recorded in every trace, so reviewers can see which dictionary produced a result. The project was developed with UniDic-CWJ 202512; other versions are untested.
4. Check the setup:

   ```bash
   uv run --project "$ALALC_HOME" alalc-run-core --text 日本橋
   ```

   It prints the core's raw JSON. If it prints `Missing UniDic path` or `core failed: DictionaryNotFoundError`, the variables are not set or the path is wrong.

Keep `.claude/settings.local.json` out of version control: it holds paths that are specific to your machine.

If an AI agent installed the skills for you, it should ask you for the dictionary folder instead of guessing, and it will not download UniDic on its own.

## Use

1. **Romanize one input.** Ask the agent: *"Romanize 誰か来ますか with alalc-romanize."* It runs the core, applies the rules and writes a trace.
2. **Romanize a batch.** Put one case per line in `phase1/batches/<batch_id>/input.jsonl` (see `examples/batch/input.jsonl`) and ask the agent to romanize the batch. Traces go to `romanized/<case_id>.json`.
3. **Observe.** Ask the agent to run `alalc-observe` on the batch. It writes `observed/<case_id>.json` with `status: pending`.
4. **Review.** Ask the agent to run `alalc-review`. It asks for your name once, then shows one case at a time and asks one question at a time. Your answers are saved with `status: reviewed`. You can stop any time.

Commands you can also run yourself (always through uv):

```bash
uv run --project "$ALALC_HOME" alalc-validate-trace romanized/
uv run --project "$ALALC_HOME" alalc-validate-record observed/
uv run --project "$ALALC_HOME" alalc-list-pending observed/
```

`examples/batch/` holds six sample traces; `uv run alalc-validate-trace examples/batch/romanized` checks them.

## Develop

```bash
uv sync
uv run pytest
```

`japanese-romanization-core` is pinned to a commit in `pyproject.toml` (a direct Git reference), so updating it means changing that commit and running `uv lock`. Because of this reference the package is not meant for PyPI as it is; use it from a clone.

## License

Code and original text: MIT (`LICENSE`). Rule files: not covered, see [NOTICE.md](NOTICE.md). Data you produce (`phase1/`) is not part of this repository.
