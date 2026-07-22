# ECC → S/4HANA: what we actually know

*A field guide built from SAP's own published position, generated from the ERP Galaxy dataset. Every count below is computed from the data, not typed in.*

---

## Why this document exists

SAP mainstream maintenance for ECC ends **31 December 2027**. Between now and then most SAP estates have to answer one question, table by table: *what happens to this when we convert?*

There is a lot of writing about S/4HANA. Most of it is either marketing, or a summary of a summary. This guide restricts itself to what SAP has actually published, and is explicit about where that runs out — because the gap between *documented* and *unknown* is where conversion projects get hurt.

---

## The five things that can happen to a table

Every verdict in this guide is one of five outcomes. They are not equally survivable, and the difference between the middle three is where most of the risk sits.

| Outcome | Tables | What it means for your code |
|---|---:|---|
| **Disappears** | 63 | Not in S/4HANA. Reads and writes both fail. |
| **Replaced** | 78 | Still present, no longer the system of record. Code compiles and returns stale or partial answers. |
| **Compatibility view only** | 59 | Reads work, writes do not. Reporting keeps running, so this is the one that surfaces late. |
| **Changed** | 37 | Survives with different structure, semantics or content. |
| **Unchanged** | 11 | SAP states it is unaffected. |

**248 tables carry a published verdict.** 238 of those cite a specific SAP Note, and 161 carry SAP's own required-action text.

### The number that matters most is the one nobody quotes

Roughly **1,972 tables have no Simplification List entry at all.**

That is not a clean bill of health. It means SAP has not published a change for them. Absence of an item is not a promise, and treating "no news" as "no change" is the single easiest way to be blindsided. Anything material to your business deserves a check regardless of whether it appears here.

---

## Tables SAP explicitly calls new

Destinations, not risks — but worth knowing, because data you are looking for has moved into them.

| Table | Held in the app |
|---|---|
| `ACDOCA` | curated |
| `CVI_CUST_LINK` | index |
| `CVI_VEND_LINK` | index |
| `EHFNDD_LISU_RT` | index |
| `FMLC_ERD` | index |
| `MATDOC` | curated |
| `MATDOCOIL` | index |
| `PPH_DBVM` | index |
| `PRCD_ELEMENTS` | curated |
| `T130F_C` | index |

A caution that cost us a bug: **a successor is not necessarily new.** `KNA1`, `LFA1`, `MARA`, `MARC` and `RESB` are all named as successors in the Simplification List and all long predate S/4HANA. "Data now lives here" and "this is new" are different claims.

---

## Field-level changes that break code quietly

A table surviving tells you nothing about the shape of the fields inside it. These are systemic — they span whole domains rather than single tables.

| Change | From → To | SAP Note | Opt-in? |
|---|---|---|---|
| Material number extended to 40 characters | `CHAR 18` → `CHAR 40` | 2267140 | **yes** |
| Currency amount fields extended to 23 digits | `9–22 digits incl. 2 decimals` → `23 digits incl. 2 decimals` | 2628654 | **yes** |
| SD document category widened, status tables absorbed | `VBTYP — CHAR 1` → `VBTYPL — CHAR 4` | 2267306 | no |
| Object list number changed from INT4 to INT8 | `INT4` → `INT8` | 2580670 | no |
| Segment field extended to 40 characters | `16 characters` → `40 characters` | 2522971 | no |
| Season, Collection and Theme extended to 10 characters | → `10 characters` | 2624475 | **yes** |

**The opt-in ones deserve a decision, not a default.** The amount field length extension is off until someone switches it on in Customizing — and SAP states that once activated it cannot be reversed.

---

## The scenarios projects actually plan around

### 👥 Business Partner / CVI

In S/4HANA the Business Partner is the single master record. Customers and vendors are no longer maintained independently — every KNA1 and LFA1 record must have a matching BUT000 business partner, created through Customer/Vendor Integration (CVI).

**What to watch**

- Every customer and vendor needs a BP before conversion — CVI is a prerequisite, not a follow-up task.
- Address data moves with it: ADRC and BUTADRSEARCH are part of the same conversion.
- BUT000_TD holds time-dependent header data; check it if BP fields look like they changed over time.
- Country-specific master data (e.g. the India GST tables) has its own migration item.

