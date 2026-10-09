# Long Vowels, Adjacent Vowels, and Morpheme Boundaries

**Source:** ALA-LC Romanization Table: Japanese (2022), §2.5  
**Phase:** Phase 1 — Skill rules  
**Purpose:** Determine whether adjacent vowels are represented with macrons, doubled `i`, or separate vowel letters.

> **Unofficial restatement.** This file is an unofficial, operational summary of the ALA-LC Romanization Table: Japanese (2022). It is not the official table; the source document always takes precedence. See NOTICE.md at the repository root.

> These rules operate on a selected reading. Correct results may depend on morpheme boundaries, not only on the kana sequence.

## 1. Lengthening bar `ー` (§2.5.1)

A vowel lengthened with the lengthening bar `ー` is romanized with a macron.

### Examples

| Japanese | Romanization |
|---|---|
| コンピュータ | `konpyūta` |
| ニューヨーク | `Nyū Yōku` |
| ケンタッキー | `Kentakkī` |
| ウィーク | `wīku` |
| ビードロ | `bīdoro` |
| そーっと | `sōtto` |

### Automation note

This is strongly rule-based once the kana sequence is known.

---

## 2. Long vowels ending in `u` (§2.5.2)

When `u` completes a long vowel within the same relevant unit, represent the long vowel with a macron rather than spelling the `u` separately.

### Examples

| Japanese | Correct | Not |
|---|---|---|
| 孔子 | `Kōshi` | `Koushi` |
| 労働 | `rōdō` | `roudou` |
| 情報 | `jōhō` | `jouhou` |
| 昨秋 | `sakushū` | `sakushuu` |
| 流水 | `ryūsui` | `ryuusui` |
| お父さん | `otōsan` | `otousan` |
| トウサン | `tōsan` | `tousan` |

This general rule is subject to the morpheme-boundary exception below.

---

## 3. Long `a`, `e`, and `o` (§2.5.3)

Long `a`, `e`, and `o` vowels are represented with macrons.

### Examples

| Japanese | Correct | Not |
|---|---|---|
| お母さん | `okāsan` | `okaasan` |
| ああ播磨灘 | `Ā Harimanada` | `Aa Harimanada` |
| バアサン | `bāsan` | `baasan` |
| お姉さん | `onēsan` | `oneesan` |
| 茂兵衞 | `Mohē` | `Mohee` |
| ええじゃないか | `ē ja nai ka` | `ee ja nai ka` |
| 狼 | `ōkami` | `ookami` |
| オオカミ | `ōkami` | `ookami` |
| ほおずき | `hōzuki` | `hoozuki` |
| 遠い | `tōi` | `tooi` |

---

## 4. Long `i` vowels (§2.5.4)

Long `i` is normally represented as **`ii`**, not with a macron.

Exception: when the long `i` is written with a lengthening bar `ー`, represent it as **`ī`**.

### Examples

| Japanese | Correct | Not |
|---|---|---|
| 新潟 | `Niigata` | `Nīgata` |
| 飯田 | `Iida` | `Īda` |
| お兄さん | `oniisan` | `onīsan` |
| びいどろ | `biidoro` | `bīdoro` |
| ビードロ | `bīdoro` | `biidoro` |
| 物言い | `monoii` | `monoī` |
| ジイサン | `jiisan` | `jīsan` |

### Key distinction

The same apparent long sound may be represented differently depending on how it is written:

- `びいどろ` → `biidoro`
- `ビードロ` → `bīdoro`

---

## 5. Morpheme-boundary exception (§2.5.5)

When adjacent vowels meet **across a morpheme boundary**, write the vowels separately rather than treating them as one long vowel.

In this rule, the important question is not only pronunciation but whether the vowels belong to separate meaningful units.

### Examples (§2.5.5.1)

| Japanese | Analysis | Correct | Not |
|---|---|---|---|
| 子牛 | 子 `ko` + 牛 `ushi` | `koushi` | `kōshi` |
| 長雨 | 長 `naga` + 雨 `ame` | `nagaame` | `nagāme` |
| 会社案 | 会社 `kaisha` + 案 `an` | `kaishaan` | `kaishān` |
| 本居 | 本 `Moto` + 居 `ori` | `Motoori` | `Motōri` |
| 腐れ縁 | 腐れ `kusare` + 縁 `en` | `kusareen` | `kusarēn` |

### Decision point

This is potentially one of the main boundaries between deterministic processing and semantic/morphological judgment. A kana sequence alone may not reveal the relevant morpheme boundary.

When the case involves a contracted reading, a long-established customary proper-name reading, a dialect form, or another uncertain analysis, follow the ordinary long-vowel rules (§§2.5.1–2.5.4) unless a morpheme boundary can be justified.

---

## 6. Final `う` in modern verbs (§2.5.5.2.1)

For a modern verb whose dictionary form ends in an added `う` after another vowel, treat the final `う` as a separate morpheme and write it as a separate `u`, not as a macron.

### Examples

| Japanese | Correct | Not |
|---|---|---|
| 縫う | `nuu` | `nū` |
| 問う | `tou` | `tō` |
| 思う | `omou` | `omō` |

### Automation note

If the morphological analyzer reliably identifies the verb and its inflectional structure, this may be deterministic.

---

## 7. Exception: `候` / `そうろう` (§2.5.5.2.2)

The final `う` in `候`, `候ふ`, and `そうろう` is **not** treated as a separate morpheme for this rule. Romanize the expression with long vowels:

- `候` → `sōrō`
- `候ふ` → `sōrō`
- `そうろう` → `sōrō`

Do not use `sourou`.

---

## 8. Suggested Phase 1 decision procedure

```text
Does the source use ー?
├─ yes → use a macron for the lengthened vowel
└─ no
   ↓
Is this a long i?
├─ yes → use ii
└─ no
   ↓
Do the adjacent vowels cross a justified morpheme boundary?
├─ yes → write the vowels separately
└─ no
   ↓
Is this a modern verb with final morphemic う?
├─ yes → write the final u separately
└─ no
   ↓
Is this 候 / 候ふ / そうろう?
├─ yes → sōrō
└─ no
   ↓
Apply the ordinary long-vowel macron rule
```

## 9. Automation notes

### Likely automatable

- `ー` → macron.
- Standard long-vowel conversion after the reading is fixed.
- `ii` versus `ī` when the written kana form is preserved.
- The explicit `候 / 候ふ / そうろう → sōrō` exception.

### May require contextual or morphological judgment

- Whether adjacent vowels cross a morpheme boundary.
- Whether a reading is a contracted/customary proper-name reading for which ordinary long-vowel treatment should be retained.
- Whether final `う` is functioning as the modern verb morpheme described in §2.5.5.2.1.

### Open questions for Phase 1

- Can UniDic token/lemma information reliably identify all morpheme-boundary cases needed here?
- Should the core expose explicit morpheme-boundary metadata rather than making the Skill reconstruct it?
- How should the system record a decision such as `koushi` versus `kōshi` so that the applied boundary is auditable?
