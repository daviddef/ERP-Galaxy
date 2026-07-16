# Enriching the Table Listing — Research Findings

**Question:** can we get S/4 equivalents, lifecycle, keys, and transactions for all 1,985 tables?
**Short answer:** not from the current sources. Three of the four fields have **zero** coverage for Tier 2, and no amount of parsing the existing PDFs will change that. The data has to come from somewhere new — and one of those somewhere-elses is sitting on your laptop.

---

## 1. Where we actually stand

| Field | Tier 1 (217, curated) | Tier 2 (1,768, from PDFs) |
|---|---|---|
| `desc` | 217 (100%) | 1,738 (**98.3%**) ✅ |
| `plainEnglish` / `lore` | 217 (100%) | 0 (0%) |
| `keyFields` | 217 (100%) | **0 (0%)** |
| `s4status` (lifecycle) | 217 (100%) | **0 (0%)** |
| `ecc` / `s4` flags | 217 (100%) | **0 (0%)** |
| `relations` | 217 | **0 (0%)** |
| T-code mapping | 86 tables | **0 (0%)** |

Descriptions are done. Everything else you asked for is at zero for 89% of the catalogue.

---

## 2. Dead end confirmed: the T-code PDFs cannot help

I checked all 14 transaction-code documents. They are flat lists:

```
•   ME21N : This Transaction code for Create Purchase Order
```

**There is no table reference anywhere in them.** They give `tcode → description`, grouped by module. We can say "ME21N is an MM-PUR transaction"; we cannot say "ME21N reads EKKO". The 945 T-codes I parsed are a *separate catalogue*, not a join.

Worse, there is no clean systematic source for table→transaction anywhere: `TSTC` maps a transaction to its *program*, and getting from program to tables requires where-used analysis over ABAP source. **Table→T-code is inherently a curation job, not an extraction job.** It stays manual, for famous tables only.

---

## 3. Why I will not generate this from model knowledge

This is the important part.

I could produce `keyFields` for all 1,768 tables in one pass. It would look authoritative. It would also be **substantially fabricated**, and you would not be able to tell which parts.

- For the ~150 famous tables, I genuinely know the keys — but **those are already Tier 1 and already have them.** The overlap between "tables I know cold" and "tables still missing keys" is nearly empty.
- For `/TDAG/CPS_IMXMLTREE`, `T7EHS00_QUSREX`, `HRP1017`, `PA0625` — I do not know the key fields. Nobody does without looking them up.
- A plausible-looking `["MANDT","BUKRS","GJAHR"]` is the **single most dangerous output this project could ship.** A wrong description is embarrassing; a wrong primary key sends someone down a broken join in front of a client.

This session has already proven the point three times: the source PDFs had truncations I'd have paraphrased into confident nonsense, and one (`HRP1017` → "Infotype 1016") contained a **typo I nearly propagated mechanically**. Those were caught because there was a source to check against. For invented keys there would be no source, and therefore no catch.

**The `null` is the honest answer.** A reference tool that says "unknown" stays trustworthy. One that guesses is worse than useless — it's a liability with a nice UI.

---

## 4. The real sources, ranked

> **UPDATE 2026-07-16 — David has no SAP system access. Options re-researched below (§7). The DDIC path is ruled out; public reference sites are viable and verified.**

### 🥇 A live SAP system's DDIC — authoritative, exhaustive, free
This is the answer for `keyFields`, **if you have access.** SAP's own data dictionary describes every table in the system:

| Table | Gives us |
|---|---|
| `DD02L` | every table + its class (TRANSP / POOL / CLUSTER / VIEW / INTTAB) |
| `DD02T` | table short texts, by language |
| `DD03L` | **every field, with `KEYFLAG` and `POSITION`** — exactly our `keyFields` |
| `DD04T` | data element texts — the human meaning of `BUKRS` etc. |
| `TSTC` / `TSTCT` | transaction codes + texts |

One `SE16` export of `DD03L` filtered to `KEYFLAG = 'X'` gives authoritative key fields for **all 1,768 tables at once**, plus it would independently verify the 217 curated ones and settle the table-class question that my `Structure` vs `Transparent Table` filtering had to infer from a PDF column.

It also fixes a nagging gap: `DD02L` tells us definitively whether a table even *exists* in a given release — which is most of the ECC-vs-S/4 question.

**Caveats you'll know better than me:**
- **Run it on a system you're authorised to use** — a sandbox, a personal/developer edition, or a trial. Not a client's production box, and not under an engagement that forbids extraction. This is your call, not mine.
- DDIC metadata is not client business data (no customer records), but it *is* SAP's intellectual property. Field **names** are facts and low-risk (same reasoning as the descriptions). Bulk-republishing SAP's entire dictionary to a public repo is more aggressive than paraphrasing descriptions — worth a deliberate decision before it lands in git.

