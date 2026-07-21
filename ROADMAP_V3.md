# ERP Galaxy — Roadmap v3

**Status (2026-07-20):** **LIVE on the App Store** (v1.0, build 5). 1.0.1 (build 9) staged and ready to submit.

---

## Where we actually are

| | |
|---|---|
| App Store | ✅ v1.0 **READY_FOR_SALE** — passed review incl. Guideline 2.1 round |
| 1.0.1 | ⏳ build 9 attached, "What's New" written, **awaiting submit** (your call) |
| Curated graph | 217 tables, 411 relationships (deduped), business + FK edges |
| Codex index | **1,975 tables**, 98%+ with primary keys, foreign keys |
| **S/4 migration verdicts** | **218** (was 59) — the differentiator |
| Lore (fun mode) | 132 + 217 curated |
| Native | Spotlight (2,192 records), Table-of-the-Day widget, join finder |
| Data collection | **zero** — no account, no network, no ads |

### What shipped since v1.0 went live (all in 1.0.1 / build 9)
- Migration verdicts **59 → 218**
- **Join finder** — every table shows what it joins to and the `ON` fields
- Node label contrast fix (solid fills, dark ink)
- Migration Journey layout fix (was collapsing to one char per line)

---

## The strategic picture — unchanged and validated

The market test's verdict held up through a real review cycle: **the moat is the migration story, not the lookup.** Apple did *not* reject on Guideline 4.2 (the standing risk) — the offline, native, zero-collection posture carried it. That posture is now proven, not theoretical, and it's worth protecting:

- **Ads still not recommended.** AdMob forces Device ID / Advertising Data / IP onto the privacy label and undercuts the 4.2 defence we just cleared. If monetising, a one-off **Pro IAP** keeps the clean posture — consultants expense tools.
- **The deadline is the wedge.** ECC mainstream maintenance ends **31 Dec 2027**. Everything that deepens "what happens to my tables" rides that.

---

## Next steps, ranked

### Tier 1 — do next (high value, data in hand or cheap)

**1. Submit 1.0.1.** It's staged. One action. Gets the 218 verdicts + join finder to real users. *Blocked only on your go-ahead.*

**2. Migration scenario playbooks.** BP/CVI conversion and material-number extension are the two migration pains that are *documentable generic knowledge*, not client-specific remediation (per practitioner research). Curated "scenario" pages — the tables involved, what breaks, what to check — extend the verdict schema we already have. Public SAP Community blogs are the source. *Medium effort, pure curation, deepens the moat.*

**3. Movement-type / document-type decoder.** ✅ **Complete.** "What does BWART 101 mean?" is a distinct, unserved question. Standard code sets only (T156, T003) — **not** client-configured domains like condition types, where there's no universal answer.

- **Movement types (T156/BWART):** 91 standard types + derived reversals.
- **Document types (T003/BLART):** 10 types, verbatim from [SAP Help — Document Types](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/a8aaa72cb39a48528b39b61623c15baa/7b47d153da7e4308e10000000a174cb4.html) (S/4HANA 2025 FPS01), "Document Types in the Standard System". SAP's own page calls these "the most important" — there is no exhaustive public list because **BLART is client-configurable**, so the panel says so explicitly rather than implying the set is complete.

*Correction: this item was previously marked done when only the movement-type half had shipped.*

**4. Deeper Simplification List parse + 2025 release.** ⭐ *Research-confirmed and verified by hand.* The SAP Note number, successor object, compat-view status and conversion steps for every verdict are **already in the PDF we parse** — we just extract the verdict quote and drop the rest. Deepen the parser + repoint at the 2025 PDF (~85 more items). Turns 218 verdicts into 218 mini-playbooks. No new data source, no licensing question. See §research below.

### Tier 2 — the next body of work

> **Note on numbering.** There was no Tier 2 in this document. The original Tier 2 item was
> promoted into Tier 1 as item 4 and shipped, so "move to Tier 2" had nothing to move to.
> This section defines it.

