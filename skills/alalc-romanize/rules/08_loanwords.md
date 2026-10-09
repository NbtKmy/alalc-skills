# Loan Words and Neologisms: Word Division

**Source:** ALA-LC Romanization Table: Japanese (2022), §6.7  
**Phase:** Phase 1 — Skill rules  
**Purpose:** Determine word division for loan words, Japanese neologisms based on foreign words, and foreign geographic names.

> **Unofficial restatement.** This file is an unofficial, operational summary of the ALA-LC Romanization Table: Japanese (2022). It is not the official table; the source document always takes precedence. See NOTICE.md at the repository root.

> This file concerns **word division**. The selection of a kana reading or kana-by-kana romanization for unusual loan-word spellings is handled in §2.4.2.

## 1. General rule (§6.7.1)

Loan words include both direct borrowings and Japanese neologisms or coined forms derived from foreign expressions.

Some word boundaries are straightforward; others are not. Apply the best-supported division and add a variant when necessary.

### Examples

| Japanese | Romanization | Note |
|---|---|---|
| ベストセラー | `besuto serā` | best seller |
| マスメディア | `masu media` | mass media |
| アール・ヌーヴォー | `Āru Nūvō` | Art Nouveau |
| アヴァンギャルド | `avan gyarudo` | variant: `avangyarudo` |
| ファッションデザイナー | `fasshon dezainā` | fashion designer |
| コンピュータプログラミング | `konpyūta puroguramingu` | computer programming |
| サラリーマン | `sararīman` | variant: `sararī man` |
| チアガール | `chiagāru` | variant: `chia gāru` |

### Decision point

Katakana orthography alone does not always encode the ALA-LC word boundary. Knowledge of the source expression, Japanese lexicalization, and established usage may matter.

---

## 2. Shortened loan words (§6.7.2)

Write neologisms formed by combining shortened forms of foreign words as **one word**.

### Examples

- ワープロ → `wāpuro`
- エアコン → `eakon`
- アメフト → `amefuto`

This rule reflects the Japanese lexicalized shortened form, not the word division of the original foreign phrase.

---

## 3. Foreign geographic names (§6.7.3)

Apply the general loan-word rule to foreign geographic names.

### Basic examples

- ホンコン → `Honkon`
- 北京 → `Pekin`
- ペキン → `Pekin`

### Preserve original-language word division when the kana form permits it

When a foreign geographic name corresponds to multiple words in the original language, retain that word division in romanization when the kana rendition supports it. In these cases, the source strongly recommends adding a variant without that spacing.

| Japanese | Preferred | Suggested variant |
|---|---|---|
| ニューヨーク | `Nyū Yōku` | `Nyūyōku` |
| ニュージーランド | `Nyū Jīrando` | `Nyūjīrando` |
| サンフランシスコ | `San Furanshisuko` | `Sanfuranshisuko` |
| サンパウロ | `San Pauro` | `Sanpauro` |

### When kana does not support the expected original-language spacing

If the kana rendition does not permit the spacing expected from the original language, write the name without that spacing.

- ロサンゼルス → `Rosanzerusu`
- ロスアンゼルス → `Rosu Anzerusu`
- サンノゼ → `Sannoze`
- サンホゼ → `San Hoze`

### Decision point

The same foreign name can have different ALA-LC spacing depending on the Japanese kana rendition on the item.

---

## 4. Foreign geographic names with Japanese additions (§6.7.3)

When a foreign geographic name is combined with a Japanese geographic or other addition, apply both §6.7.1 and the geographic-name rules in §6.10.

### Examples

| Japanese | Romanization |
|---|---|
| ホーチミン市 | `Hō Chi Min-shi` |
| カリフォルニア州 | `Kariforunia-shū` |
| ニューヨーク市長 | `Nyū Yōku shichō` |
| グランドセントラル駅 | `Gurando Sentoraru-eki` |
| ゴビ砂漠 | `Gobi sabaku` |

The added Japanese element does not always behave the same way: jurisdiction names, stations, and common-noun compounds are governed by their specific rules.

---

## 5. Suggested Phase 1 decision procedure

```text
Is the expression a shortened Japanese loan-word blend?
├─ yes → write as one word
└─ no
   ↓
Identify plausible foreign-source word boundaries and Japanese lexicalization.
↓
If it is a foreign geographic name, determine whether the kana form supports
original-language word division.
├─ yes → preserve that division; consider unspaced variant
└─ no → keep the division licensed by the kana form
↓
If Japanese geographic additions occur, apply §6.10 to those additions.
↓
If more than one division remains defensible, emit a variant/judgment point.
```

## 6. Automation notes

### Likely automatable

- A lexicon of common shortened loan-word blends such as `wāpuro`, `eakon`, and `amefuto`.
- Application of §6.10 once the foreign-name base and Japanese addition are identified.
- Retaining source-kana evidence so that spacing is not normalized away.

### May require contextual or external knowledge

- Recovering the foreign source expression and its original word division.
- Determining whether a Japanese loan word has lexicalized as one unit despite its foreign origin.
- Choosing when an unspaced variant should be supplied.
- Distinguishing foreign geographic names from ordinary loan words when entity context is absent.

### Open questions for Phase 1

- Should the Skill consult external name/reference sources for foreign geographic names, or only use information supplied with the item?
- Can common loan-word division be handled by a lexicon before AI judgment?
- How should evidence for original-language word division be recorded in Phase 1 observations?
- Should strongly recommended variants for foreign geographic names be emitted automatically or only when cataloging context requests variants?
