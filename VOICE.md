# SAP Galaxy — Voice Guide & Rewrite Pilot

**Decision (2026-07-16):** descriptions get the fun treatment, not consultant-speak.
**Constraint:** paraphrase the source, never invent. Fun ≠ made up.

---

## The voice, reverse-engineered from the existing curated tables

The `plainEnglish` field already has a voice. It is **not** jokes. It's a smart colleague explaining over coffee:

- **Analogy that lands:** *"If BSEG is the body, BKPF is the envelope."*
- **Caps for emphasis, sparingly:** *"THE big table of S/4HANA"*, *"the BIGGEST table in any ECC6 system"*
- **A practical warning tucked in:** *"Primary key includes ledger (RLDNR) — always filter by it."*
- **Short sentences. Fragments are fine.**
- **Speaks to a person doing a job**, not to an auditor.

Rules: no gags, no puns for their own sake, no exclamation marks. Personality comes from *clarity + a point of view*, not from trying to be funny. Every sentence must still be **true**.

---

## The problem this pilot exposes

The existing entries are great **because the author knew those tables cold**. BKPF, BSEG, ACDOCA are famous. Our 1,951 new tables are mostly not.

Voice quality is a direct function of source richness. Three tiers fall out naturally:

### Tier A — Famous tables (~150 of the new 1,951)
LFA1, EKKO, MKPF, T003T. Well-documented, genuinely known. Full BKPF-grade treatment.

> **LFA1** — *source: "Vendor master (general section)"*
> The vendor's business card. One row per vendor, and the bits that stay true no matter which company code or purchasing org you're in — name, address, tax numbers, account group. The company-code-specific money stuff lives next door in LFB1.

> **EKKO** — *source: "Purchasing Document Header"*
> The cover sheet of a purchase order. One row per PO: who you're buying from, when, under what terms. The actual "what you're buying" lines are in EKPO. Classic header/item split — SAP does this everywhere once you spot it.

> **MKPF** — *source: "Header- Material Document"*
> Every time stock physically moves, SAP writes a material document. This is its header — when it happened and who did it. The what-and-how-much is in MSEG. Think of MKPF as the receipt, MSEG as the line items on it.

### Tier B — Ordinary config/text tables (~1,500)
Source gives a real description, but there's no lore. Light touch: clear, human, one useful orienting sentence. **This is where most of the 1,951 land.**

> **T003T** — *source: "Document type texts"*
> The text table for document types. Whenever a screen shows "Vendor Invoice" instead of the cryptic `KR`, this is where that label came from. One row per document type per language.

> **T049B** — *source: "Control parameters for autocash"*
> Config knobs for autocash — the automatic clearing of incoming payments. Someone in FI set these once and everyone forgot. You'll only meet this table when autocash misbehaves.

Note: even here, "Someone set these once and everyone forgot" is a *characterisation of a config table*, not an invented fact. That's the line.

### Tier C — Thin or third-party (~300)
`/TDAG/CPT_EXEMLI` (*"CP: Exemption Limits"*), `/TDAG/RCSA_TPL` (*"obsolete"*).

We do not know these tables. Trying to be fun here produces **confident nonsense** — the exact failure mode that makes a reference tool worthless. Honest options:

> **/TDAG/CPT_EXEMLI**
> Exemption limits for Compliance for Products (CP). Part of the TechniData EHS add-on, not core SAP.

Flat, factual, short. **Recommended: name + literal source, no personality.** A dry-but-correct entry is a working reference. A witty-but-wrong one is a liability — and at 300 tables, nobody notices the errors until a consultant does, in front of a client.

---

## Recommendation

**Fun tone, applied honestly — graded by what we actually know:**

| Tier | Count | Treatment |
|---|---|---|
| A — famous | ~150 | Full voice. Analogies, opinions, warnings. |
| B — ordinary | ~1,500 | Light voice. Clear + one orienting sentence. |
| C — thin/third-party | ~300 | Factual only. No personality. |

The app still *reads* fun, because Tier A is what people actually look up — LFA1 and EKKO get browsed a thousand times more than `/TDAG/CPT_EXEMLI`. The galaxy's bright stars carry the personality; the background stars just need to be accurate.

**The alternative — forcing jokes onto all 1,951 — makes the app worse, not funnier.** Padding beyond the source *is* inventing, and invented SAP facts are how a consultant gets embarrassed in a client meeting. That is the one thing this tool exists to prevent.

---

## Open question for David

Does Tier C get **flat prose** (recommended), or should those ~300 be **excluded** from the Codex entirely so every table you see has real personality? Smaller, better dataset vs. bigger, patchier one.
