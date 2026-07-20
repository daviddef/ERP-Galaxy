# App Store submission — metadata

**App:** `6791550922` · `com.daviddef.erpgalaxy` · v1.0 · primary locale **en-AU**

---

## Name & subtitle

| Field | Value | Limit |
|---|---|---|
| Name | `ERP Galaxy` | 30 |
| Subtitle | `Offline SAP table reference` | 30 (27 used) |

**⚠️ Trademark judgement call.** SAP's guidance forbids "SAP" *in a product name* but permits
descriptive use ("for SAP", "SAP-compatible"). The **name is clean**. The **subtitle uses SAP
descriptively** — which is the standard nominative-fair-use register every competing site uses,
but it sits directly under the app name where Apple's metadata review sometimes asks for proof
of trademark rights.

If Apple pushes back, the fix is one field: drop the subtitle to `ECC to S/4HANA table atlas`
or `Offline table reference` and keep SAP in the description and keywords only, where it is
plainly descriptive. Not worth pre-emptively crippling discovery — but worth knowing which
field to change.

---

## Keywords (100 char limit)

```
SAP,ABAP,table,tcode,S4HANA,ECC,BSEG,ACDOCA,migration,consultant,dictionary,SE16,ERP,fields
```
90 characters. Notes:
- Do **not** repeat words already in the name/subtitle — Apple indexes those anyway, so
  repeating them wastes the budget.
- Real table names (`BSEG`, `ACDOCA`) are in because that is literally what people search.
- Comma-separated, no spaces — spaces waste characters.

---

## Promotional text (170, editable without a new build)

```
The ECC deadline is 2027. Lock your tables to a board and see which ones survive S/4HANA —
which disappear, which become compatibility views, and where the data moved.
```

---

## Description

See `metadata/description.txt` (applied via API). Structure:
1. One-line what-it-is
2. The migration hook (the differentiator the market test identified)
3. Feature list
4. The offline/privacy promise
5. Honest limits
6. Trademark disclaimer

---

## URLs

| Field | Value |
|---|---|
| Privacy Policy | `https://daviddef.github.io/ERP-Galaxy/privacy.html` ✅ live |
| Support | `https://github.com/daviddef/ERP-Galaxy/issues` |
| Marketing | `https://github.com/daviddef/ERP-Galaxy` |

Privacy policy is served by GitHub Pages from `/docs` on the public repo. **Apple checks this
URL** — if the repo ever goes private, the link dies and the next review fails.

---

## Categories

| | | Why |
|---|---|---|
| Primary | `DEVELOPER_TOOLS` | The audience is ABAP devs, data architects, consultants. Small category — easier to be visible. |
| Secondary | `REFERENCE` | Literally what it is. |

Alternative: `BUSINESS` primary. It's a bigger, more crowded category, so I chose the
narrower one. Easy to change.

---

## Age rating

All questions answered **NONE** — no violence, no profanity, no gambling, no user content,
no unrestricted web access. The app is an offline reference tool. Expected rating: **4+**.

Note `unrestrictedWebAccess: false` is honest here precisely *because* the WKWebView loads
bundled local HTML and the app makes no network requests. If ads were added this would need
revisiting.

---

## App Privacy (nutrition label)

**Nothing collected.** No data types, no tracking. This is genuinely true today:
no analytics, no ads, no network calls.

**This is also the strongest asset the listing has** — and AdMob would destroy it. Adding ads
forces Device ID, Advertising Data and IP Address onto the label, requires an ATT prompt, and
undermines the Guideline 4.2 defence that the app is not a repackaged web page.

---

## Screenshots

Required: 6.7" iPhone. Since the app is Universal (`TARGETED_DEVICE_FAMILY: 1,2`), iPad
13" is required too.

✅ **Uploaded and accepted (all COMPLETE, no errors):**

| Display type | Size | Shots |
|---|---|---|
| `APP_IPHONE_67` | 1320×2868 | galaxy · BSEG detail · migration impact |
| `APP_IPAD_PRO_3GEN_129` | 2064×2752 | galaxy + sidebar · BSEG detail |

Apple accepted the 6.9" size (1320×2868) into the 6.7" slot, and the 13" iPad size
(2064×2752) into the 12.9" slot — no resizing needed.

**How they were taken.** The simulator can't be tapped from the CLI (`simctl` has no input
injection), so `tools/screenshot_harness.py` injects a one-shot state change into a throwaway
copy of the HTML — one state per build, held permanently. Timed multi-state harnesses don't
work: each `simctl io screenshot` takes ~60s, so a 6-second window is unhittable.

