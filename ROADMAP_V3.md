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

**3. Movement-type / document-type decoder.** "What does BWART 101 mean?" is a distinct, unserved question. Standard code sets only (T156, T003) — **not** client-configured domains like condition types, where there's no universal answer. Bounded public dataset. *Medium effort, strong differentiation.*

**4. Deeper Simplification List parse + 2025 release.** ⭐ *Research-confirmed and verified by hand.* The SAP Note number, successor object, compat-view status and conversion steps for every verdict are **already in the PDF we parse** — we just extract the verdict quote and drop the rest. Deepen the parser + repoint at the 2025 PDF (~85 more items). Turns 218 verdicts into 218 mini-playbooks. No new data source, no licensing question. See §research below.

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