**5. Field-level S/4 schema deltas.** ✅ **Shipped, in the form the research supports.**

**The research verdict: a full per-table field diff is blocked, and not on difficulty.**

| Source | Verdict |
|---|---|
| **erpexplorer.com** | Only public source with **both** ECC and S/4 field lists per table (name, data element, type, length, decimals, key flag). **But** its `robots.txt` names `ClaudeBot`, `GPTBot`, `CCBot`, `Google-Extended` and others with `Disallow: /`, and the ECC↔S/4 "Differences" view is their **paid Pro feature**. Scraping it to build a competing free feature is a stated position, not a grey area. **Declined.** |
| sapdatasheet.org | ECC only, single version, no S/4 side |
| leanx.eu / se80.co.uk | ECC only / Cloudflare bot challenge |
| GitHub DD03L dumps | None found for ECC+S/4 |
| SAP Simplification Database (SYCM/ATC) | Real and field-aware, but S-user gated — not public |

**What we shipped instead, and it's the better feature anyway:** the changes that actually break
code are *systemic* — whole domains, not one table — and SAP documents them in the Simplification
List we already parse. Six changes, every figure and Note number from SAP's own 2025 PDF:

| Change | From → To | Note |
|---|---|---|
| Material number | `CHAR 18` → `CHAR 40` | 2267140 |
| Currency amounts (AFLE) | 9–22 digits → `23` digits | 2628654 |
| SD document category | `VBTYP CHAR 1` → `VBTYPL CHAR 4` | 2267306 |
| Object list number | `INT4` → `INT8` *(type, not length)* | 2580670 |
| Segment | `16` → `40` chars | 2522971 |
| Season / Collection / Theme | → `10` chars | 2624475 |

Attached to tables two ways: tables SAP **names** in the item text, and tables carrying the field
as a **key** field (MATNR hits 114). Both the opt-in switches and the coverage limit are stated in
the app — we hold key fields, not full field lists, so MSEG carries MATNR but won't match. The
panel says that rather than implying completeness.

**Still open:** per-table added/removed/renamed fields beyond these systemic changes. That needs
either live DDIC access to both an ECC and an S/4 system, or a licensing conversation with
erpexplorer — not scraping.

**6. Fill the `lore` gap.** 132 of 2,001. Fun mode is the app's personality and it's mostly
empty outside the curated set. Pure authoring, zero sourcing risk, never blocks a release.

**7. Resolve the known data debt.** The 12 tables where key sources disagree, and the ~150
`moduleInferred` assignments guessed from name prefixes. Small, unglamorous, and it removes the
soft spots most likely to embarrass the app in front of someone who knows the system.

**8. Monetisation — Pro IAP, not ads.** Deferred deliberately, not declined. Ads would force
Device ID / Advertising Data / IP onto a privacy label whose emptiness is currently the
listing's strongest asset and part of the Guideline 4.2 defence already cleared. Revisit once
item 5 lands, because field-level data is the thing worth paying for.

