---
name: semiotics-engine
version: "1.0"
last_updated: "2025-07-15"
description: >
  Semiotic deconstruction — signifier/signified analysis, Peircean triadic model
  (representamen/interpretant/object), Saussurean dyadic model. Applied to species
  nomenclature, scientific terminology, and knowledge representation.
runAs: inline
---

# 🔣 Semiotics Engine — 符号学分析引擎

> *Every scientific name is a sign. This skill decomposes signs to find what they point to.*

---

## PREFLIGHT

Before applying semiotic analysis, **read the exact name string** (species, gene, compound)
as it appears in the source — including diacritics, hyphenation, and whitespace.
Do not "correct" it first; the error is part of the sign's history.

---

## CORE MODELS

### Saussurean Dyadic (quick decomposition)

```
SIGN = SIGNIFIER (the written/spoken form)
       +
       SIGNIFIED (the concept/referent)

Example:
  Signifier: "Ochetobius elongatus"
  Signified: the actual fish species in Cyprinidae
```

The signifier→signified mapping is **arbitrary and conventional**. When a source uses
a signifier, ask: *which signified does this author intend?* — not *which signified
does the dictionary assign?*

### Peircean Triadic (deeper decomposition)

```
REPRESENTAMEN (the name-as-encountered: "Ochetobibus elongatus" [OCR error])
       ↓
INTERPRETANT (what the reader understands: possibly Ochetobius, possibly nonsense)
       ↓
OBJECT (the actual biological entity — the fish)
```

The triadic model captures **miscommunication**: the Representamen is corrupted by OCR,
the Interpretant diverges across readers, but the Object remains invariant.
**The engine's job is to reconstruct the path from corrupted Representamen to invariant Object.**

---

## DECOMPOSITION PIPELINE

```
Exact name (as-is)
  → OCR variants (character-level: e/l, i/l, rn/m, cl/d, 0/O)
  → Orthographic variants (nomenclatural synonyms, misspellings)
  → Author network (who cites which variant? are they the same Object?)
  → Citation graph intersection (do variant strings co-occur in same paper?)
  → Chinese common-name mapping (if applicable)
  → Converge on canonical signified
```

---

## WHEN → THEN decision rules

```
WHEN exact name search returns 0 results
  → DO NOT assume the entity doesn't exist
  → Generate OCR variants (see semiotic pipeline step 2)
  → Search each variant
  → IF variant hits found → map back to canonical signified
  → Tag the original signifier as "OCR-corrupted Representamen"

WHEN two signifiers map to the same signified
  → Record as synonym pair
  → Prefer the accepted name per GBIF/Eschmeyer/Catalog of Fishes
  → Retain the variant for query expansion

WHEN a signifier has drifted across literature (same name, different concept)
  → Flag as "signified drift" — a semiotic hazard
  → Disambiguate by date range or author lineage

WHEN Chinese name and Latin name disagree
  → Prioritize Latin as canonical (nomenclatural code)
  → Record Chinese name as regional interpretant variant
  → Cross-check against fishbase.cn for resolution

WHEN author string is present (e.g., "Cyprinus carpio Linnaeus, 1758")
  → Author+year disambiguates homonyms
  → Same signifier + different author = potentially different Object
```

---

## SEMIOTIC HAZARD TAXONOMY

| Hazard | Example | Mitigation |
|--------|---------|------------|
| **OCR corruption** | Ochetobius → Ochetobibus | Variant generation + phonetic matching |
| **Homonymy** | Morus (plant genus) vs Morus (bird genus) | Author+year disambiguation |
| **Synonymy** | Barbus and Puntius — same fish, competing names | Canonical mapping via Eschmeyer |
| **Signified drift** | "species complex" meaning changes across decades | Date-stamped interpretation |
| **Inexact translation** | Chinese 鳤 → English "Elopichthys"? (actually Ochetobius) | Triangulate: Latin → GBIF → Chinese → cross-verify |

---

## CAPABILITY REFERENCES

- **Variant generation**: see `cognitive-search-engine/variant_generator.py` — the character-level OCR confusion matrix drives step 2 of the decomposition pipeline.
- **Graph resolution**: pass signifier variant clusters to `graph-search-engine` to intersect citation graphs and author networks.
- **Taxonomic canonicalization**: delegate final Object resolution to GBIF API / Eschmeyer Catalog (external, call via taxon-resolver utility).

---

## CLOSING PRINCIPLE

> *The map is not the territory, the name is not the thing, and the OCR output is not the name.* — Modified from Korzybski. Always trace the sign back to the Object.
