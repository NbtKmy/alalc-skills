---
name: alalc-romanize
description: Run japanese-romanization-core with MeCab + UniDic first, preserve its result as the immutable baseline, then apply the project's ALA-LC Japanese Romanization Table (2022) rule files with AI judgment. Produce an auditable per-case romanization trace for Phase 1. Use for one Japanese input or a batch before alalc-observe and human review.
compatibility: Claude Code and OpenCode. Requires uv, a clone of the alalc-skills repository (ALALC_HOME), a local UniDic dictionary, and the rule files in rules/.
metadata:
  project: japanese-romanization
  phase: "1"
  ruleset: "ALA-LC Japanese Romanization Table 2022"
---

# ALA-LC Romanize — Phase 1

## Purpose

This skill performs the **romanization stage only** of the Phase 1 workflow.

For every input case:

1. Run `japanese-romanization-core` first with MeCab + UniDic.
2. Preserve the complete core result as the baseline.
3. Compare the original Japanese text and the core result against the ALA-LC rule files in `rules/`.
4. Apply ALA-LC-specific changes or confirmations with explicit rule references.
5. Emit an auditable **ALA-LC romanization trace** for the later `alalc-observe` skill.

The core result is evidence and baseline data. It is **not automatically the final ALA-LC result**.

This skill must not perform Human Review and must not decide which parts should be automated in Phase 2. Those belong to later stages.

## Non-negotiable pipeline

Always use this order:

```text
Japanese input
    ↓
japanese-romanization-core + MeCab + UniDic
    ↓
immutable core baseline
    ↓
ALA-LC rule evaluation + AI judgment
    ↓
ALA-LC proposal + decision trace
    ↓
alalc-observe
    ↓
Human Review
```

**Never romanize the Japanese text directly with the language model before running `japanese-romanization-core`.**

Do not replace the core output with a model-generated reconstruction. Do not silently normalize the core result before preserving it.

---

# 1. Required files and environment

The skill directory contains `SKILL.md` and the rule files:

```text
alalc-romanize/
├── SKILL.md
└── rules/
    ├── 00_scope_and_principles.md
    ├── 01_reading_selection.md
    ├── 02_vowels_and_boundaries.md
    ├── 03_capitalization.md
    ├── 04_punctuation.md
    ├── 05_romanization_symbols.md
    ├── 06_word_division_basics.md
    ├── 07_prefixes_suffixes.md
    ├── 08_loanwords.md
    ├── 09_verbs_adjectives_particles.md
    ├── 10_proper_names.md
    ├── 11_geographic_names.md
    └── 12_numerals.md
```

All code lives in the `alalc-skills` repository and is run with `uv`. Every command below is run as `uv run --project "$ALALC_HOME" <command>`:

- `alalc-run-core` — Stage A: raw core JSON for one input
- `alalc-assemble-trace` — build and validate a trace from case, core raw and AI judgment
- `alalc-validate-trace` — check traces against the quality gates

The environment must provide:

- `uv`
- a local UniDic dictionary (this skill never downloads or replaces one)
- the `alalc-skills` clone, with `uv sync` already run

Required environment variables:

```text
ALALC_HOME=/absolute/path/to/alalc-skills        # clone of the alalc-skills repository
UNIDIC_PATH=/absolute/path/to/unidic-cwj-...
UNIDIC_VERSION=...
UNIDIC_NAME=unidic-cwj        # optional
```

`japanese-romanization-core` and MeCab come from the `alalc-skills` project environment; this skill ships no Python environment of its own.

If any required variable is unset, or the dictionary cannot be located, stop before ALA-LC reasoning and ask the user to configure it. Do not guess paths.

Record the actual dictionary version in downstream run metadata.

---

# 2. Accepted input

## 2.1 Single case

A user may supply plain Japanese text:

```text
誰か来ますか
```

Treat it internally as a case with at least:

```json
{
  "text": "誰か来ますか",
  "kind": "unknown",
  "context_before": null,
  "context_after": null,
  "item_supplied_reading": null,
  "notes": null,
  "metadata": {}
}
```

If the user supplies bibliographic type, surrounding context, item-supplied reading, or notes, preserve them. Do not discard contextual metadata merely because the core library does not consume it.

## 2.2 Batch

For a batch, prefer JSONL with one independent case per line:

```jsonl
{"id":"001","text":"誰か来ますか","kind":"sentence"}
{"id":"002","text":"日本永代蔵","kind":"work_title"}
{"id":"003","text":"東京都民","kind":"unknown"}
```

