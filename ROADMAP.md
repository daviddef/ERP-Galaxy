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
- ✅ `tools/parse_pdfs.py` committed, validated against EHS ground truth.
- Split Tier 1 / Tier 2; drop Structures and General View Structures from the graph.
- Assign modules; extend colour/emoji maps.
- Reconcile the 148 HTML-only tables (PDFs are **not** a superset — merge, never replace).
- **Pass 1: author `desc` for all 2,020** (factual, our words). Ship-critical. See [VOICE.md](VOICE.md).

**Exit:** one clean dataset, provenance tracked per table, Codex-ready.

### Phase 1b — `lore` pass (ongoing, never blocks a release)
The fun voice, written incrementally: Tier A (~150) first, Tier B over time, Tier C never (`lore: null` → UI falls back to `desc`). Decoupled from shipping by design.

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

---

## 7. Getting to TestFlight (decided 2026-07-16)

### Device strategy: iPad/Mac first, iPhone via the Codex

David's read is correct — the galaxy is a big-screen experience and the iPhone is tight. But **the answer isn't cutting iPhone, it's giving it a different front door.**

| Device | Primary UI | Why |
|---|---|---|
| **iPad** | Galaxy graph | 217 nodes at 1024pt+ is genuinely comfortable. The hero experience. |
| **Mac** | Galaxy graph | Free via "Designed for iPad" — see below. Biggest canvas of all. |
| **iPhone** | **Codex (search/list)** | A 390pt force graph is a hairball. But a *searchable list* is perfect on a phone — that's what phones are for. Graph stays reachable, secondary. |

This is what the Tier 1 / Tier 2 split was already for. The Codex isn't a post-launch nice-to-have — **it is the iPhone's reason to exist**, and its `desc` data is being authored now. Phone users mostly want "what is LFA1" answered in 3 seconds, not an exploration canvas.

**Consequence: the Codex (was Phase 4) moves ahead of native-feel polish (Phase 3) if iPhone parity matters at v1.** If it doesn't, ship iPad/Mac-first and let iPhone be tight for one build.

### Mac is nearly free
"Designed for iPad" runs the iPad build on Apple Silicon Macs — **no Mac Catalyst work**. TestFlight supports it, toggleable per tester group in App Store Connect. Caveats: no menu bar, limited window chrome. Fine for v1; a real Catalyst app is a later call. (Known Apple issue: some "Designed for iPad" builds appear in TestFlight on macOS but fail to install with *"This app can only be tested on an iOS device."* Budget an hour for this to misbehave.)

### ⚠️ The real risk: App Store Guideline 4.2 (Minimum Functionality)

**A WKWebView wrapper around a website is the textbook 4.2 rejection.** This is the single biggest threat to shipping, and it is architectural — not something to discover at submission.

Mitigations, roughly in order of weight:
1. **Fully offline** — no network at all. Already true as of Phase 0. This is the strongest argument: it is demonstrably not a web page.
2. **Native Codex** — a real SwiftUI/SwiftData screen, not web content. Doubles as the iPhone answer.
3. **Spotlight indexing, widget, Siri Shortcuts** — system integration a website cannot do.
4. Haptics + share sheet — necessary, not sufficient on their own.

The app is also **not** a repackaged public website: the data is curated and the HTML is a bundled asset, not a hosted URL. That helps, but the reviewer sees a web view first.

### Fastest honest path to a build on your device

**Internal TestFlight skips Beta App Review.** Up to 100 App Store Connect users, no review, minutes not days. External testers *do* require Beta App Review — which applies the same 4.2 guideline.