### 🥈 SAP Simplification List — authoritative for S/4 lifecycle
Published by SAP per release as public PDFs on help.sap.com (2020, 2021, 2022, 2023, 2025). It's the canonical statement of what changed, what's deprecated, and what replaced it.

- **We now have a strong PDF pipeline**, and these are structured documents.
- **Coverage is partial by nature** — it lists *simplification items* (a few hundred), not every table. It'll light up the tables that actually changed, which is exactly the interesting set. Everything else stays `unknown`.
- Extracting *facts* ("BSEG is superseded by ACDOCA") is fine — facts aren't copyrightable. Do not lift its prose.

### 🥉 Public reference sites (sapdatasheet.org, tcodesearch, leanx…)
Have per-table field lists. But: ~1,768 page fetches, ToS questions, and it's the same provenance problem that started this whole licensing thread. **The DDIC export is strictly better and free.** Only worth it if you have no system access at all.

---

## 5. Recommended plan

**Phase 1c — DDIC export (unblocks the most, costs the least)**
You run one export on an authorised system; I do the rest.
```abap
" SE16 / SE16N, or a tiny report + GUI_DOWNLOAD
DD03L  where TABNAME in (our 1,985)  and AS4LOCAL = 'A'
       fields: TABNAME FIELDNAME POSITION KEYFLAG ROLLNAME
DD02L  where TABNAME in (our 1,985)  and AS4LOCAL = 'A'
       fields: TABNAME TABCLASS
DD04T  where DDLANGUAGE = 'E'        " data element -> English meaning
```
→ authoritative `keyFields` at ~100% coverage, table class verified, and `FIELD_DESC` expanded well past the current 250 entries.
I can write the ABAP report or the SE16 steps — say which you'd prefer.

**Phase 1d — Simplification List parse** → `s4status` for the changed subset; everything else honestly `unknown`.

**Phase 1e — T-codes and relations** → stays curated. Not extractable. Grows with `lore`, famous tables first.

**Schema addition:** every enriched field gets a provenance marker (`source: "ddic" | "simplification-list" | "curated"`) and `unknown` is a first-class value, distinct from "not yet looked at". If the UI can't tell those apart, the tool starts lying by omission.

---

## 6. What this means for the Codex

The Codex ships **fine today** on `desc` alone — "1,985 SAP tables, offline, searchable" is a real product, and the honest one. Keys and lifecycle make it *much* better, but they are an enrichment pass, not a prerequisite. Nothing here blocks TestFlight.

---

## 7. Round 2 research — no SAP access (2026-07-16)

### ❌ Free local SAP system — ruled out, definitively
The **ABAP Platform Trial / ABAP Cloud Developer Trial** Docker image is free and runs locally, and looks like the obvious answer. It isn't:

> *"The trial is covering NetWeaver, and tables like MARA are not included because they belong to the applications (like Business Suite)."*
> *"It is an ABAP platform, not a business suite — you are not supposed to have standard tables there."*

It ships only the flight model (`SCARR`, `SPFLI`) and the EPM demo model (`SNWD_*`). **Not one of our 1,985 tables exists in it.** No `BKPF`, no `LFA1`, no `PA0147`. Dead end — and worth recording so nobody burns a weekend on a 32 GB Docker image discovering this.

A real ECC/S4 system (S/4HANA Fully-Activated Appliance via Cloud Appliance Library) needs a paid licence plus cloud hosting. Not viable.

### ❌ Bulk dataset — does not exist
No public machine-readable DDIC dump found. sapdatasheet.org publishes 557 sitemap files, but they are URL indexes only — no data export. It's per-page or nothing.

### ✅ Public reference sites — viable, and verified against known truth
Spot-checked three tables spanning the full difficulty range. **3/3 returned complete, correct key fields:**

| Table | Source | Keys returned | Verdict |
|---|---|---|---|
| `BKPF` | leanx.eu | MANDT, BUKRS, BELNR, GJAHR | ✅ matches our curated Tier 1 exactly |
| `PA0147` | leanx.eu | MANDT, PERNR, SUBTY, OBJPS, SPRPS, ENDDA, BEGDA, SEQNR | ✅ correct standard PA infotype key |
| `/TDAG/CPT_EXEMLI` | sapdatasheet.org | MANDT, SUBIDPS, MATCLASS, REGLIST, EXEMPTION | ✅ **even the obscure add-on namespace is covered** |

That `/TDAG/` hit is the important one — it's the hardest case in the catalogue, and the coverage held.

**`robots.txt` permits it on all three:**
- `sapdatasheet.org` — `Disallow: /download/` only; table pages allowed.
- `leanx.eu` — `Disallow: /wp-admin/` only.
- `tcodesearch.com` — **explicitly allows `Anthropic-ai` and `GPTBot`**, while blocking `CCBot`/`Omgili`.