A plain list may be accepted and normalized to independent cases.

For batches of roughly 10–50 inputs:

- process each case independently;
- run the core separately for each case;
- do not copy a reading or interpretation from one case into another unless the batch metadata explicitly establishes shared context;
- produce one trace record per input case;
- an error in one case must not silently alter or skip the others.

---

# 3. Stage A — run `japanese-romanization-core`

Use the library as the mandatory first-pass analyzer and romanizer.

The current public API uses the following pattern:

```python
from pathlib import Path
from romanizer_core import (
    DictionaryConfig,
    MeCabAnalyzer,
    MeCabAnalyzerConfig,
    Romanizer,
    romanization_to_dict,
)

analyzer = MeCabAnalyzer(
    MeCabAnalyzerConfig(
        dictionary=DictionaryConfig(
            path=Path(UNIDIC_PATH),
            version=UNIDIC_VERSION,
        )
    )
)
romanizer = Romanizer.modified_hepburn(analyzer)
result = romanizer.romanize(text)
raw = romanization_to_dict(result)
```

Always invoke the core through `alalc-run-core` so Claude Code and OpenCode use the same path. The command prints the raw `romanization_to_dict()` JSON to stdout:

```bash
uv run --project "$ALALC_HOME" alalc-run-core --text "誰か来ますか"
```

Run one invocation per case; never batch several inputs into one `--text`.

## Core baseline requirements

For every case, preserve at least:

- exact input text;
- `romanized_text`;
- `json_schema_version`;
- analyzer metadata;
- UniDic dictionary metadata;
- token offsets;
- token surfaces;
- lemma and reading fields;
- POS and conjugation information;
- per-token romanization and its provenance.

Store the complete `romanization_to_dict()` result without model edits as `core_result.raw` in the later Phase 1 record.

The language model may inspect this structure, but it must not rewrite it.

## Item-supplied reading

When a case has `item_supplied_reading`, run the core **twice**, each as its own `alalc-run-core` invocation:

1. on `text` → the normal baseline, stored as `core_result.raw`;
2. on the `item_supplied_reading` string (kana) → stored unedited as `core_result.reading_raw` (pass it to `alalc-assemble-trace` with `--reading-raw`).

The item reading takes precedence (rule precedence 1). Use `reading_raw` as the evidence for the romanization of that reading; the proposal's delta is still counted against `core_result.raw`. Do not hand-romanize the kana. Cases without `item_supplied_reading` have no `reading_raw`.

---

# 4. Stage B — establish ALA-LC rule context

Read `rules/00_scope_and_principles.md` for every case.

Use its precedence rules, especially:

1. item-supplied reading;
2. specific ALA-LC exception;
3. specific rule for the expression class;
4. general ALA-LC rule;
5. contextual/reference-source judgment;
6. supported variants.

Then load every additional rule file relevant to the case. Multiple files may apply to a single input.

## Rule routing guide

| Issue or feature | Rule file |
|---|---|
| reading choice, item-supplied reading, historical kana, special proper-name reading | `01_reading_selection.md` |
| long vowels, adjacent vowels, morpheme boundaries | `02_vowels_and_boundaries.md` |
| proper-name/entity capitalization | `03_capitalization.md` |
| punctuation, middle dot, brackets, repetition marks | `04_punctuation.md` |
| macrons and apostrophes | `05_romanization_symbols.md` |
| compounds and general word division | `06_word_division_basics.md` |
| prefixes and suffixes | `07_prefixes_suffixes.md` |
| loan-word and foreign-name word division | `08_loanwords.md` |
| verbs, adjectives, adverbs, conjunctions, particles | `09_verbs_adjectives_particles.md` |
| personal/corporate/work-title proper-name exceptions | `10_proper_names.md` |
| geographic names | `11_geographic_names.md` |
| numerals and numeric punctuation | `12_numerals.md` |

Do not choose only one file when rules interact. For example, a geographic proper name may require reading selection, capitalization, word division, and geographic-name rules.

## Project policies

These decisions were made by the project owner and apply on top of the rule files.

- **P1 — initial capital.** The first letter of the proposed output is always capitalized, whatever `kind` is (sentence, phrase, common noun, title). The core already does this: keep it, never lowercase it, and record no decision for it. Capitalization after the first letter follows `rules/03_capitalization.md`.
- **P2 — table-driven readings.** When a rule file gives an explicit table or example for the exact expression (for example 私 → `watakushi` with variant `watashi`, 十日 → `tōka`), apply the table's preferred form. If it differs from the core, record `changed` and add the table's variant as `variant_added`. Do not override it with contextual judgment about what sounds natural, and do not use `lookup_required` for it.
- **P3 — search before lookup.** Before declaring `lookup_required`, search the `rules/` directory next to this `SKILL.md` for the exact expression and for related tables (dates, counters, native readings, exceptions): `grep -rn "<expression>" <skill_dir>/rules/` (`<skill_dir>` is the directory containing this `SKILL.md`). Use `lookup_required` only when no rule text or example covers it.

