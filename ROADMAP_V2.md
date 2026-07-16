# ERP Galaxy — Roadmap v2

**Status (2026-07-16):** Build 1 **live on TestFlight**, VALID. 217-table curated galaxy + 1,816-table Codex, 98.7% with primary keys, 3,220 foreign-key edges, 43 evidence-backed S/4 migration verdicts. Fully offline. ~30 commits, public repo.

---

## 1. The breakthrough we just had

**SAP's public reference pages carry declared foreign keys** — the "Check table" column. I had told David these sources gave us *no* relationships and that every edge had to be hand-curated. That was wrong: the data sat in 2,033 pages already on disk, in a column I never parsed.

| | |
|---|---|
| Raw FK links extracted | 12,594 |
| Edges after dropping noise (`T000`/`T002`/`T006`) | **3,220** |
| Tables that gained relationships | **1,588** |
| Previously "unmapped" Codex tables now mapped | **1,601** |

**The subtle part — FKs are not a substitute for curation.** Only **39%** of the 411 hand-curated edges are declared FKs. The two capture different things:

- **Curated edges** = *business flow*. `BKPF → BSEG` (header→items) is not a foreign key. It's meaning.
- **FK edges** = *config/lookup*. `BKPF.BUKRS → T001`, `CCIHT_WAH → T001W`.

Dump FKs into the galaxy and `PA0003` (456 edges) drowns it. So FKs surface **on Codex detail sheets**, not in the curated graph. **This is the moat**: anyone can scrape names; the 411 hand-authored business edges are the thing that can't be harvested.

---

## 2. Extending beyond SAP — research verdicts