**Caveats:**
- **Volume:** ~1,768 fetches. Must be politely rate-limited (~1 req/sec ≈ 30 min) — these are small sites, not CDNs.
- **Staleness:** sapdatasheet's sitemaps show `lastmod 2020-09-27`. Fine for `keyFields` (primary keys are stable across releases) but **not** a source of truth for current S/4 status.
- **Licensing:** field *names* are facts (`BKPF`'s key is `MANDT, BUKRS, BELNR, GJAHR` — a fact about SAP, not creative expression). Same reasoning that cleared the descriptions. We take the fact, never the prose.
- **Accuracy:** these sites are themselves derived from a real DDIC. Verified 3/3, but this is second-hand data — mark provenance `source: "public-reference"`, not `"ddic"`, so a future reader knows it wasn't read from a system.

---

## 8. Execution results (2026-07-16) — and a serious finding

### 🔴 The curated Tier 1 `keyFields` do not survive verification

I harvested all **217 curated tables** from sapdatasheet.org and compared to the hand-authored keys in the HTML. This was meant to validate the *scraper*. It ended up impeaching the *curated data*.

| Result | Count |
|---|---|
| Exact match | **99 (45.6%)** |
| Mismatch | 106 |
| No keys returned | 12 |

Anatomy of the 106 mismatches:

| Pattern | Count | Reading |
|---|---|---|
| Scraped is a strict **superset** of curated | 49 | curated looks **abridged** |
| Genuinely divergent | 46 | one side is wrong |
| Scraped is a subset | 8 | scraper may be wrong |
| Same fields, different **order** | 3 | key order matters — one is wrong |

**Spot-checks point at the curated data, not the scraper:**

- `BSAD` curated `[MANDT,BUKRS,KUNNR,GJAHR,BELNR,BUZEI]` vs scraped `[…,UMSKS,UMSKZ,AUGDT,AUGBL,ZUONR,…]`. BSAD is a *cleared-items* index — the clearing fields **are** in its real key. Curated looks like a hand-written "logical" key, not the DDIC key. Same story for `BSAK`, `BSID`, `BSAS`.
- `ANKT` curated `[MANDT,ANLKL,SPRAS]` vs scraped `[MANDT,SPRAS,ANLKL]` — **order differs**, and order is part of a primary key.
- `BUT000` curated `MANDT` vs scraped `CLIENT` — likely an ECC-vs-S/4 release difference, i.e. *both* right for their release. Which means **release matters and neither dataset records it.**

**This is unresolved.** I could not obtain the independent second source (leanx.eu) needed to adjudicate — the session hit its limit. **Do not treat either key set as trustworthy until a tiebreak is run.** The plan (`§7`) assumed the curated 217 were ground truth; that assumption is now dead.

### ⚠️ Simplification List coverage is far lower than hoped

Parsed the official 1,482-page S/4HANA 2023 Simplification List → 441 items → **6 of 8 batches extracted** (2 failed on the session limit) → 364 raw facts across 264 distinct tables.

**But only 43 of those tables are in our catalogue** (32 Tier 1, 11 Tier 2) — about **2%** of 1,985.

| Status | Count |
|---|---|
| compat_view | 16 |
| replaced | 14 |
| changed | 8 |
| deprecated | 3 |
| unchanged | 2 |

The extractions themselves are good and evidence-backed (`MKPF`/`MSEG` → replaced by `MATDOC`; `GLFUNCT` → `ACDOCA`; `COEP` → `ACDOCA`). But the reach is small, because the Simplification List discusses the big process-level tables, and our Tier 2 is mostly HR/EHS config tables that SAP never wrote a simplification item about.

**Honest conclusion:** `s4status` will be populated for a few dozen tables, not for 1,985. Everything else stays `unknown` — which is the truthful answer, since "no simplification item exists" genuinely is *not* the same as "unchanged".

### Verdict

| Field | Path | Coverage | Status |
|---|---|---|---|
| `desc` | PDFs (done) | 98.3% | ✅ shipped |
| `keyFields` | public reference sites | ~high, verified 3/3 | needs go-ahead (outward-facing) |
| `s4status` | SAP Simplification List PDFs | partial by design | ✅ legitimate, do first |
| table→T-code | **nothing** | 0% | curation only, famous tables |
| `relations` | **nothing** | 0% | curation only |

Sources: [Simplification List for SAP S/4HANA 2023](https://help.sap.com/doc/c34b5ef72430484cb4d8895d5edd12af/2023/en-US/SIMPL_OP2023.pdf) · [SAP Help Portal — Simplification Lists](https://help.sap.com/docs/search?q=sap+simplification+list&locale=en-US&format=pdf&product=SAP_S4HANA_ON-PREMISE) · [ABAP Platform Trial image docs](https://github.com/SAP-docs/abap-platform-trial-image) · [SAP Community — trial has no standard tables](https://community.sap.com/t5/application-development-discussions/abap-trial-trial-version-do-not-have-standard-tables/td-p/12064151) · [DD03L — Table Fields](https://www.sapdatasheet.org/abap/tabl/dd03l.html)
