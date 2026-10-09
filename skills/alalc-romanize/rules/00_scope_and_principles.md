# Scope and General Principles

**Source:** ALA-LC Romanization Table: Japanese (2022), §§1–2.1  
**Phase:** Phase 1 — Skill rules  
**Purpose:** Define the scope of ALA-LC Japanese romanization and the general decision order to be used before applying more specific rules.

> **Unofficial restatement.** This file is an unofficial, operational summary of the ALA-LC Romanization Table: Japanese (2022). It is not the official table; the source document always takes precedence. See NOTICE.md at the repository root.

> This file is an operational restatement of the 2022 ALA-LC table for use by a Skill. It does not replace the source document. When this file and the source appear to conflict, treat the source as authoritative and flag the case for review.

## 1. Scope of the romanization table

ALA-LC Japanese romanization is a **transliteration scheme for library cataloging**. Its purpose is to convert Japanese script to the Roman alphabet in a consistent and uniform way while reflecting the original Japanese text and its readings as closely as practical.

It is **not a pronunciation guide**. Pronunciation matters when determining readings, but the output is governed by the cataloging romanization rules rather than by a goal of reproducing speech phonetically.

A one-to-one mapping from Japanese script to romanized text is not always possible. Reading may vary by time, place, entity, or context. When the rules do not determine a unique result, textual context and appropriate reference sources must be considered.

Alternative readings may be useful as **variant access points** in bibliographic or authority records when doubt remains or when an alternative is useful for access.

## 2. Two components of the task

ALA-LC Japanese romanization has two major components:

1. **Romanization of the Japanese text** — converting the source script and selected reading into Roman letters. The principal guidance is in §§2–5 and §7, together with the Romanized/Kana Equivalent Charts.
2. **Word division** — deciding where spaces and, in specified cases, hyphens occur. The principal guidance is in §6.

These components interact and must both be considered when producing a final result.

## 3. General reading and transcription order

Apply the following order unless a more specific rule overrides it:

1. **Respect an explicitly indicated reading on the item.**
   - If the material being cataloged supplies a specific reading, use that reading.
2. **For kana-only text, normally romanize what is written.**
   - Hiragana and katakana words or parts of words are generally romanized as they appear, subject to explicit exceptions elsewhere in the table.
3. **If no reading is supplied and the reading is uncertain, consult standard Japanese dictionaries.**
   - Prefer the current modern reading as far as possible.
4. **Apply the relevant ALA-LC conversion and word-division rules.**
5. **If ambiguity remains, preserve it as an explicit decision point rather than silently guessing.**
   - Consider a variant romanization where appropriate.

## 4. Rule precedence for the Skill

For Phase 1, use this precedence when rules appear to compete:

1. A reading explicitly supplied on the item.
2. A specific ALA-LC exception for the case at hand.
3. A specific ALA-LC rule for the relevant class of expression.
4. The general ALA-LC rule.
5. Contextual judgment and reference-source evidence.
6. Variant romanization when a useful alternative should be retained.

Do not let a general heuristic override an explicit exception or a reading supplied by the item.

## 5. Handling uncertainty

When a unique output cannot be justified from the available evidence:

- Do not invent a reading or boundary merely to return one answer.
- Identify the unresolved point explicitly.
- State which ALA-LC rule or rules are relevant.
- Preserve plausible alternatives when they are supported.
- Prefer evidence from the item itself, then appropriate reference sources.
- Use an AI judgment only for the unresolved decision, not to rewrite portions already determined by rules.

### Suggested Skill output for an unresolved case

```yaml
status: needs_judgment
issue:
  type: reading | word_division | capitalization | other
  surface: "..."
  context: "..."
  relevant_rules:
    - "ALA-LC ..."
  candidates:
    - value: "..."
      evidence: "..."
    - value: "..."
      evidence: "..."
```

## 6. Relationship to `japanese-romanization-core`

For Phase 1, treat the core library as the provider of linguistic analysis and basic romanization candidates. Do not assume that a core token boundary, dictionary reading, or basic romaji rendering is automatically the final ALA-LC result.

The Skill is responsible for applying the ALA-LC-specific rules that are not already guaranteed by the core and for identifying cases that require contextual judgment.

## 7. Automation notes

### Likely automatable

- Detect whether the source is kana-only.
- Apply a reading explicitly supplied by upstream structured input.
- Route a case to the relevant rule group.
- Record provenance for the source text, reading, rule, and final decision.

### May require contextual judgment

- Choosing among multiple readings when dictionaries or sources disagree.
- Determining whether an alternative should be retained as a variant access point.
- Resolving cases where historical, entity-specific, or contextual usage differs from a default reading.

### Open questions for Phase 1

- How should an item-supplied reading be passed to the Skill: inline annotation, structured metadata, or both?
- Which dictionary/reference-source checks should be performed automatically, and which should remain a human/AI task?
- What minimum provenance should be stored for every non-default decision?
