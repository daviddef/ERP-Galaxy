# SAP Galaxy 🌌 — Roadmap

**Status:** Pre-Xcode. HTML prototype complete, data expansion pending.
**Repo:** https://github.com/daviddef/ERP-Galaxy (public)
**Target:** Native iOS app, WKWebView shell → progressive SwiftUI extraction.

---

## 1. Where We Actually Are

| Asset | State |
|---|---|
| `sap-table-explorer.html` | 184 KB, self-contained except D3 (CDN) |
| Curated tables | 217 |
| Curated relationships | 467 (**not** 567 as the handover claims) |
| Modules | 11 (FI, CO, MM, SD, PP, HR, WM, PM, QM, PS, BASIS) |
| PDF source corpus | 30 docs → 3,596 table names, 945 T-codes |
| Xcode project | Does not exist yet |
| Local git | Not initialised (remote exists, public) |

### Corrections to `CLAUDE_CODE_HANDOVER.md`

The handover is directionally right but factually wrong in ways that matter:

1. **"Self-contained: YES / Offline support ✅" is false.** D3 v7 loads from `cdnjs.cloudflare.com` (line 7). Bundled as-is, the app is a blank screen offline. **Ship-blocker.**
2. **567 relationships → actually 467.**
3. **§5c "verify viewport exists"** — it exists but lacks `maximum-scale`/`user-scalable=no`.
4. **§5d safe-area insets** — not present; must be written.
5. **JS→Swift bridge** — does not exist. (`webkit` greps are CSS vendor prefixes.)
6. **`config.preferences.javaScriptEnabled`** (§4) deprecated since iOS 14 → use `defaultWebpagePreferences.allowsContentJavaScript`.
7. **Share sheet's `scene.windows.first?.rootViewController`** is fragile on iPad/multi-scene.
8. **Swift 5.9 / iOS 15** — toolchain is Xcode 26.5 / Swift 6.3. Recommend **iOS 17** target.

---

## 2. The Data Expansion — Read This Before Merging Anything

The 30 PDFs were parsed (`pdftotext -layout` + per-format parsers). Results:

| Metric | Count |
|---|---|
| Total entries extracted | 3,879 |
| — **Structures** (no data, not real tables) | 1,574 |
| — **General View Structures** (views, not tables) | 285 |
| — **real tables** (Transparent/Pooled/Cluster/Append) | **2,020** |
| Already in our dataset | 69 |
| **Genuinely new real tables** | **1,951** |
| In our dataset but **absent from all PDFs** | 148 |

*Parser validated against ground truth:* the EHS doc's own rank column runs to 2,362, and the parser now accounts for all 2,362 rows. Two extraction bugs were found and fixed during a pilot — see §5.

**This is a ~10x expansion, and it cannot be done as a straight merge.** Four reasons:

### 2a. The PDFs carry almost none of our schema
A curated node looks like this:
```js
{id:"BKPF", module:"FI", ecc:true, s4:true, s4status:"modified",
 shortDesc:"Accounting Document Header",
 plainEnglish:"The cover sheet for every financial posting...",
 keyFields:["MANDT","BUKRS","BELNR","GJAHR"], relations:[...]}
```
The PDFs give us **`id` + one short description.** No module, no ECC/S4 lifecycle, no key fields, no plain-English explainer, no relations. Merging naively yields 1,951 nodes with 8 of 9 fields empty.

### 2b. There is zero relationship data in the PDFs
Our 467 edges are hand-curated. The PDFs contain no foreign-key or join information whatsoever. 1,951 new nodes would be **orphans** — grey dots floating in the void with no edges. In a force-directed graph whose entire premise is *relationships*, that is not a feature, it's noise.

### 2c. 1,576 entries are Structures, not tables
`RDGPRINT`, `EHSBT_APPL_SCOPE` etc. are ABAP structures/DDIC definitions — no persisted data. An SAP practitioner looking up "what table holds X" is actively misled by these. **Exclude from the graph**; at most, tag them in the index.

### 2d. 2,000 nodes will kill the graph on a phone
217 nodes already sits near the practical limit for a D3 force simulation rendering SVG in mobile Safari. 2,000+ nodes means unusable frame rates and a hairball nobody can read. This isn't tunable — it's architectural.

### The resolution: a two-tier data model

Don't fight it. Split the product into the two things it's actually trying to be:

**Tier 1 — The Galaxy (exploration).** The curated ~217, plus selectively promoted tables that earn their place by having real relationships mapped. Stays a force-directed graph. Quality over quantity. This is the *fun* part.

**Tier 2 — The Codex (lookup).** All ~2,020 real tables. No graph — a fast searchable/filterable index: name, description, module, source. This is where SwiftData earns its keep, and it unlocks Spotlight, the widget, and Siri Shortcuts.

A table graduates Tier 2 → Tier 1 when someone curates its relationships. The Codex becomes the backlog for growing the Galaxy — and the app ships with "2,000+ tables" as a real claim without a wrecked graph.

### New modules to add
The PDFs extend beyond our 11 modules: **EHS**, **FI-TV** (Travel), **FM** (Funds Mgmt), **FI-CS** (Consolidation), **FI-BL** (Bank), **FI-CR** (Credit/Risk). `MODULE_COLORS` and `MODULE_EMOJIS` need extending.