---

# 5. Stage C — apply ALA-LC as a delta from the core baseline

The AI's job is not to create a second independent romanization. It is to determine what ALA-LC requires **relative to the preserved core baseline**.

For each relevant rule, decide whether it:

- changes the core result;
- confirms the core result without change;
- adds a supported variant;
- requires information not currently available.

Use these action values in the trace:

```text
changed
verified_no_change
variant_added
lookup_required
```

## Important distinction

A `verified_no_change` decision is useful data, but only when the check was material: another rule, an exception, or an alternative reading actually competed, and you can record it as `considered_not_applied` in `rule_evaluations`.

Do **not** record routine confirmations: a proper noun that stays capitalized, a word boundary the core already placed correctly, a particle that stays separate, the initial capital (P1). If no competing rule or exception was considered, there is no decision.

Targets should not overlap between decisions unless they concern different aspects of the same span. When one span has several findings, keep one decision per distinct finding.

---

# 6. Decision construction

Each meaningful ALA-LC judgment must have a stable `decision_id` within the case (`d1`, `d2`, ...).

A decision trace should contain:

```json
{
  "decision_id": "d1",
  "type": "word_division",
  "action": "changed",
  "target": {
    "text": "...",
    "start": 0,
    "end": 2
  },
  "before": "...",
  "after": "...",
  "candidates": [
    {
      "output": "...",
      "rule": "ALA-LC-6.2.1"
    }
  ],
  "rule_evaluations": [
    {
      "rule": "ALA-LC-6.2.1",
      "result": "applied"
    }
  ],
  "reason": "...",
  "confidence": 0.0,
  "information_used": [
    "core.tokens[*].pos",
    "sentence_context"
  ],
  "external_references": []
}
```

`information_used` and `external_references` are **intermediate trace fields**. They provide factual provenance to `alalc-observe`; they are not themselves Phase 2 automation judgments.

## `target` offsets

- `start` and `end` refer to offsets in the original input text.
- Preserve exact source substrings.
- Never fabricate offsets from the romanized string.

## Rule identifiers

Use stable identifiers in the form:

```text
ALA-LC-2.5.5.1
ALA-LC-6.8.4
ALA-LC-7.2.1
```

The number must correspond to the source ALA-LC section represented in the rule file.

## Rule evaluation values

Use only:

```text
applied
considered_not_applied
not_applicable
```

When two rules compete, explicitly record both when the comparison was material to the decision.

---

# 7. Reasoning and evidence rules

The trace must provide concise reasons, not hidden chain-of-thought.

A good `reason` states the observable linguistic/cataloging basis, for example:

```text
「誰か」はこの文脈では不定代名詞として機能するため、一語として扱う。
```

Do not include long internal deliberation.

For `information_used`, identify concrete inputs that affected the decision, such as:

```text
core.tokens[*].surface
core.tokens[*].kana
core.tokens[*].pos
core.tokens[*].conjugation_form
input.kind
input.context_before
input.context_after
input.item_supplied_reading
sentence_context
```

If an external dictionary, authority source, official entity source, or web source is actually consulted, record it in `external_references` with enough information for later review.

Example intermediate reference:

```json
{
  "type": "official_source",
  "title": "...",
  "url": "...",
  "supports": "established reading ..."
}
```

Do not claim that an external source was used when the model merely knew something from training.

---

# 8. Handling missing information and unresolved cases

Do not silently invent evidence.

If an ALA-LC rule requires information that is not available:

1. preserve the core baseline for the unresolved span;
2. create a `lookup_required` decision;
3. set `after` to `null` when no defensible ALA-LC replacement is available;
4. list plausible candidates only when the rule files or available evidence support them;
5. state what information is missing;
6. hand the case forward for observation/review rather than pretending it is resolved.

The overall `proposed_output` may retain the core rendering for an unresolved span. That does **not** mean the span has been verified as ALA-LC compliant; the `lookup_required` decision is authoritative for that issue.

Use external lookup only when:

- a relevant ALA-LC rule actually calls for reference evidence; and
- the current harness/user permissions allow it.

