# alalc-skills

**ALA-LC 日本語字訳**のための Claude Code（および OpenCode）用スキル集です。ALA-LC の規則のうち、AI を使わずにどこまで適用できるかを調べることが目的です。

| スキル | 内容 |
|---|---|
| `alalc-romanize` | まず `japanese-romanization-core`（MeCab + UniDic）を実行して結果を基準として保存し、そのうえで ALA-LC の規則を適用して、ケースごとに検証可能な trace を作ります |
| `alalc-observe` | trace の各 decision について、AI なしでどこまで自動化できるか（決定的 / 表引き / AI 判断 / 外部資料・人手）を記録します |
| `alalc-review` | 未レビューのレコードを 1 件ずつ提示し、人によるレビュー（Human Review）を保存します |

実装は Python パッケージ（`alalc_phase1`）で、[uv](https://docs.astral.sh/uv/) で実行します。スキルには手順だけを置き、検証・ハッシュ・組み立てなどの決まった処理はコマンドが行います。

> **`rules/` は非公式の要約です。** `skills/alalc-romanize/rules/` は *ALA-LC Romanization Table: Japanese (2022)* を運用上の範囲で言い換えたもので、公式の字訳表ではありません。常に原文が優先され、MIT ライセンスの対象外です。詳しくは [NOTICE.md](NOTICE.md) を参照してください。

## 必要なもの

- [uv](https://docs.astral.sh/uv/) と Python 3.13 以上（Python は uv が入れられます）
- ローカルの UniDic-CWJ 辞書（同梱していません。各自で入手してください）
- Claude Code または OpenCode

## 導入

```bash
git clone https://github.com/NbtKmy/alalc-skills.git
cd alalc-skills
uv sync
```

3 つのスキルをエージェントから見えるようにします（コピーでも symlink でも構いません）。

```bash
mkdir -p ~/work/.claude/skills        # 作業用ディレクトリ
ln -s "$PWD"/skills/* ~/work/.claude/skills/
```

環境変数を設定します（Claude Code では `.claude/settings.local.json` の `env` に書けます）。

```text
ALALC_HOME=/absolute/path/to/alalc-skills
UNIDIC_PATH=/absolute/path/to/unidic-cwj-...
UNIDIC_VERSION=...
UNIDIC_NAME=unidic-cwj        # 任意
```

## 使い方

1. **1 件を字訳する。** エージェントに「alalc-romanize で 誰か来ますか を字訳して」と頼みます。core を実行し、規則を適用して trace を書きます。
2. **バッチで字訳する。** `phase1/batches/<batch_id>/input.jsonl` に 1 行 1 ケースで入力を書き（`examples/batch/input.jsonl` を参照）、バッチの字訳を頼みます。trace は `romanized/<case_id>.json` に出ます。
3. **observe する。** `alalc-observe` をバッチに対して頼みます。`status: pending` の `observed/<case_id>.json` ができます。
4. **review する。** `alalc-review` を頼みます。最初に名前を 1 回だけ聞かれ、その後は 1 件ずつ、1 問ずつ質問されます。回答は `status: reviewed` で保存されます。途中でやめても構いません。

自分で実行できるコマンド（必ず uv 経由）:

```bash
uv run --project "$ALALC_HOME" alalc-validate-trace romanized/
uv run --project "$ALALC_HOME" alalc-validate-record observed/
uv run --project "$ALALC_HOME" alalc-list-pending observed/
```

`examples/batch/` に 6 件のサンプル trace があります。`uv run alalc-validate-trace examples/batch/romanized` で検証できます。

## 開発

```bash
uv sync
uv run pytest
```

## ライセンス

コードと独自の文章: MIT（`LICENSE`）。`rules/`: 対象外（[NOTICE.md](NOTICE.md) を参照）。利用者が作るデータ（`phase1/`）はこのリポジトリに含まれません。