*Tables involved: 8 · SAP Notes: 2576961, 2379157, 2409939, 2877717*

### 🔢 Material number field length

S/4HANA can extend the material number from 18 to 40 characters. The feature is optional and off by default, but turning it on ripples through every object that stores or compares a material number — including your own code.

**What to watch**

- Custom code that declares MATNR with a fixed length, or moves it into a shorter field, will truncate.
- Interfaces and file layouts with a fixed 18-character material field need widening on both sides.
- In a multi-system landscape the change has to be coordinated — a longer number cannot be sent to a system that has not been extended.
- Decide before conversion: switching later is far more disruptive.

*Tables involved: 60 · SAP Notes: 2267140, 2270396, 2471287*

### 📒 Universal Journal (ACDOCA)

S/4HANA merges Finance, Controlling, Asset Accounting, Material Ledger and profitability into one line-item table, ACDOCA. The classic totals and index tables are no longer the system of record; many survive only as compatibility views so existing reads keep working.

**What to watch**

- Always filter ACDOCA by ledger (RLDNR) unless you deliberately want every ledger.
- Reads against the old totals tables may still work through compatibility views — writes do not.
- Reporting built on the old tables should be re-pointed at ACDOCA to see the full picture.
- Currency configuration is part of this change; check the currency item before assuming parity.

*Tables involved: 13 · SAP Notes: 2344012, 2270449*

### 📦 Inventory documents (MATDOC)

Material document header and items (MKPF, MSEG) are consolidated into MATDOC, and the aggregate stock tables are calculated on the fly rather than stored. Reads are redirected, but anything that writes to or joins on the old tables needs attention.

**What to watch**

- Custom code updating MKPF or MSEG must be changed to MATDOC.
- Aggregated stock quantities are derived at runtime — do not assume a stored total.
- Joins written against MKPF/MSEG keys should be re-checked against the MATDOC key.
- Performance characteristics differ; re-test heavy inventory reports.

*Tables involved: 3 · SAP Notes: 2319579*

---

## Lessons

### From SAP's own required actions (16)

SAP repeats the same instruction across many tables. Where it repeats, it is worth reading once, properly.

**Read the Universal Journal, not the old FI tables**  
The classic FI index and totals tables are no longer the system of record. Custom programs that select from them need to read ACDOCA instead. This single instruction covers more tables than any other in the Simplification List.  
*Applies to 35 tables · SAP Note 2270333*

**Anything writing MKPF or MSEG must write MATDOC**  
Inventory management collapsed into one document table. Reads may survive through compatibility views, but updates do not — code that writes the old tables has to be changed.  
*Applies to 20 tables · SAP Note 2328419*

**Turn off the statistical moving average for throughput**  
Not mandatory, but SAP recommends it: leaving it active costs transactional throughput in Material Ledger processing.  
*Applies to 17 tables · SAP Note 2354768*

**Table pools and clusters are gone — including CDCLS**  
Removed as of 1809. Code referencing the container objects breaks; the logical tables survive as transparent tables. This is why change-document access needs checking.  
*Applies to 12 tables · SAP Note 2577406*

**Append structures on VBUK or VBUP need rework**  
The SD status tables were eliminated and their fields folded into the header and item tables. Any customer append on them has nowhere to go without adaptation.  
*Applies to 12 tables · SAP Note 2267306*

**LIS in PP is an interim solution — don't invest heavily**  
SAP is explicit that the Logistics Information System is a bridge in S/4HANA. Building new reporting on these structures is building on something with a stated end.  
*Applies to 9 tables · SAP Note 2268063*

**LIS in PM is an interim solution — don't invest heavily**  
Same position as PP: the information structures remain usable, but SAP frames them as an interim step rather than a destination.  
*Applies to 9 tables · SAP Note 2267463*

**KONV appends must move to PRCD_ELEMENTS**  
Pricing conditions changed their persistence table. KONV still exists, which is exactly why this one is missed — the appends do not come along automatically.  
*Applies to 8 tables · SAP Note 2267308*

**Foreign trade customizing tables retired in 1709**  
A small set of customizing tables became obsolete. Worth checking early because they are easy to overlook in a config comparison.  
*Applies to 5 tables · SAP Note 2468294*

