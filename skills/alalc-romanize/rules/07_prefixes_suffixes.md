# Prefixes and Suffixes

**Source:** ALA-LC Romanization Table: Japanese (2022), §§6.5–6.6  
**Phase:** Phase 1 — Skill rules  
**Purpose:** Decide whether prefixes and suffixes are joined, separated, or otherwise treated specially in ALA-LC word division.

> **Unofficial restatement.** This file is an unofficial, operational summary of the ALA-LC Romanization Table: Japanese (2022). It is not the official table; the source document always takes precedence. See NOTICE.md at the repository root.

> Prefix and suffix treatment depends not only on morphology but also on semantic independence, lexicalization, the script/type of the modified word, and several named exceptions.

## 1. Honorific prefixes (§6.5.1.1)

Keep the honorific prefix `御`, read `o`, `go`, `mi`, or `on`, together with the element it modifies.

### Examples

| Japanese | Romanization |
|---|---|
| お誕生日会 | `otanjōbikai` |
| お送り致しましょう | `ookuri itashimashō` |
| お出掛け遊ばしますか | `odekake asobashimasu ka` |
| おフランス | `Ofuransu` |
| 御祝儀袋 | `goshūgibukuro` |
| ご婦人方 | `gofujingata` |
| 御世 | `miyo` |
| 御曹司 | `onzōshi` |
| 御大将 | `ontaishō` |

Capitalization may still depend on the status of the resulting expression, as in `Ofuransu`.

---

## 2. Prefixes written together (§6.5.1.2)

Write a prefix together with the following word when separating it would fail to convey the intended meaning.

### Examples

`koseibutsugaku`, `daijinbutsu`, `daiōjō`, `shinkansen`, `kyūtaisei`, `shinkenchiku`, `chōtaikoku`, `zenchūshaku`, `kogirei`, `dainagon`, `shinhannin`, `keijidōsha`, `hijōshiki`, `ibunka`, `chōonpa`, `fukanō`, `ōjishin`, `Koimari`

### Decision point

The source frames this rule semantically: the intended meaning must remain intact. A purely orthographic prefix list is therefore insufficient for all cases.

---

## 3. Prefixes written separately when the base is independent (§6.5.2.1)

If the meaning of the modified word is independent from the prefix, write the prefix and the following word separately.

When in doubt, a variant may be added.

### Examples

- 各議員 → `kaku giin`
- 当施設 → `tō shisetsu`
- 一図書館員 → `ichi toshokan'in`
- 各都道府県 → `kaku todōfuken`

### Decision point

The distinction between an integrated lexical unit and an independent modified word is potentially semantic and usage-based.

---

## 4. Prefix + katakana loan word (§6.5.2.2)

When a prefix modifies a loan word written in katakana, write the prefix separately from the loan word.

### Examples

- 全マニュアル → `zen manyuaru`
- 元ボクサー → `moto bokusā`
- 各セクション → `kaku sekushon`
- 新アニメシリーズ → `shin anime shirīzu`

This is a strong structural rule when the katakana loan-word status is clear.

---

## 5. Prefixes modifying multiple compounds (§6.5.3)

Write a prefix separately when it modifies multiple following words or a word that does not immediately follow it.

### Examples

- 新植民地主義 → `shin shokuminchi shugi`
- 大人名事典 → `dai jinmei jiten`
- 小文学辞典 → `shō bungaku jiten`
- 各無産政党 → `kaku musan seitō`
- 一記念写真 → `ichi kinen shashin`

### Decision point

The Skill may need to determine the syntactic or semantic scope of the prefix.

---

## 6. General suffix rule (§6.6.1)

Write a compound formed by adding a single suffixed element as one word.

### Examples

| Japanese | Romanization |
|---|---|
| 耳鼻科 | `jibika` |
| 経済的 | `keizaiteki` |
| 生物学 | `seibutsugaku` |
| 人生観 | `jinseikan` |
| 唯物論 | `yuibutsuron` |
| 健康法 | `kenkōhō` |
| 落穂集 | `Ochiboshū` |
| カロリー表 | `karorīhyō` |
| エッセイ集 | `esseishū` |
| 経済学史 | `keizaigakushi` |
| 現代語訳 | `gendaigoyaku` |
| 外国語学 | `gaikokugogaku` |
| 作曲者名 | `sakkyokushamei` |

Proper-name exceptions in §6.9 can override this general suffix rule.

---

## 7. `hen`, `shō`, `kō`, and `ten` written separately (§6.6.2.1)

Write the following suffixes separately from the preceding word when used in the specified functions:

- `hen` (`編`, `篇`) — sections of books
- `shō` (`抄`, `鈔`) — excerpts or commentaries
- `kō` (`考`, `稿`) — treatises or drafts
- `ten` (`展`) — exhibitions

### Examples

| Japanese | Romanization |
|---|---|
| 君が代考 | `Kimigayo kō` |
| 戦前編 | `senzen hen` |
| 美人画展 | `bijinga ten` |
| 戦前戦後編 | `senzen sengo hen` |
| 日本食肉史抄 | `Nihon shokunikushi shō` |
| 日本印書考 | `Nihon insho kō` |
| 支那書誌学稿 | `Shina shoshigaku kō` |
| 東西美術交流 300 年展 | `Tōzai bijutsu kōryū 300-nen ten` |
| 横浜市史稿 | `Yokohama shishi kō` |

---

## 8. Exception: treat the suffix as part of a compound (§6.6.2.2)

When it makes more sense to treat one of the above suffixes as part of an established compound, write it together with the preceding element.

### Examples

- 前編 → `zenpen`
- 私考 → `shikō`
- 草稿 → `sōkō`
- 特別展 → `tokubetsuten`
- 企画展 → `kikakuten`

### Decision point

This rule explicitly requires deciding whether the expression functions as an integrated compound rather than as a base plus the special suffix.

---

## 9. Suggested Phase 1 decision procedure

```text
Is the element a prefix?
├─ honorific 御/o/go/mi/on → join with modified element
├─ modifies katakana loan word → separate
├─ scope extends over multiple following words → separate
├─ following word remains semantically independent → separate
└─ otherwise, if separation would lose intended meaning → join

Is the element a suffix?
├─ ordinary single-element suffix → join
├─ hen/shō/kō/ten in section/excerpt/treatise/exhibition function → separate
└─ established compound using one of those elements → join
```

## 10. Automation notes

### Likely automatable

- Honorific-prefix joining after the prefix reading is identified.
- Prefix + katakana loan word separation.
- Ordinary one-element suffix joining in clearly classified cases.
- A lexicon of established `hen/shō/kō/ten` compounds and explicit examples.

### May require contextual or semantic judgment

- Whether separating a prefix would change the intended meaning.
- Whether the following word is semantically independent from the prefix.
- Prefix scope over more than one compound.
- Whether `hen`, `shō`, `kō`, or `ten` is an independent suffix or part of an established compound.

### Open questions for Phase 1

- Does UniDic expose prefix/suffix status reliably enough for initial routing?
- Can prefix scope be inferred from token structure, or does it often require phrase-level semantics?
- Which joined-prefix forms and special-suffix compounds should be placed in a lexicon?
- When ALA-LC says “in case of doubt, add a variant,” what threshold should the Skill use before producing that variant?