So:
1. **Internal TestFlight ASAP** — Phase 2 shell (~1 day). Universal. iPhone tight, and that's fine: you learn *how* tight from the real device.
2. **De-risk 4.2 before external/public** — land the native Codex first (it's also the iPhone fix). One change, two problems.

### 🔴 Blocker — yours, not mine
**Apple Developer Program membership ($99/yr)** is required for any TestFlight build. It needs payment details and Apple ID authentication, so **you must set it up** — I can't enter credentials or complete the purchase. Everything else (project, signing config, icon, build) I can do.

Once you have the Team ID, I can scaffold the Xcode project and configure signing.

### Phase 6+ — Post-launch
Spotlight indexing (Codex makes this near-free) → "Table of the Day" widget → Siri Shortcuts → extract detail sheet & search to native → curate Tier 2 → Tier 1 over time.

**~6–10 days to TestFlight.** The handover's "days not weeks" holds — the data work adds ~2 days it didn't account for.

---

## 4. Open Decisions

1. ~~**Licensing**~~ **Resolved:** rewrite all upfront in our own words. Raw scraped text stays gitignored. *Residual:* Tier C `desc` sits close to source by necessity — see the caveat in [VOICE.md](VOICE.md).
2. ~~**Scope of "fun and savvy"**~~ **Resolved (2026-07-16):** fun tone in the copy, stored as a separate `lore` field with a UI toggle. Adds a small Phase 3 item (the toggle control + fallback).
3. **Tier 1 promotion criteria** — which of the 1,951 deserve curated relationships first? Suggest: by module coverage gaps + practitioner frequency (LFA1, EKKO, MKPF etc. are obvious candidates).
4. ~~**`/TDAG/*` (278 tables)**~~ **Resolved:** keep, tagged as an add-on so they can be filtered. Search-gated, so they cost nothing until someone looks for them.
5. ~~**`d3.min.js` vendoring**~~ ✅ **Done** — vendored to `vendor/d3.min.js`, verified rendering 217 nodes / 467 links from `file://` with no network.

---

## 6. What `/TDAG/` Actually Is

Worth recording, because my first characterisation ("third-party, not core SAP") was **wrong** and would have shipped as a wrong description.

- `/XXX/` is an **SAP-reserved namespace** allocated to a partner. Objects inside it are add-on deliverables, not part of the ECC/S4 core.
- **TDAG = TechniData AG**, the German partner that originally *built* SAP's EH&S module under contract.
- **SAP acquired TechniData in 2010.** So `/TDAG/` is now **SAP's own software** — it just kept the legacy namespace. Calling it "third-party" is out of date by 16 years.
- `/TDAG/CP` = **Compliance for Products**, now part of SAP EHS Management (Product Compliance); covers EU RoHS, REACH and customer declarations. Entry point is the Compliance Workbench (`/TDAG/CPM00`).
- **Who cares:** chemical, pharma, and discrete manufacturing clients running Product/REACH Compliance. Niche, but real — and an EHS consultant would be pleased to find these.

**Namespace breakdown of the 1,285 `/TDAG/` entries** (only 278 are real tables; the rest are structures/views):

| Prefix | Entries | Meaning |
|---|---|---|
| `CPS` / `CPC` / `CPV` / `CPT` | 819 | Compliance for Products — **confirmed** |
| `RCSS` / `RCSC` / `RCSV` / `RCSA` | 427 | Regulatory content (`RCSC_LEGSL` = "Legislation"). Likely tied to SAP Product and REACH Compliance — **not confirmed; do not assert in a description until verified.** |

Sources: [SAP to Acquire TechniData AG](https://www.prnewswire.com/news-releases/sap-to-acquire-technidata-ag-91681344.html) · [SAP ABAP Package /TDAG/CP](https://www.sapdatasheet.org/abap/devc//tdag/cp.html) · [History of SAP Product Compliance Solutions](https://www.opesus.com/en/history-sap-product-compliance-solutions)
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

3. **EHS descriptions truncated (~1,660 affected) — found *after* the row-count check passed.** The fix for bug 2 keyed continuation lines off a fixed `' '*40` indent. But the description column *shifts across pages*, so that rule captured **67 of 2,682** continuation lines. `/TDAG/CPC_DECL` read *"CP: Definition of"* instead of *"CP: Definition of declaration types"*. Fixed by anchoring continuations to each row's own description column, taken from the head match's start offset — which also rejects page artifacts (a stray `RUCT` fragment) and the document's trailing table-of-contents (which the last row had absorbed wholesale).

**Lessons:**
- **Validate extraction against ground truth before scaling authoring on top of it.** The EHS rank column made row *count* checkable.
- **A row-count check does not prove content integrity.** Bug 3 passed the 2,362-row check while silently amputating ~1,660 descriptions. Count and completeness are different assertions — test both.
- **The authoring pass found bug 3, not the parser tests.** A pilot batch returned 14% `null` ("cannot describe this"), far above the predicted 1–3%. The agent was correctly refusing to describe truncated text. **Treat a downstream quality anomaly as an upstream data signal.**

### Data hygiene flags
- **23 new tables have source descriptions too thin to paraphrase** (`"obsolete"`, `"Language dependent"`). Rewriting these means inventing. Ship names-only.
- **278 new tables are `/TDAG/*`** — SAP EHS Management Product Compliance, in a legacy partner namespace. **Keep, but tag `addon:"EHS-CP"`.** See "What `/TDAG/` actually is" below.
- **The EHS source contains untranslated German** (`"Generierte Tabelle zu"`). The rewrite must handle or flag these.
- **Raw scraped descriptions are gitignored** (`data/raw_*.json`, `txt/`) and must never be committed — see decision 1. Only rewritten prose enters the public repo.