### ⚠️ Licensing — resolve before shipping
The PDFs are scraped from **tcodesearch.com**, and the descriptions are largely **SAP's own DDIC short texts**. Redistributing ~2,000 of them verbatim in (a) a **public** GitHub repo and (b) a paid/public App Store binary is a real IP exposure — SAP is litigious about its data dictionary. Options: rewrite descriptions in our own "idiot's guide" voice (on-brand anyway), ship names-only with original prose, or seek clearance. **Decide before Phase 2.** Table *names* are facts and are far safer than *descriptions*.

---

## 3. Roadmap

### Phase 0 — Foundation & de-risk (½ day)
- `git init`, wire to the existing public remote, commit the HTML as baseline.
- **Vendor `d3.min.js` locally** — kills the offline blocker and the ATS workaround.
- Harden viewport tag; add `env(safe-area-inset-*)` CSS.
- Verify: open in Safari with network **offline**. Graph must render.

**Exit:** a genuinely self-contained artifact under version control.

### Phase 1 — Data pipeline (1–2 days)
- Commit `tools/parse_pdfs.py` + `data/tables.json` (reproducible, reviewable).
- Split Tier 1 / Tier 2; drop Structures from the graph.
- Assign modules; extend colour/emoji maps.
- Reconcile the 148 HTML-only tables (PDFs are **not** a superset — merge, never replace).
- Resolve the licensing decision above.

**Exit:** one clean dataset, provenance tracked per table.

### Phase 2 — Xcode shell (1 day)
Project scaffold, four Swift files per handover §4 (with the deprecation fixes), HTML + `d3.min.js` in Resources, dark-only Info.plist, iOS 17 target.

**Exit:** graph renders in the simulator.

### Phase 3 — Native feel (1–2 days)
Haptics + share bridge; disable WebView zoom (it fights `d3.zoom()`); splash to cover the ~300 ms simulation settle; landscape + iPad.

**Exit:** feels like an app, not a website in a box.

### Phase 4 — The Codex (2–3 days)
Tier 2 into **SwiftData** as a native SwiftUI list — `searchable()`, module filter, table detail. First genuinely native screen. Deep-links into the Galaxy when a table is Tier 1.

**Exit:** "2,000+ SAP tables, offline, in your pocket."

### Phase 5 — Ship (1–2 days)
Icon, screenshots, bundle ID, signing, TestFlight.
*Requires your Apple Developer account — credential/submission steps are yours, not mine.*

### Phase 6+ — Post-launch
Spotlight indexing (Codex makes this near-free) → "Table of the Day" widget → Siri Shortcuts → extract detail sheet & search to native → curate Tier 2 → Tier 1 over time.

**~6–10 days to TestFlight.** The handover's "days not weeks" holds — the data work adds ~2 days it didn't account for.

---

## 4. Open Decisions

1. **Licensing** — rewrite descriptions, names-only, or clearance? *Blocks Phase 1 data commit.*
2. **Scope of "fun and savvy"** — the brief says "idiot's guide accessible, not enterprise-dry," but the HTML is a fairly straight reference tool. Does this mean personality in the copy, or achievements/table-of-the-day? *Changes Phase 3 scope; cheaper to decide before the bridge is built.*
3. **Tier 1 promotion criteria** — which of the 1,951 deserve curated relationships first? Suggest: by module coverage gaps + practitioner frequency (LFA1, EKKO, MKPF etc. are obvious candidates).
4. ~~**Public repo** — intentional?~~ **Confirmed OK (2026-07-16).** Note this raises the stakes on decision 1: a public repo is the more exposed venue for the scraped descriptions, and git history is permanent — a later `git rm` does not remove them from earlier commits.

---

## 5. Reproducing the Data Extraction

```bash
# 30 PDFs → text (three distinct layouts: bullet, EHS ranked-table, HR flat)
for f in *.pdf; do pdftotext -layout "$f" "${f%.pdf}.txt"; done
python3 tools/parse_pdfs.py   # → data/tables.json, data/tcodes.json
```
Parser notes: EHS is a ranked 4-column layout with wrapped descriptions; HR Infotypes is flat `NAME description`; the other 28 are `• NAME : description` bullets, some with a `( Category : X )` prefix to strip. T-code docs are routed by filename (case-insensitive match on `transaction`/`tcode`).

**Two bugs found during the rewrite pilot — both would have silently poisoned the dataset:**

1. **Truncated descriptions (465 affected).** Bullet descriptions wrap across blank-line-separated continuation lines; the first parser captured only the first line. `ACCTCR` read *"Compressed data from"* instead of *"Compressed data from FI/CO document - currencies"*. Fixed by block-joining on bullet boundaries. The `( Category : X )` strip also failed where the source omits the closing paren (`T049B`).
2. **EHS rows dropped (285 affected).** EHS puts the *type* on the first line while the description wraps *below* it, so block-joining corrupted it (`"Structure for Printing DG Structure Data"`). Needs line-wise parsing with continuation. A further 285 rows used an undeclared type, `General View Structure`.

**Lesson: validate extraction against a ground-truth count before scaling any authoring on top of it.** The EHS rank column made this checkable; docs without one are validated by spot-check.

### Data hygiene flags
- **23 new tables have source descriptions too thin to paraphrase** (`"obsolete"`, `"Language dependent"`). Rewriting these means inventing. Ship names-only.
- **278 new tables are `/TDAG/*`** — TechniData third-party EHS add-on, not core SAP. Most consultants will never see them. Candidate for exclusion or a separate flag.
- **The EHS source contains untranslated German** (`"Generierte Tabelle zu"`). The rewrite must handle or flag these.
- **Raw scraped descriptions are gitignored** (`data/raw_*.json`, `txt/`) and must never be committed — see decision 1. Only rewritten prose enters the public repo.