If lookup is unavailable, do not substitute model memory for a checked reference.

---

# 9. Stage D — build the ALA-LC proposal

After all applicable decisions are made:

1. start from the core baseline;
2. apply every resolved `changed` decision;
3. retain `verified_no_change` spans unchanged;
4. record variants separately rather than replacing the preferred form;
5. retain unresolved spans provisionally from the core result and keep their `lookup_required` decisions explicit.

Set:

```text
core_output_accepted_without_change = true
```

only if the final proposal is textually identical to the core output and no `changed` decision altered it.

A difference in capitalization, spaces, hyphens, punctuation, macrons, apostrophes, or digits counts as a change.

---

# 10. Output contract: ALA-LC Romanization Trace

This skill outputs an **intermediate trace**, not a completed `Phase1Observation`.

Recommended top-level shape:

```json
{
  "trace_version": "alalc-romanization-trace/0.1.0",
  "case_id": "...",
  "input": {
    "text": "...",
    "kind": "unknown",
    "context_before": null,
    "context_after": null,
    "item_supplied_reading": null,
    "notes": null,
    "metadata": {}
  },
  "core_result": {
    "output": "...",
    "raw": {},
    "reading_raw": null
  },
  "alalc_result": {
    "proposed_output": "...",
    "variants": [],
    "core_output_accepted_without_change": false
  },
  "decisions": [],
  "unresolved": []
}
```

The later `alalc-observe` skill will use this trace to populate fields such as:

- `automation_class`;
- `candidate_layer`;
- `required_information`;
- `core_information_sufficient`;
- `external_reference_needed` / `external_reference_used`;
- `automation_notes`;
- `open_questions`.

Do **not** pre-judge these Phase 2-oriented observation fields here unless the observation skill explicitly requests factual provenance from this trace.

---

# 11. Quality gates before returning a case

A case is ready to hand to `alalc-observe` only when all applicable checks pass:

1. **Core-first check** — `japanese-romanization-core` actually ran for this case.
2. **Baseline preservation check** — the raw core JSON is preserved without AI edits.
3. **Rule-source check** — every ALA-LC change cites at least one relevant ALA-LC section.
4. **Delta-accounting check** — every material difference between core output and ALA-LC proposal is explained by one or more decisions.
5. **No-fabrication check** — no reading, entity fact, reference lookup, or item-supplied reading is invented.
6. **Offset check** — decision target offsets refer to the original Japanese input.
7. **Variant check** — variants are not silently substituted for the preferred proposal.
8. **Unresolved check** — unresolved issues are explicit and do not masquerade as verified output.
9. **Independence check for batches** — one case's interpretation did not become evidence for another without explicit shared metadata.

10. **Script check** — `alalc-validate-trace` reports no errors. Warnings (routine `verified_no_change`, missing initial capital) must be resolved or justified.

Build each trace with `alalc-assemble-trace`, which embeds the raw core JSON verbatim and refuses to write a trace that fails validation:

```bash
uv run --project "$ALALC_HOME" alalc-assemble-trace \
  --case case.json --core-raw core.json [--reading-raw reading.json] --judgment judgment.json --out <trace>.json
```

`--reading-raw` is required exactly when the case has `item_supplied_reading`.

`judgment.json` contains only your output: `proposed_output`, `variants`, `decisions`, `unresolved`. Never write `core_result` or `core_output_accepted_without_change` by hand.

If one of these checks fails, fix the trace before proceeding. If it cannot be fixed because information is missing, preserve the case as unresolved rather than guessing.

---

# 12. Batch file behavior

When a batch output directory is available, use one file per case, for example:

```text
phase1/batches/B20261002-001/
├── input.jsonl
└── romanized/
    ├── B20261002-001-0001.json
    ├── B20261002-001-0002.json
    └── ...
```

Do not write `human_review` here.

Do not merge the records into the reviewed corpus here.

The next stage owns transformation from these romanization traces into pending Phase 1 observations.

---

# 13. Scope boundaries

This skill **does**:

- run the core baseline;
- inspect UniDic/core analysis;
- apply the project's ALA-LC rule files;
- use AI judgment where the rule files require context;
- preserve variants and unresolved points;
- create a decision trace.

This skill **does not**:

- alter `japanese-romanization-core`;
- decide what should be automated in Phase 2;
- write `Automation notes` or answer `Open questions for Phase 1` as the final observation layer;
- mark Human Review as accepted or corrected;
- overwrite a human-reviewed result;
- treat model memory as a verified external authority source.

The handoff target is `alalc-observe`, not the final reviewed corpus.
