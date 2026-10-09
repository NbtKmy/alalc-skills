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

4. **Ask one question at a time.**
   - First: is the ALA-LC proposal `accepted` or does it need to be `corrected`?
   - If `corrected`, ask in turn: the corrected output; which decisions they disagree with and, for each, whether the decision is correct, the corrected result, any change to the observation fields, and a comment; any issues the AI missed (target text and note); a general comment.
   - Decisions the user does not mention count as agreed.

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

6. **Save.**

   ```bash
   uv run --project "$ALALC_HOME" alalc-apply-review --record observed/<case_id>.json --review review.json
   ```

   The command adds `reviewed_at`, validates, sets `status: reviewed` and writes the record. On failure nothing is written: show the user the error and fix `review.json` with them.

7. **Continue or stop.** The user may stop at any time. Remaining records stay `pending` and are picked up next time.

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
