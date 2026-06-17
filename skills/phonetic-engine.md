---
name: phonetic-engine
version: "1.0"
last_updated: "2025-07-15"
description: >
  Phonetic and phonological analysis. IPA transcription, Soundex/Metaphone
  double-coding, tonal analysis (Mandarin 4 tones), syllable structure.
  Applied to species name matching across languages and OCR errors.
runAs: inline
---

# 🎵 Phonetic Engine — 语音学/音律分析引擎

> *"Ochetobius" and "Ochetobibus" are different strings but the same phonemes.
> This skill hears what OCR cannot see.*

---

## PREFLIGHT

Before phonetic analysis, **preserve the original string exactly** — do not
phonetically normalize it first. The distance between the original and its
phonetic representation is diagnostically valuable.

---

## CORE TOOLS

### 1. IPA TRANSCRIPTION

```
Latin:     Ochetobius elongatus
IPA broad: /ˌɒkɪˈtoʊbiəs ˌiːlɒŋˈɡɑːtəs/
```

Phonetic neighbors are within IPA edit distance ≤2, capturing near-homophones
that string distance misses:

```
Ochetobius  → /ɒkɪtoʊbiəs/
Ochetobibus → /ɒkɪtoʊbɪbəs/  (IPA distance: 1 — [i]→[ɪ] vowel shift)
```

String distance: 2 ("ius"→"ibus"). Phonetically: neighbors.

### 2. SOUNDEX + METAPHONE DOUBLE-CODING

```
Ochetobius → Soundex: O231 (aggressive, high recall) | Metaphone: OXTBS (precise)
Double-code: O231::OXTBS
```

- **Both match** → near-certain same entity
- **Soundex-only** → verify with additional evidence
- **Neither** → escalate to semiotics-engine

```
Ochetobius  → O231::OXTBS  ← double-code match → HIGH
Ochetobibus → O231::OXTBS  ← double-code match → HIGH (same entity!)
Ochetobamus → O231::OXTPMS ← Soundex only → MEDIUM
```

### 3. MANDARIN TONE ANALYSIS

4 tones (+ neutral). Same syllable, different tone = different character.

```
guǎn (tone 3, 鳤 — Ochetobius fish genus)    guān (tone 1, 关 — to close)
guǎn (tone 3, 管 — tube)                     guàn (tone 4, 贯 — to pierce)
```

- Same tone + syllable → homophone, possible same-species reference
- Different tone + syllable → different character, possible OCR/IME error
- Untoned pinyin → **ambiguous** — disambiguate by context or radical

### 4. OCR PHONETIC ERROR MODEL

OCR errors = visual confusion producing phonetically similar output:

| Visual | Phonetic outcome | Example |
|--------|------------------|---------|
| rn → m | /rn/ → /m/ | "cornu" → "comu" |
| cl → d | /kl/ → /d/ (cluster collapse) | "clarus" → "darus" |
| i → l | /ɪ/ → /l/ (vowel→consonant) | "lineatus" → "llneatus" |
| vv → w | /v/ → /w/ | "novus" → "nowus" |

Orthographically predictable, phonetically recoverable.

---

## PHONETIC SEARCH PIPELINE

```
Input: name string (possibly OCR-corrupted)
  Step 1: Preserve original
  Step 2: IPA transcription
  Step 3: OCR variants (← cognitive-search-engine/variant_generator.py)
  Step 4: Double-code all variants (Soundex + Metaphone)
  Step 5: Cluster (IPA ≤2 OR double-code match)
  Step 6: Search centroids against canonical databases
  Step 7: Score — Double-code+IPA0→HIGH | Double-code+IPA1→MED-HIGH
                 Soundex-only+IPA2→MED | No match+IPA>2→LOW (human review)
```

---

## WHEN → THEN decision rules

```
WHEN exact string search returns 0 results
  → Generate phonetic variants → IF double-code match → HIGH confidence
  → IF Soundex-only → flag for review, MEDIUM confidence
  → IF no match → escalate to semiotics-engine

WHEN Chinese name is untoned pinyin
  → Flag "ambiguous: tone disambiguation required"
  → Generate all 4 tonal variants → cross-reference fishbase.cn

WHEN OCR error suspected (e.g., "Ochetobibus")
  → Apply OCR→phonetic error model → match against known genera
  → Confirm via orthographic proximity + taxonomic plausibility

WHEN matching Latin ↔ Chinese names
  → IPA for both → distance ≤3 = candidate → cross-validate taxonomically

WHEN Soundex and Metaphone disagree
  → Metaphone wins for precision; Soundex-only = suggestion, not conclusion
  → Require additional evidence (author, year, geographic range)
```

---

## CAPABILITY REFERENCES

- **Variant generation**: `cognitive-search-engine/variant_generator.py` provides OCR confusion matrix; phonetic-engine adds the *phonetic interpretation* layer.
- **Semiotic resolution**: hand off unresolved candidates to `semiotics-engine` for signifier→signified chain reconstruction.
- **Taxonomic verification**: delegate final confirmation to GBIF/Eschmeyer/FishBase APIs.

---

## CLOSING PRINCIPLE

> *Script encodes sound. When script breaks (OCR, misspelling, transliteration), sound survives. Listen to what the text was trying to say.*