**CO compatibility views are a stopgap, not a destination**  
Reading CO data through the compatibility views works, but SAP asks you to move to direct ACDOCA access for the affected value types.  
*Applies to 4 tables · SAP Note 2270404*

**Clean up total requirements before converting**  
A pre-conversion housekeeping step. Custom code reading the requirements tables needs checking at the same time.  
*Applies to 3 tables · SAP Note 2268089*

**Classic Profit Centre planning needs a new home**  
Planning in classic PCA is not carried forward as-is; SAP names the alternatives, and the choice between them is a design decision, not a technical one.  
*Applies to 2 tables · SAP Note 2993220*

**Substance volume tracking selection criteria change**  
An EHS consequence of the SD status tables disappearing — the selection criteria have to be adapted.  
*Applies to 2 tables · SAP Note 2267439*

**BUTADRSEARCH survives only for compatibility**  
Business partner address search data is retained for compatibility reasons, not because it is still the right thing to read.  
*Applies to 1 table · SAP Note 2576961*

**Migrate table-logging config before you convert**  
Run SAP's report in the source ERP system first. Doing it afterwards is not the documented path.  
*Applies to 1 table · SAP Note 2268131*

**Exchange-rate-difference customizing moved on**  
Custom code using the old exchange rate difference customizing has to be adapted; SAP names the affected fields.  
*Applies to 1 table · SAP Note 3053636*

### From building this thing (6)

Ours, not SAP's. Several were learned by getting it wrong here first.

**No simplification item is not a promise**  
1,803 of the tables in this app have no Simplification List entry at all. That means SAP has not published a change — not that the table is safe. The app files these under “No verdict” rather than “Carries over”, because collapsing the two turns “we don't know” into “it's fine”, and that is the error most likely to hurt you.

**A compatibility view is a read, not a reprieve**  
59 tables survive only as compatibility views. Reporting keeps working, which is exactly why they get missed — the failure surfaces later, on the first write. Treat “still readable” and “still there” as different findings.

**Some switches cannot be unflipped**  
The amount field length extension is off by default and, once activated in Customizing, SAP states it cannot be reversed. Decide switches like this before conversion planning hardens, not after.

**A successor table is not necessarily a new table**  
KNA1, LFA1, MARA, MARC and RESB are all named as successors in the Simplification List, and all long predate S/4HANA. “Data now lives here” and “this is new” are different claims, and conflating them invents history.

**“Still there” does not mean “still correct”**  
KONV still exists after pricing moved to PRCD_ELEMENTS. BSEG still exists after the Universal Journal. A table that survives can still be the wrong thing to read, and code that compiles will keep returning plausible answers from it.

**Prefer SAP's words to any summary of them**  
While building this app, curated one-line notes had drifted from SAP's published verdicts on 20 tables — VBUK and VBUP read “unchanged” where SAP had eliminated them. Wherever a summary and the Simplification List disagree, the list wins.

---

## What else is in the dataset

- **2,230 tables** with keys and declared foreign keys
- **91 movement types** and **10 document types**, decoded
- **3,622 BAPIs and RFC-enabled function modules**, with cloud release status; 47 carry a derivable link to a table

---

## Where this comes from, and where it stops

**Sources.** SAP's public Simplification List for S/4HANA 2025 FPS01, and SAP's Apache-2.0 licensed ABAP Cloudification Repository. Table names, field names and Note numbers are facts; the prose around them is ours.

**What we deliberately do not have:**

- **Full field lists.** We hold key fields and declared foreign keys, not every column. A table can carry a field without us knowing.
- **A per-table field diff.** The only public source pairing ECC and S/4 field lists disallows automated collection and sells that comparison as its own product.
- **BAPI parameter signatures.** SAP publishes none publicly.
- **Which tables a BAPI reads or writes.** Not published. Where the app links them, it is inferred from a shared successor view and labelled as such.
- **Anything about your system.** Every verdict here is about standard SAP. Your Z-tables, appends and modifications are yours to assess.

*Not affiliated with or endorsed by SAP SE. SAP and S/4HANA are trademarks of SAP SE.*
