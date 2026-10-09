# Verbs, Adjectives, Adverbs, Conjunctions, and Particles

**Source:** ALA-LC Romanization Table: Japanese (2022), §6.8  
**Phase:** Phase 1 — Skill rules  
**Purpose:** Apply ALA-LC word-division rules to parts of speech other than the noun-centered compounds covered earlier in §6.

> **Unofficial restatement.** This file is an unofficial, operational summary of the ALA-LC Romanization Table: Japanese (2022). It is not the official table; the source document always takes precedence. See NOTICE.md at the repository root.

> Several rules in this section depend on grammatical function. Surface form alone is not always sufficient; the same expression can be divided differently when its syntactic or semantic role changes.

## 1. Verbs with auxiliaries (§6.8.1.1)

Write simple and compound inflected or contracted verbs, together with their auxiliaries, as single words.

### Examples

- 生きてる → `ikiteru`
- 支配する → `shihaisuru`
- ドライブする → `doraibusuru`
- 読み得る → `yomiuru`
- なし得ない → `nashienai`
- 関する → `kansuru`
- 思い出す → `omoidasu`

### Decision point

Not every following verb-like form is treated as an auxiliary under ALA-LC; §6.8.1.2 and §6.8.1.3 provide important separations.

---

## 2. Verbs with modifiers (§6.8.1.2)

Write verbs separately from adverbs or inflected adjectives that modify them.

### Examples

| Japanese | Romanization |
|---|---|
| どう考える | `dō kangaeru` |
| そうする | `sō suru` |
| こうなる | `kō naru` |
| 強くなる | `tsuyoku naru` |
| 美しくなりたい | `utsukushiku naritai` |
| 生きていた | `ikite ita` |
| 帰って来る | `kaette kuru` |
| やって見よう | `yatte miyō` |
| 戴いていきます | `itadaite ikimasu` |
| 言っているのだが | `itte iru no da ga` |

### Decision point

The Skill must distinguish an integrated/contracted verb from a separate modifying or following verbal element.

---

## 3. Honorific, potential, and similar auxiliaries (§6.8.1.3)

Write honorific auxiliaries, potential auxiliaries such as `dekiru`/`dekinai`, and similar auxiliary-like forms **separately** from the other part of the verb.

### Examples

- 我慢出来るか → `gaman dekiru ka`
- 我慢出来ません → `gaman dekimasen`
- 死にたまう / 死にたもう → `shini tamau`, `shini tamō`
- 次回の主催地は日本らしい → `jikai no shusaichi wa Nihon rashii` when `らしい` is an auxiliary meaning “it appears to be Japan”
- よろしくお願い致します → `yoroshiku onegai itashimasu`
- 読ませて頂きます → `yomasete itadakimasu`

### Decision point

This rule can conflict with a generic morphological notion of “auxiliary.” Follow the ALA-LC examples and functions rather than blindly concatenating all auxiliary-tagged tokens.

---

## 4. Adjectives (§6.8.2)

Write compound inflected adjectives and adjectival verbs as single words.

### Examples

`ikanaru`, `miryokuaru`, `teikōnaki`, `dōdōtaru`, `osorubeki`, `ayamariyasui`, `ureshii`, `adokenai`, `usoppoi`

The source gives:

- 誤った作法 → `ayamatta sahō`
- 誤りやすい作法 → `ayamariyasui sahō`

### Semantic contrast: `らしい`

- 日本らしい風景 → `Nihonrashii fūkei` when `らしい` is an adjective meaning **Japan-like**.
- Compare §6.8.1.3: `Nihon rashii` when `らしい` is auxiliary-like and means **it appears to be Japan**.

### Decision point

This is a clear example where semantic function changes word division.

---

## 5. Adverbs and conjunctions (§6.8.3)

Write compound adverbs and conjunctions as single words.

### Examples

- 特に → `tokuni`
- 並に → `narabini`
- 共に → `tomoni`
- 遂に → `tsuini`
- 如何に → `ikani`
- 直ぐに → `suguni`
- 又は → `matawa`
- 或いは → `aruiwa`
- その後 → `sonogo`
- その後 → `sonoato`
- これから → `korekara`
- それでも → `soredemo` when used as a conjunction meaning **nonetheless**

A preferred reading decision such as `sonogo` versus `sonoato` belongs to the reading-selection rules; this section governs word division once the reading is chosen.

---

## 6. Particles (§6.8.4)

Write particles separately from other words and separately from each other.

Exception: lexicalized medial `の` compounds are governed by §6.2.2.

### Examples

| Japanese | Romanization |
|---|---|
| 幸福への道 | `kōfuku e no michi` |
| 絵は誰にでも描ける | `E wa dare ni de mo kakeru` |
| そういう本を読むのが楽しい | `Sō iu hon o yomu no ga tanoshii` |
| 雲の上に | `kumo no ue ni` |
| うれしいな | `ureshii na` |
| 何だろうか | `nan darō ka` |
| さらりと | `sarari to` |

### Semantic contrast: `それでも`

- `soredemo` when it is the conjunction “nonetheless.”
- `sore de mo` when it is pronoun + particle + particle (“that or the like”).

### Semantic contrast: `誰か`

- `dareka` when it means “somebody” (§6.2.1).
- `dare ka` when used in a question as “who” + particle `ka`.

### Decision point

These distinctions require grammatical/semantic classification, not character-level spacing.

---

## 7. Contracted `no` (§6.8.4)

In some expressions, `no` is contracted to `n`. Keep the contracted element separate according to the examples.

- 頭ン中 → `atama n naka`
- オレん家 → `ore n chi`
- そうだったんだ → `sō datta n da`

---

## 8. Suggested Phase 1 decision procedure

```text
Classify the grammatical function of each non-noun element.
↓
For verbs:
  integrated inflected/contracted verb + auxiliary? → one word
  modifier/following verb or adjective? → separate
  honorific/potential/similar auxiliary? → separate
↓
For adjectives/adjectival verbs:
  compound inflected form? → one word
↓
For adverbs/conjunctions:
  established compound form? → one word
↓
For particles:
  separate each particle, unless another rule establishes lexicalization
↓
If surface form permits more than one grammatical interpretation
(e.g. 誰か, それでも, らしい), emit a semantic judgment point.
```

## 9. Automation notes

### Likely automatable

- Separating tokens confidently identified as particles.
- Many ordinary inflected/contracted verb patterns if analyzer features match the ALA-LC categories.
- A lexicon of compound adverbs/conjunctions.
- Contracted `n` handling when the source form is explicitly present.

### May require contextual or semantic judgment

- `dareka` versus `dare ka`.
- `soredemo` versus `sore de mo`.
- adjectival `Nihonrashii` versus auxiliary `Nihon rashii`.
- Integrated auxiliary versus separately written verb/auxiliary-like element.

### Open questions for Phase 1

- Which UniDic POS/conjugation fields correlate reliably with the distinctions in §§6.8.1.1–6.8.1.3?
- Can `らしい` function be identified deterministically from analyzer features and dependency context?
- How often does particle separation disagree with raw MeCab/UniDic tokenization?
- Which compound adverbs/conjunctions should be lexicalized explicitly rather than delegated to AI judgment?
