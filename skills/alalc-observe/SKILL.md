---
name: alalc-observe
description: Assess each decision in ALA-LC romanization traces for how far it could be automated without AI, and write pending Phase 1 observation records. Use after alalc-romanize has produced traces and before alalc-review.
compatibility: Claude Code and OpenCode. Requires uv and a clone of the alalc-skills repository (ALALC_HOME).
metadata:
  project: japanese-romanization
  phase: "1"
---

# ALA-LC Observe — Phase 1

## Purpose

For every decision in an `alalc-romanize` trace, record how much of it could be done **without AI**. The records are later aggregated to find which parts of ALA-LC Japanese romanization can become Python code and which still need judgment.

This skill classifies. It does **not** re-decide the romanization, does not edit the trace, and does not perform Human Review (that is `alalc-review`).

## Environment

```text
ALALC_HOME=/absolute/path/to/alalc-skills     # clone of the alalc-skills repository, `uv sync` done
```

If `ALALC_HOME` is unset, stop and ask the user to set it. Every command runs as `uv run --project "$ALALC_HOME" <command>`.

## Input and output

```text
phase1/batches/<batch_id>/
├── romanized/<case_id>.json     # input: traces from alalc-romanize
└── observed/<case_id>.json      # output: one pending record per case
```

## Workflow

For each `romanized/<case_id>.json`, one case at a time:

1. **Validate the trace.**

   ```bash
   uv run --project "$ALALC_HOME" alalc-validate-trace romanized/<case_id>.json
   ```

   If it reports an error, report that case, skip it, and continue with the others. Never fix a trace here.

2. **Read the case.** Read each decision (`type`, `action`, `before`, `after`, `candidates`, `rule_evaluations`, `reason`, `information_used`), the ALA-LC rule files it cites (under the `alalc-romanize` skill's `rules/`), and the core fields it relies on. Take the facts for `required_information` from the decision's `information_used`; add only what that list lacks.

3. **Write `observation.json`** (a scratch file, any path) with exactly one entry per trace decision, `lookup_required` decisions included:

   ```json
   {
     "decisions": [
       {
         "decision_id": "d1",
         "automation_class": "table_driven",
         "candidate_layer": "lookup_table",
         "required_information": ["input.text", "rules/01_reading_selection.md §2.2 table"],
         "core_information_sufficient": false,
         "external_reference_needed": false,
         "automation_notes": "The reading is listed in the date table; no context is needed.",
         "open_questions": []
       }
     ]
   }
   ```

   A trace with no decisions gets `{"decisions": []}`.

4. **Assemble.**

   ```bash
   uv run --project "$ALALC_HOME" alalc-assemble-observation \
     --trace romanized/<case_id>.json --observation observation.json --out observed/<case_id>.json
   ```

   The command embeds the trace unedited, computes `trace_sha256`, validates, sets `status: pending` and writes the file. The output file name must be the `case_id`. If validation fails it writes nothing: fix `observation.json` and run it again.

5. **Handle warnings.** A warning means the class and layer do not fit together, or `core_information_sufficient` contradicts the layer. Either fix the classification or keep it and say why in `automation_notes`.

A record that is already `reviewed` is never overwritten. A `pending` record may be regenerated.

## The seven fields (per decision)

| Field | Meaning |
|---|---|
| `automation_class` | smallest mechanism that reproduces the decision (below) |
| `candidate_layer` | where it would be implemented if automated (below) |
| `required_information` | non-empty list: core fields (`core.tokens[*].pos`), input metadata (`input.kind`), rule tables (`rules/…`), context, dictionaries |
| `core_information_sufficient` | `true` only if the core output alone provides everything needed |
| `external_reference_needed` | `true` if an outside dictionary, authority file or entity information is needed |
| `automation_notes` | factual notes about automation; no speculation |
| `open_questions` | points to confirm in Human Review or later (may be empty) |

### `automation_class`

Choose the smallest mechanism that reproduces the decision.

- `deterministic` — core fields alone (POS, kana, conjugation, offsets) determine it in code.
- `table_driven` — a lookup in a rule table, vocabulary table or closed list (reading tables, counters, dates, exception lists) is enough. No AI needed.
- `ai_judgment` — the rule text is sufficient but context or meaning must be interpreted (for example *dareka* vs *dare ka*).
- `external_or_human` — the rule text alone does not decide it; outside material or a human decision is required.

### `candidate_layer`

- `core` — extend `japanese-romanization-core` itself.
- `alalc_rules` — an ALA-LC post-processing step in Python that receives the core output.
- `lookup_table` — rule or vocabulary table data that `alalc_rules` would read.
- `llm` — stays with the LLM.
- `human_authority` — a human or an external authority.

Usual pairings: `deterministic` → `core` / `alalc_rules`; `table_driven` → `lookup_table` / `alalc_rules`; `ai_judgment` → `llm`; `external_or_human` → `human_authority`.

## Quality gates

1. Every decision has an observation (one to one, by `decision_id`).
2. Enum values are valid and `required_information` is non-empty.
3. `trace_sha256` matches: the trace was not edited.
4. Every classification warning is fixed or explained in `automation_notes`.
5. Cases are independent: do not carry an interpretation from one case into another.

## Do not

- re-judge or edit the romanization, the trace, or the core output;
- invent facts for `required_information` or `automation_notes`;
- claim an external source was used unless the trace's `external_references` records it;
- write `human_review` or change `status`.
