# Reading Selection

**Source:** ALA-LC Romanization Table: Japanese (2022), §§2.2–2.4  
**Phase:** Phase 1 — Skill rules  
**Purpose:** Select the reading to be romanized before later spelling, capitalization, and word-division rules are applied.

> **Unofficial restatement.** This file is an unofficial, operational summary of the ALA-LC Romanization Table: Japanese (2022). It is not the official table; the source document always takes precedence. See NOTICE.md at the repository root.

> This file is an operational restatement of the 2022 ALA-LC table. It distinguishes source-supported reading choice from later romanization mechanics.

## 1. Preferred reading sources (§2.2)

When a Japanese expression has multiple readings:

1. If the item itself supplies a reading, use that reading.
2. Otherwise, use the reading preferred by most standard dictionaries.
3. A supported alternative may be retained as a suggested variant.

### Examples

| Text on item | Preferred romanization | Suggested variant |
|---|---|---|
| 私 | `watakushi` | `watashi` |
| 大地震 | `daijishin` | `ōjishin` |
| 重複 | `chōfuku` | `jūfuku` |

### Decision point

The Skill must not infer that the first reading returned by a morphological analyzer is necessarily the ALA-LC preferred reading. Dictionary preference or an item-supplied reading may override it.

---

## 2. Grammatical particles (§2.3.1)

When used as grammatical particles:

- `は` → `wa`
- `へ` → `e`

This rule applies to their **grammatical use**, not every occurrence of the characters `は` and `へ`.

### Automation note

Correct application depends on identifying the grammatical function. If the analyzer provides reliable particle tagging, this may be deterministic; otherwise the Skill may need contextual judgment.

---

## 3. Historical kana usage (§2.3.2)

For historical kana orthography:

1. Use the **modern reading** unless the item assigns a specific reading.
2. A direct kana-by-kana rendering of the historical spelling may be supplied as a variant.

### Examples

| Historical form | Modern reading | Preferred romanization | Suggested variant |
|---|---|---|---|
| てふてふ | ちょうちょう | `chōchō` | `tefutefu` |
| ぬゑのたんじやう | ぬえのたんじょう | `Nue no tanjō` | `Nue no tanjiyau` |
| おもひでぽろぽろ | おもいでぽろぽろ | `Omoide poroporo` | `Omohide poroporo` |

### Decision point

The source spelling alone does not always give the preferred romanization. The Skill may need to distinguish historical orthography from an intentionally assigned non-modern reading.

---

## 4. Well-established readings of proper names (§2.4.1)

For a proper name, a well-established non-standard reading may take precedence over an otherwise expected dictionary or character reading when that reading is commonly attested in sources associated with the entity, such as websites, reference sources, or publications.

### Examples

| Text on item | Preferred romanization | Suggested variant |
|---|---|---|
| 本朝書籍目錄 | `Honchō shojaku mokuroku` | `Honchō shoseki mokuroku` |
| 圖書寮 / 図書寮 | `Zushoryō` | `Toshoryō` |
| 大日本帝国 | `Dai Nippon Teikoku` | `Dai Nihon Teikoku` |
| 日本永代蔵 | `Nippon eitaigura` | `Nihon eitaigura` |

### Decision point

This is not purely a character-to-reading problem. Entity-specific evidence may be required.

### Suggested evidence order

1. Reading explicitly given on the item.
2. Official or entity-associated source.
3. Reliable reference source.
4. Standard dictionary preference.
5. Supported variant if more than one reading remains useful.

---

## 5. Loan words written in kana (§2.4.2.1)

For a loan word written in kana, romanize **the kana actually written on the item**, kana by kana, even if the spelling differs from the form normally used in contemporary Japanese.

A normalized or commonly used alternative may be supplied as a variant.

### Examples

| Text on item | Usual modern spelling | Preferred romanization | Suggested variant |
|---|---|---|---|
| コミユニテイ | コミュニティ | `komiyunitei` | `komyuniti` |
| スタア | スター | `sutaa` | `sutā` |
| テレビジオン | テレビジョン | `terebijion` | `terebijon` |
| ギリシア | ギリシャ | `Girishia` | `Girisha` |
| シンポジウム | — | `shinpojiumu` | `shinpojūmu` |
| シンポジューム | — | `shinpojūmu` | — |

### Important distinction

Do not silently normalize the source kana before producing the preferred ALA-LC form. The written form is significant.

---

## 6. Foreign geographic names written in kanji (§2.4.2.2)

For foreign geographic names that are originally in Chinese characters or are represented in Japanese by kanji:

1. Follow the preferred-reading principles in §§2.2 and 2.4.1.
2. Use preferred sources to identify the reading unless the item supplies one.
3. Alternative supported readings may be supplied as variants.
4. Also consult the geographic-name rules in §6.10 for word division and related formatting.

### Examples

| Text | Preferred romanization | Suggested variant(s) |
|---|---|---|
| 香港 | `Honkon` | — |
| 済州島 | `Chejutō` | `Chejudō`, `Saishūtō`, `Saishūdō` |
| 紐育 | `Nyū Yōku` | `Nyūyōku` |
| 加奈陀 | `Kanada` | — |
| 亜米利加 | `Amerika` | — |

### Decision point

The correct reading may depend on historical period, established usage, or the language associated with the place name; do not derive it mechanically from kanji alone.

---

## 7. Alternative romanizations as variants (§2.4.3)

Variant romanizations may be added to bibliographic and authority records based on cataloger judgment.

A variant is not automatically a correction of the preferred form; it is an additional access form.

### Examples

#### その後

Preferred:

- `sonogo`

Suggested variants:

- `sono go`
- `sono ato`
- `sono nochi`
- `sonoato`
- `sononochi`

#### 行く年来る年

Preferred:

- `yuku toshi kuru toshi`

Suggested variant:

- `yukutoshi kurutoshi`

#### 等

Preferred:

- `tō`

Suggested variants:

- `nado`
- `ra`

---

## 8. Suggested Phase 1 decision procedure

```text
Is a reading explicitly supplied on the item?
├─ yes → use it
└─ no
   ↓
Is this historical kana usage?
├─ yes → determine modern reading; keep direct historical rendering only as variant if useful
└─ no
   ↓
Is this a proper name or foreign geographic name with established special usage?
├─ yes → check entity/reference evidence
└─ no
   ↓
Is this a kana loan word?
├─ yes → romanize the kana as written; normalization may become a variant
└─ no
   ↓
Use the reading preferred by standard dictionaries
```

After selecting the reading, pass it to the later rules for long vowels, word division, capitalization, punctuation, etc.

## 9. Automation notes

### Likely automatable

- Detect item-supplied reading when provided as structured metadata.
- Detect kana-only loan-word spelling and preserve the written kana.
- Generate candidate variants from explicitly supplied alternative readings.
- Apply `は → wa` and `へ → e` when grammatical-particle tagging is reliable.

### May require contextual or external-reference judgment

- Preferred reading among competing dictionary readings.
- Historical spelling versus intentionally assigned reading.
- Well-established non-standard reading of a proper name.
- Foreign geographic-name reading.
- Whether a variant is useful enough to retain.

### Open questions for Phase 1

- Which reference sources are allowed or preferred for entity-specific readings?
- Should variant generation be automatic, suggested, or opt-in?
- How should confidence/evidence be represented when an AI resolves a reading?
