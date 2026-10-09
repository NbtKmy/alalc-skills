---
name: alalc-review
description: Walk a human through pending ALA-LC observation records one case at a time in Claude Code, and record their Human Review verbatim. Use after alalc-observe.
compatibility: Claude Code and OpenCode. Requires uv and a clone of the alalc-skills repository (ALALC_HOME).
metadata:
  project: japanese-romanization
  phase: "1"
---

# ALA-LC Review — Phase 1

## Purpose

Present each pending observation record to a human, ask for their verdict, and save it as `human_review`. The human's answers are the data. This skill never judges for them.

## Environment

```text
ALALC_HOME=/absolute/path/to/alalc-skills     # clone of the alalc-skills repository, `uv sync` done
```

If `ALALC_HOME` is unset, stop and ask the user to set it. Every command runs as `uv run --project "$ALALC_HOME" <command>`.

## Workflow

1. **Ask for the reviewer name once**, at the start. Use the string exactly as given. Never guess or fill it in.

2. **List pending records** (in `case_id` order):

   ```bash
   uv run --project "$ALALC_HOME" alalc-list-pending observed/
   ```

   Each line is `<case_id><TAB><path>`. Lines starting with `skip:` on stderr are records that could not be read or failed validation; tell the user and do not review them.

3. **Present one record at a time**: the input text and `kind`, the core output, the ALA-LC proposal, the variants, each decision with its seven observation fields, and the unresolved points. Show the data as it is.

4. **Ask the questions in the order below, one at a time.** See "How to ask" for the wording rules.
   1. *Verdict:* is the ALA-LC proposal correct as a whole? Options: `accepted` / `corrected`.
   2. If `corrected`, ask for the corrected output (free text).
   3. For **every** decision in the record, one by one, in `decision_id` order, ask two separate questions:
      - *Romanization:* is this decision correct? Options: correct / not correct. If not correct, ask for the corrected result (`corrected_after`) and an optional comment.
      - *Automation observation:* is its automation assessment (the seven fields) right? Options: right / needs a change. If it needs a change, ask which fields change and to what.
   4. *Missed issues:* is there anything the AI should have recorded as a decision but did not? If yes, ask for the target text and a note, and repeat until the user says no.
   5. *General comment* (optional, may be empty).

   Write a `decision_overrides` entry only for a decision where the user answered "not correct" or "needs a change". A decision where both answers were "correct" / "right" gets no entry; that is how agreement is recorded. Never infer agreement or disagreement from an unanswered question or an unchecked box; ask.

5. **Write `review.json`** (a scratch file) by copying the user's answers as they gave them. Do not complete, paraphrase or improve them. Do not include `reviewed_at`; the command adds it.

   ```json
   {
     "reviewer": "<name as given>",
     "case_verdict": "corrected",
     "corrected_output": "<their text>",
     "decision_overrides": [
       {
         "decision_id": "d1",
         "decision_correct": false,
         "corrected_after": "<their text>",
         "observation": { "automation_class": "ai_judgment", "candidate_layer": "llm" },
         "comment": "<their words>"
       }
     ],
     "missed_issues": [{ "target_text": "<their text>", "note": "<their words>" }],
     "comment": null
   }
   ```

   For `accepted`, give only `reviewer` and `case_verdict`. `corrected_output` must be null for `accepted` and must differ from the proposal for `corrected`. In `decision_overrides`, only `decision_id` is required; `observation` may hold just the fields that change.

6. **Confirm, then save.** Before saving, read the whole review back in plain language (verdict, corrected output, each decision marked correct or not, observation changes, missed issues, comment) and ask "この内容で保存してよいですか？ / Save this?". Save only after a yes. If the user wants a change, fix `review.json` and read it back again.

7. **Save.**

   ```bash
   uv run --project "$ALALC_HOME" alalc-apply-review --record observed/<case_id>.json --review review.json
   ```

   The command adds `reviewed_at`, validates, sets `status: reviewed` and writes the record. On failure nothing is written: show the user the error and fix `review.json` with them.

8. **Continue or stop.** The user may stop at any time. Remaining records stay `pending` and are picked up next time.

## How to ask

- Use the user's language (Japanese if they write Japanese).
- One decision and one question at a time. Show the decision's `before` → `after`, `reason` and cited rules next to the question.
- Use positive, single-choice questions ("この判断は正しいですか？ 正しい / 正しくない"). Do **not** ask "check the box if you disagree" or "no check means you agree".
- Do not use multi-select questions where the meaning of an answer depends on which other options are selected or left empty. Only use multi-select for picking fields to change (step 3, second question), and say plainly what each selected item will do.
- If an answer seems contradictory or unclear, do not stop and do not guess. Ask one short clarifying question about that single point, quoting the user's own words.
- The user's reasons belong in `comment` (decision level or general), in their own words.

## Re-reviewing

A `reviewed` record is refused by default. If the user explicitly wants to redo one, add `--replace`; the previous review moves to `human_review_history`.

```bash
uv run --project "$ALALC_HOME" alalc-apply-review --record observed/<case_id>.json --review review.json --replace
```

## Warnings

If the command warns that the verdict is `accepted` but a decision is marked `decision_correct: false`, ask the user which they meant before moving on.

## Do not

- fill in, translate or "fix" what the user says;
- decide the verdict or any override yourself;
- edit `trace` or `trace_sha256` in a record;
- review a record that failed validation.