Two traps worth remembering:
- **`localStorage` survives reinstall.** The board from the impact shot persisted into the
  graph shot. `simctl uninstall` first, or clear it in the harness.
- **Never commit the harness.** It goes into `ERPGalaxy/Resources/Web/erp-galaxy.html`, which
  is a *copy* of the source. Always `cp sap-table-explorer.html` back afterwards and verify.

---

## Review notes

Same substance as the TestFlight notes — they pre-empt Guideline 4.2, which remains the
single biggest risk to this listing:

- No login. No demo account needed.
- Not a web wrapper: 2,033 records bundled, no hosted URL, **zero network calls**, runs in
  Airplane Mode. D3 is a bundled local renderer.
- Native: Spotlight index, WidgetKit extension, haptics, share sheet.
- 30-second path: search `BSEG` → tap → burger menu → lock tables → Impact.

---

## Review round 1 — Guideline 2.1, Information Needed (2026-07-17)

**Not a rejection on the merits.** Apple did *not* invoke Guideline 4.2 (minimum
functionality), which was the standing risk. They asked for information.

**Root cause: my mistake.** The detailed review notes I wrote went into
`betaAppReviewDetails` — the **TestFlight** resource. App Store review reads a *different*
resource, `appStoreReviewDetails`, and its `notes` field was **empty**. The reviewer opened
the submission with no explanation of what the app was, so "we need additional information"
is exactly the right response. Two similarly-named resources; I populated the wrong one.

**Fixed:** `metadata/review_notes.txt` (3,991 chars) now answers all seven questions and is
written to `appStoreReviewDetails.notes`. `demoAccountRequired` set to false.

Their seven items:

| # | Item | Status |
|---|---|---|
| 1 | Screen recording on a physical device | 🔴 **David** — see `metadata/RECORDING_SCRIPT.md`. `devicectl` has no recording capability and a Simulator capture would not satisfy "physical device". |
| 2 | Devices/OS tested | ✅ iPhone 17 Pro iOS 26.0 (physical); iPhone 17 Pro Max + iPad Pro 13" M5, iOS 26.5 |
| 3 | Purpose and audience | ✅ incl. the 2027 ECC deadline as the concrete problem |
| 4 | Setup and access instructions | ✅ no credentials; exact tap path given |
| 5 | External services | ✅ **none** — zero network calls; D3.js bundled locally, BSD-3-Clause |
| 6 | Regional differences | ✅ none — identical everywhere, English only |
| 7 | Regulated industry / third-party material | ✅ answered directly on SAP: no SAP code/logos/docs text, factual identifiers + our own prose, nominative fair use, explicit non-affiliation |

Build **5** is attached (an earlier note here said build 1 — that was stale), so the
reviewer did see the current feature set including the widget, Spotlight and the impact board.

Note their boilerplate mentions Guideline 2.3.3 (screenshots must show the app in use, not
splash art). Ours do — that section is generic advice, not a specific finding.

---

## Status

- [x] Privacy policy hosted and verified live
- [x] Name/subtitle/URLs written
- [x] Description/keywords/promo written
- [x] Categories set (DEVELOPER_TOOLS + REFERENCE)
- [x] Age rating declared (all 21 answers → 4+)
- [x] Screenshots captured and uploaded (5, all COMPLETE)
- [x] Build attached (**build 5**)
- [x] App Review Information notes (all 7 answers, 3,991 chars)
- [ ] App Privacy declared *(web UI only — API cannot do this)*
- [ ] Screen recording on a physical device — **David**, see `metadata/RECORDING_SCRIPT.md`
- [ ] Reply to Apple in App Store Connect with the recording attached

---

## 1.0.1 submission (2026-07-20)

Submitted for review — build **10** (1.0.1), state WAITING_FOR_REVIEW.

Rolled up since v1.0 shipped: migration verdicts 59→218, join finder, node
contrast + Migration Journey layout fixes, sheet swipe-dismiss from anywhere,
module All/None/solo + compact single-row chips.

Note: `appStoreVersionSubmissions` is deprecated (403, DELETE-only). The current
submit flow is: POST /v1/reviewSubmissions {platform:IOS} → POST
/v1/reviewSubmissionItems {reviewSubmission, appStoreVersion} → PATCH
/v1/reviewSubmissions/{id} {submitted:true}. Also: PATCH .../relationships/build
returns 204 (empty body), which trips a naive JSON parser but is success.

As a metadata-inclusive update from an already-approved app past the 2.1 round,
this should get a lighter review than the first submission.
