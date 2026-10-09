# Diacritic Marks and Other Romanization Symbols

**Source:** ALA-LC Romanization Table: Japanese (2022), §5  
**Phase:** Phase 1 — Skill rules  
**Purpose:** Apply the macron and apostrophe conventions used in ALA-LC Japanese romanization after the relevant reading has been established.

> **Unofficial restatement.** This file is an unofficial, operational summary of the ALA-LC Romanization Table: Japanese (2022). It is not the official table; the source document always takes precedence. See NOTICE.md at the repository root.

> Long-vowel determination is governed in detail by §2.5. This file defines the symbols themselves and the apostrophe rule.

## 1. Macron (§5.1)

Use a macron over a vowel to indicate a long vowel where the ALA-LC rules call for one.

The macron can occur over:

- `ā`
- `ī`
- `ū`
- `ē`
- `ō`

The decision whether a vowel is long, whether `ii` is retained, and whether adjacent vowels cross a morpheme boundary must follow §2.5 rather than a simple character-replacement rule.

### Automation note

The final insertion of a macron is likely deterministic once the reading and the §2.5 analysis are fixed.

---

## 2. Apostrophe after syllabic `n` (§5.2)

Insert an apostrophe between syllables when:

1. the first syllable ends in `n`, and
2. the following syllable begins with a vowel (`a`, `i`, `u`, `e`, `o`) or `y`.

The apostrophe shows that the final `n` belongs to the preceding syllable rather than to the onset of the following syllable.

### Examples

| Japanese | Romanization |
|---|---|
| 長井憲一 | `Nagai Ken'ichi` |
| 信越 | `Shin'etsu` |
| 翻訳 | `hon'yaku` |
| 万葉 | `Man'yō` |
| 親愛なる | `shin'ainaru` |
| 三億円 | `san'okuen` |
| 真打 | `shin'uchi` |

### Key distinction

Do not insert an apostrophe merely because the letters `n` and a vowel/y are adjacent in a final Roman string. The rule depends on a **syllable boundary** in which `n` is syllabic and belongs to the preceding syllable.

---

## 3. Suggested Phase 1 decision procedure

```text
Has §2.5 determined that a vowel requires a macron?
├─ yes → add the appropriate macron
└─ no → preserve the non-macron form required by §2.5

For each syllabic n boundary:
Does the following syllable begin with a, i, u, e, o, or y?
├─ yes → insert apostrophe
└─ no → no apostrophe
```

## 4. Automation notes

### Likely automatable

- Rendering macrons once long-vowel status is known.
- Inserting the apostrophe when syllable boundaries are available.
- Validating that the final output does not omit a required apostrophe.

### May require contextual or structural judgment

- Determining the relevant syllable/morpheme boundary if the core exposes only a flat Roman string.
- Distinguishing syllabic `n` from an `n` that belongs to the following syllable when upstream analysis is incomplete.

### Open questions for Phase 1

- Does `japanese-romanization-core` already preserve enough kana/syllable structure to apply §5.2 without AI judgment?
- Should apostrophe insertion live in the core renderer or remain an ALA-LC-specific post-processing rule?
- Can macron handling be treated as fully delegated to the core, or are there ALA-LC-specific cases that still require a separate validation step?