### Tier 3 — declined, with reasons
- **Fiori app → T-code mapping.** Verified to exist (unauthenticated OData) but SAP's API Policy explicitly forbids the bulk extraction it would need. Hand-curating a bounded set for our 86 existing T-codes is the only defensible path, and it's labour-heavy. The classic library also sunsets Dec 2026.
- **CDS view → table catalogue.** No public machine-readable source; the mapping only lives in a live system or a competitor's paid product.
- **Certification quiz mode.** Crowded with exam-dump sites, brand risk, doesn't use the graph. No.
- **Custom-code remediation.** Inherently per-tenant (scans a client's Z-code) — structurally impossible for an offline no-account app.
- **Other platforms (Dynamics/Oracle/etc).** Dynamics remains the strongest second platform (CC-BY, relationships included) — but *after* the SAP migration wedge is fully proven. Cheap-to-copy data doesn't deepen the moat; the migration curation does.

---

## S/4 data-depth research — findings (verified by hand)

**Headline: the biggest upgrade needs no new data source. We already have the richer data — we just don't parse it yet.**

Our current parser pulls only the *verdict quote* from each Simplification List item. But I confirmed by re-downloading and grepping the live PDF that every item carries a **structured template** we're throwing away:

| Field in the PDF | Count (2025 PDF) | What it gives a user |
|---|---|---|
| `Related Notes` (SAP Note #) | **806 items** | the citable SAP Note for that change |
| `Required and Recommended Action` | **531 items** | the actual conversion steps |
| `How to Determine Relevancy` | **246 items** | how to check if it affects you |
| Compat-view / DDL / backup names | `BSIS_BCK`, `COSP_BAK`, `_DDL` ×79, `MATDOC` ×84 | the successor object + whether reads still work |

So "BSEG → ACDOCA" could become "BSEG → ACDOCA, reads preserved via compat view, custom code see **SAP Note 1976487**, run X before conversion." That's the difference between a fact and a *playbook*, and it's all in the file.

### 1. Newer Simplification List — VIABLE, and easy
**Verified downloadable:** [SIMPL_OP2025.pdf](https://help.sap.com/doc/0df2ffddebab40cf9338488b2f18dc41/2025.latest/en-US/SIMPL_OP2025.pdf) — 1,514 pages, rolling doc (currently covers S/4HANA 2025 FPS01). SAP moved to a **2-year cadence**, so there is no 2024 or 2026 — 2025 is current, 2027 is next. It has **~85 more items** than our 2023 source. Swapping the source URL and re-running the pipeline is nearly free.

### 2. Simplification Item Catalog (structured UI/API) — BLOCKED
`launchpad.support.sap.com/#/sic` is **403 without an S-user** (support contract). But its structured item IDs/categories are **duplicated in the public PDF** (`SI27: MasterData_BP` etc.), so we lose nothing by staying with the PDF.

### 3. Readiness Check outputs — PARTIAL (taxonomy generic, numbers client-specific)
The *category taxonomy and per-item reference-table mapping* ("SI27 checks KNA1") is generic and referenceable. The actual numbers (which tables are big, which items are relevant) are 100% client-specific. Reference the taxonomy, never the numbers.

### 4. Per-table detail (Note #, successor CDS, compat view, steps) — VIABLE
See headline. All present in the PDF we already use. **This is the highest-leverage next step.**

### 5. Data-volume "biggest tables" — PARTIAL, and a trap
There is **no authoritative public ranking** — a real Readiness Check showed the top-20 dominated by that customer's workload (billing tables), with BSEG *not even in the top 20*. So: never claim a hard ranking. At most, flag qualitatively "commonly cited high-volume/archiving candidate" for the handful (BSEG, GLPCA, COEP, MSEG, CDPOS, ACDOCA) that recur across public examples.

### 6. Custom-code impact — PARTIAL (generic half is in the PDF; the scan is client-side)
No downloadable "table X → remediate" file exists without a support contract and a live ATC scan. But the *generic* half — "code reading MSEG should know MSEG→MATDOC, see Note X" — is the same PDF item text. We can state the guidance; we can't detect *whose* code needs it.

### The one clear action
**Deepen the parser to capture `Related Notes` + `Required and Recommended Action` per item, and repoint it at the 2025 PDF.** No new source, no licensing question (facts, our own prose — same posture as everything else), turns 218 verdicts into 218 mini-playbooks plus ~85 new items. This is now **Tier 1, item 4**.

---

## Open items
- 12 tables where the two key sources disagree (kept curated, not guessed)
- ~150 module assignments on migration tables are `moduleInferred` (from name prefixes)
- `lore` at 132/1,975 — grows incrementally, never blocks a release
- Privacy policy depends on the repo staying public (GitHub Pages)