### SAP SuccessFactors — **PARTIAL / VIABLE**
- **Model:** OData entities (Employee Central, MDF Generic Objects, per-module services).
- **Source:** no free tenant, and `$metadata` needs paid-tenant auth — **but SAP publishes static OData reference PDFs openly on help.sap.com** (`SF_EC_OData_API_REF.pdf` et al, 800+ pages).
- **Relationships:** ✅ Navigation Properties are documented, plus a dedicated EC entity-relationships page.
- **Licensing:** identical posture to what we already navigated — SAP doc copyright; take **facts**, author our own prose.
- **Verdict:** *the same playbook we already ran.* Parse public PDFs → own descriptions. Wrinkle: MDF objects are tenant-configurable, so a chunk of the model is un-documentable by nature (SAP's version of Z-tables).

### ServiceNow — **PARTIAL, leaning BLOCKED** ⚠️
- **Model:** literal Glide tables; `sys_db_object` + `sys_dictionary` are self-describing. Reference fields are clean FKs. ~4,000–6,000 OOB tables, ~150K fields.
- **The trap:** a **free Personal Developer Instance** gives full admin access to all of it. Technically the best schema source of any platform researched — better than SAP's.
- **Why we won't:** the Website ToU and PDI Agreement contain **explicit anti-scraping clauses** — *"use any robot, spider... to scrape, mine, retrieve, cache, analyze, or index"* — and PDIs are licensed *"solely for your own internal use to evaluate the ServiceNow Products."* That is far more specific than SAP's generic doc copyright, and it names exactly the mechanism we'd use.
- **Legitimate slice:** the public **CMDB CI class reference** on docs.servicenow.com is fair game to parse.
- **Verdict:** take the CMDB-only path or none. **Do not harvest a PDI.** The easiest data here is the most explicitly forbidden — and the reason to decline is that the prohibition is real, not that it's risky to get caught.

### Microsoft Dynamics 365 — **VIABLE. The standout finding.** ⭐
The hunch paid off, and I verified the two load-bearing claims by hand rather than trusting the research:

```
microsoft/CDM            LICENSE → "Attribution 4.0 International"   ✅ CC-BY-4.0
MicrosoftDocs/powerapps-docs  LICENSE → "Attribution 4.0 International"   ✅ CC-BY-4.0

CustTable Main.manifest.cdm.json → relationships: 473 explicit edges
   CustTable -> CustBankAccount         via Relationship_BankAccountsRelationshipId
   CustTable -> BankCentralBankPurpose  via Relationship_BankCentralBankPurposeRelationshipId
   CustTable -> CashDisc                via Relationship_CashDiscRelationshipId
```

| | SAP (what we did) | Dynamics 365 (what we'd do) |
|---|---|---|
| Format | 30 PDFs, 3 layouts, 4 parser bugs | **structured JSON** |
| Relationships | **none** — 411 hand-curated | **included**: `fromEntity`/`toEntity`/`attribute` |
| Licence | SAP copyright — facts only, rewrite all prose | **CC-BY-4.0 — redistributable with attribution** |
| Scale | 1,816 | ~1,684 (F&O/CDM) + 593 (Dataverse) |

**Every constraint that made SAP hard is absent here.** No PDF archaeology, no truncated columns, no form-feed page breaks, no licensing tightrope, no hand-curated edges. The graph builds itself. Dynamics is a **better second platform than SAP was a first**, and it's the clear next move.

### Oracle Fusion Cloud — **PARTIAL / VIABLE**
- **Publishes foreign keys per table, in both directions** — `AP_INVOICES_ALL` lists ~40 FK rows. Structurally better than SAP.
- Clean static HTML on docs.oracle.com, no login. Likely several thousand tables across seven guides.
- **Catch:** standard Oracle all-rights-reserved notice, no redistribution grant. Same posture as SAP — structural facts are fine, Oracle's prose is not. Workable, just not free of the rewrite tax.

### Ranked
| Platform | Verdict | Licence | Relationships | Move |
|---|---|---|---|---|
| **Dynamics 365** | ⭐ **VIABLE** | **CC-BY-4.0** | **included** | **do this next** |
| Oracle Fusion | VIABLE | proprietary | published FKs | strong third |
| SuccessFactors | PARTIAL | SAP copyright | nav properties | same playbook as SAP |
| ServiceNow | **leaning BLOCKED** | ToU forbids scraping | clean FKs | CMDB docs only |

### The strategic read
Every platform has the same shape: **names and fields are gettable; relationships are sometimes gettable; meaning never is.** Our differentiator was never the table list — it's the curated business edges, the plain-English voice, and the migration verdicts.

Note the irony worth sitting with: **SAP was the hardest possible starting point** — PDFs, no relationships, hostile licensing. We did the difficult one first. Everything after this is easier, and the pipeline in `tools/` already generalises.

But note the flip side too. If Microsoft hands you 1,684 tables *with* edges under CC-BY, then **so can any competitor, in a weekend.** The SAP corpus is defensible *because* it was miserable to build. Dynamics is cheap to add and cheap to copy — so the moat there has to be the curation and the migration story, not the data.

**Scaling model:** one schema (`id, module, desc, keys, fks, lifecycle, tier`) with a `platform` discriminator. The pipeline (parse → author → gate → merge) is already platform-agnostic — it's in `tools/`. What doesn't scale is curation, and that's the point.

---

## 3. AdMob — how and where

**Verified requirements** (full detail in research notes):

| Required | Detail |
|---|---|
| SPM package | `github.com/googleads/swift-package-manager-google-mobile-ads` (SDK 13.6, iOS 13+) |
| `GADApplicationIdentifier` | Info.plist — SDK crashes without it |
| `SKAdNetworkItems` | Google's boilerplate list |
| **Privacy label change** | **Device ID, Advertising Data, IP Address, Crash/Performance, Product Interaction** |
| UMP/CMP | Mandatory for personalised ads in EEA/UK/CH |
| `NSUserTrackingUsageDescription` | Only if we call ATT |

### 🔴 Confirmed: no AdSense inside the WebView
Injecting `<ins class="adsbygoogle">` into our bundled HTML is a **policy violation risking account suspension** — not a grey area. AdSense-in-app is only sanctioned via "WebView API for Ads", which is for wrapping a **live website**; our HTML is local and offline, so it doesn't apply. **Native `BannerView` only.**

### Placement
Anchored **adaptive banner at the bottom**, as a native SwiftUI view **outside** the WebView, with the WebView's bottom anchor constrained to the banner's top. Do *not* z-order it under the WebView (invisible and untappable). Reserve layout space instead.

**Not interstitials.** Apple **2.5.18** requires clear labelling and an easy close control, and **3.2.2(iii)** rejects apps "designed predominantly for the display of ads." A graph you pan continuously has no natural break point — an interstitial mid-exploration is exactly the "interferes with usability" pattern.

### ⚠️ The strategic cost — read before deciding
The app today collects **nothing**. That is:
1. A genuine selling point for consultants on **corporate devices** — and the audience most likely to notice.
2. **My strongest argument against a Guideline 4.2 rejection.** "It's fully offline with a 1,816-table index" is what makes it not-a-repackaged-website.

AdMob trades both away for what is likely **very low revenue** — a niche B2B audience, on managed devices, many with ad blocking, during working hours.

**Recommendation: don't ship ads in v1.** Get external TestFlight through Beta App Review with the offline story intact. If you want monetisation, the honest options are:
- **One-off "Pro" IAP** — no data collection, no ATT, no CMP, no privacy-label change, and consultants *do* expense tools.
- **Free with a paid tier** for the curated galaxy + migration verdicts (the expensive, defensible part), Codex free forever.

If you still want ads: test ad unit IDs work in TestFlight today (`ca-app-pub-3940256099942544/2435281174`), so we can prototype the layout without an AdMob account and decide with it in front of us.

---

## 4. Making it fun, not consulting

Shipped already: the galaxy metaphor, module colours, migration fill (red = dying, green = new), haptics, plain-English voice.

Ideas that fit the tone without becoming gimmicks:

1. **Table of the Day** widget — one table, one plain-English explainer. Home-screen presence, near-zero cost, and it's the single best 4.2 defence (a widget is not a website).
2. **"Explain like I'm new"** toggle — the `lore` field we designed and never filled. `desc` for the client meeting, `lore` for learning. **This is the "fun mode" already in the schema.**
3. **Migration Impact score** — for a locked board, "3 of your 5 tables die in S/4." Turns a reference tool into an *assessment* tool. Genuinely novel; nobody's doing it.
4. **Share a board as an image** — a consultant screenshotting *your* graph into a client deck is free distribution with your name on it.
5. **Spotlight indexing** — type "BSEG" in iOS search, get the answer. This is the "offline mobile" advantage made real.
6. ~~Achievements/streaks~~ — **no.** Wrong audience. A data architect does not want a badge.

**The unifying idea:** the websites answer *"what is this table?"* We should answer *"what happens to my tables?"* That's the question with a deadline attached.

---

## 5. Scalability

**Data:** 576 KB HTML with everything embedded. Fine today; at ~4 platforms it's ~2 MB of JS parsed at launch. **Trigger point:** move the Codex to **SwiftData** when we add platform #2 — which also unlocks Spotlight, widgets, and Siri.

**Graph:** 217 nodes is near the mobile ceiling. **Never** put 1,816 in the force sim. The lockable board is the answer — and it's built.

**Pipeline:** already platform-agnostic (`tools/`: parse → build → author → gate → merge). Adding a platform is a parser + a module map.

**The real bottleneck is curation.** 411 edges are hand-made. That doesn't parallelise — but it's also the moat, so the constraint and the differentiator are the same thing.

---

## 6. Market test — the honest version

### The App Store is empty. That cuts both ways.
Querying the iTunes Search API directly (not web search): **there is no credible SAP table/tcode reference app on iOS.** The nearest hit is "ABAP" by Pavel Lezama — **3.0 stars from 2 ratings**. On Android, the closest analog ("SAP TCODE Buddy") has **500+ installs total**.

The optimistic read: a vacant category. **The pessimistic read is stronger and you should hear it.**

### 🔴 The strongest argument against this product
**The market has already spoken, twice.**

1. Five mature, free websites (tcodesearch, sapdatasheet, leanx, se80, erpexplorer) have served the "look up a table" job for **over a decade**. They have the data, the audience, and years of runway. **None of them built a serious native app.** That's not an oversight — it's revealed preference.
2. The handful who *did* try mobile got **hundreds of installs, not thousands.**

The likely reason: **the job is desk-bound by nature.** A consultant in a migration workshop has two monitors and SAP GUI open. They will type into Google or a bookmarked tab. That is *faster* than picking up a phone. Our "offline mobile" advantage is real only in narrow cases — locked-down client sites, plant/warehouse floors, flights, or as the only SAP-adjacent thing a security-conscious employer will allow on a phone.

**Ad-supported is the weakest part of the plan.** This independently confirms §3: small install base, corporate-managed devices, task-focused sessions. A consultant checking one table mid-call is a bad ad impression at any volume.

### The wedge — stop competing on lookup
Lookup is desk-bound and the websites win it. **They cannot answer "what happens to my tables?"**

That's a different job with a **hard external deadline**: ECC 6.0 mainstream maintenance ends **31 Dec 2027**, extended to 2030 at a 9–12% premium, and SAP confirmed in Jan 2025 there's no further extension. One estimate puts **17,000 companies** still un-migrated. That is a real, dated, funded wave running straight through this product's window.

**Reposition from reference tool to migration-assessment tool.** Lock your 5 tables → *"3 of these die in S/4, 1 becomes a compatibility view, here's the successor and SAP's own words for it."* Nobody — web or mobile — does this. It's the one thing that:
- requires **judgment against the Simplification List**, not a schema dump;
- **can't be scraped**, so a competitor can't bolt it on next quarter;
- has someone's **deadline and budget** attached.

The lockable board shipped today is the skeleton of exactly this.

### Trademark: clear
SAP's own guidance permits descriptive use ("for SAP", "built for SAP data") and forbids "SAP" *in* a product name. **"ERP Galaxy" is correctly positioned** — which retroactively justifies the rename. Every surviving competitor uses the same register.

### Who actually buys
Not "SAP practitioners" — too broad. It's **consultants and migration staff scoping ECC→S/4 in 2026–27**. Narrow, real, dated, and *funded* — their employers already pay ~$1,488/yr for SAP Learning Hub. Which is the argument for **IAP over ads**: this audience doesn't click ads, but their employer expenses tools.

---

## 7. Next

Ordered by the market read, not by what's fun to build:

1. **Lean into migration assessment.** The board exists; add the **Migration Impact score** ("3 of your 5 tables die in S/4"). This is the only defensible differentiator and the only one with a deadline attached. *Highest value, days of work.*
2. **Widen S/4 verdict coverage** — 43 tables is thin for the thing the product now hangs on. Parse more Simplification List releases (1909→2023) and lift coverage across the curated 217 first.
3. **Beta App Review** for external TestFlight — the real Guideline 4.2 test. *Before ads.*
4. **Fill `lore`** for the ~150 famous tables — fun mode is designed, specced, and empty.
5. **Widget + Spotlight** — cheap, strong 4.2 defence, and makes "offline mobile" concrete rather than theoretical.
6. **Monetisation: IAP, not ads.** The audience doesn't click ads; their employers expense tools.
7. **Platform #2: Dynamics 365** — CC-BY, relationships included. But only *after* the migration wedge is proven on SAP; adding cheap-to-copy data doesn't deepen the moat.

*Open: 12 tables where the two key sources disagree (left curated, not guessed). 68 Codex tables without keys. `lore` at 0. No Fiori data — no source exists in what we have.*
