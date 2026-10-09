# Punctuation and Typographical Marks

**Source:** ALA-LC Romanization Table: Japanese (2022), §4  
**Phase:** Phase 1 — Skill rules  
**Purpose:** Convert Japanese punctuation and typographical marks into the forms used in ALA-LC romanized text while preserving distinctions that affect meaning or word division.

> **Unofficial restatement.** This file is an unofficial, operational summary of the ALA-LC Romanization Table: Japanese (2022). It is not the official table; the source document always takes precedence. See NOTICE.md at the repository root.

> This file covers punctuation and typographical marks only. Numeric middle dots and ranges are governed more specifically by §7.5 and should be routed to the numeral rules when applicable.

## 1. General principle (§4)

Japanese punctuation and typographical marks should be handled according to the specific mappings below.

If a mark is not covered by the table, or if a simple one-to-one conversion does not work, do not silently invent a convention. Use contextual judgment and retain a variant when appropriate.

---

## 2. Middle dot `・` (§4.1)

When `・` divides words:

1. Use a **comma followed by a space** when that makes the meaning of the romanized words clearer.
2. Otherwise, use **a space only**.
3. If the middle dot occurs between numbers, do not apply this rule; use §7.5 instead.

### Examples

| Japanese | Romanization | Treatment |
|---|---|---|
| 松本清長・山本周五郎集 | `Matsumoto Seichō, Yamamoto Shūgorō shū` | comma + space |
| ポール・クローデル | `Pōru Kurōderu` | space only |

### Decision point

The mark itself does not determine whether a comma is needed. The Skill may need to decide whether the dot separates coordinate names/items or merely separates components of one expression.

---

## 3. Punctuation with Roman equivalents (§4.2)

Use the following equivalents:

| Japanese mark | Romanized form | Notes |
|---|---|---|
| `、` | `,` | comma |
| `。` | `.` | period |
| `？` | `?` | question mark |
| `！` | `!` | exclamation point |
| `～` | `-` | when used with numbers/dates for a range; see also §7.5 |
| `「」` | `""` | quotation marks |
| `『』` | `""` | quotation marks |
| `＝` | `=` | equal sign |

### Automation note

Most of these mappings are direct once the function of `～` has been identified.

---

## 4. Brackets and parentheses (§4.3)

Use the corresponding Roman forms:

| Japanese form | Romanized form |
|---|---|
| `〈 〉` | `< >` |
| `《 》` | `< >` |
| `〔 〕` | `[ ]` |
| `〖 〗` | `[ ]` |
| `〘 〙` | `[ ]` |
| `〚 〛` | `[ ]` |
| `( )` | `( )` |

Word division around bracketed material is handled in §6.3.2.

---

## 5. Repetition marks (§4.4.1)

The repetition marks `ゝ` and `々` indicate repetition of the preceding syllable according to the source rule. Expand the repeated material and romanize the resulting reading rather than reproducing the repetition mark itself.

### Examples

| Japanese | Romanization |
|---|---|
| 蝶々 | `chōchō` |
| 日々 | `hibi` |
| 年々 | `nennen` |
| こゝろ | `Kokoro` |

### Decision point

The repeated element may undergo a reading or voicing change. The Skill should rely on the established reading rather than mechanically duplicating Roman letters when that would produce the wrong result.

---

## 6. Geta placeholder `〓` (§4.4.2)

A geta mark may stand for a character that cannot be identified even after exhaustive research.

When a reading for the missing character is known, supply its romanized reading **in brackets**.

### Decision point

The source rule does not provide a method for discovering the missing character or its reading. If the reading is not supplied or otherwise established, the Skill should flag the case rather than invent one.

---

## 7. Suggested Phase 1 decision procedure

```text
Is the mark a numeric middle dot or a range marker?
├─ yes → route to §7.5 numeral rules
└─ no
   ↓
Is it a listed punctuation/bracket form?
├─ yes → apply the direct equivalent
└─ no
   ↓
Is it a middle dot dividing words?
├─ yes → choose comma + space or space according to clarity
└─ no
   ↓
Is it a repetition mark?
├─ yes → resolve the established repeated reading, then romanize
└─ no
   ↓
Is it a geta placeholder with a known reading?
├─ yes → supply that romanized reading in brackets
└─ no → flag for judgment/review
```

## 8. Automation notes

### Likely automatable

- Direct conversion of listed punctuation marks.
- Direct conversion of listed bracket forms.
- Routing numeric `・` and range `～` to §7.5.
- Removal of repetition marks after the repeated reading has been resolved.

### May require contextual judgment

- Whether a word-dividing middle dot should become comma + space or space only.
- The correct reading produced by a repetition mark when phonological or lexical changes occur.
- Any unlisted typographical mark.
- A geta placeholder whose reading is not supplied.

### Open questions for Phase 1

- Can punctuation conversion be performed entirely after linguistic analysis, or must some marks remain visible to the analyzer?
- What evidence reliably distinguishes comma-worthy `・` from a simple word separator?
- How should unknown/unlisted marks be represented in the observation data?
- Should a geta reading be accepted only when supplied by the user/cataloging record, or can it come from an external reference source?
