# TestFlight — external release setup

**App Store Connect app:** `6791550922` · bundle `com.daviddef.erpgalaxy` · Team `L9SAXP2E2W`

## State (2026-07-16)

| | |
|---|---|
| Build 4 | **VALID** — widget extension included |
| Internal testing | ✅ **IN_BETA_TESTING** — `erp_int` can install now |
| External testing | ⏸️ **READY_FOR_BETA_SUBMISSION** |
| Export compliance | ✅ answered (`usesNonExemptEncryption: false`, set via `ITSAppUsesNonExemptEncryption` in Info.plist) |
| Beta localization | ✅ description + feedback email set |
| Beta review detail | 🔴 **blocked — `contactPhone` required** |

Beta groups already exist: `erp_int` (internal), `erp_ext` (external, public link disabled).

## 🔴 The one blocker

Apple rejects the review-detail write without a phone number:

```
409 ENTITY_ERROR.ATTRIBUTE.REQUIRED
"You must provide a value for the attribute 'contactPhone'"
```

That's David's personal contact detail — not something to invent. Everything else
(name, email, notes, demo-account-not-required) is staged and ready to write in one call.

## Beta App Review notes (staged)

These pre-empt the Guideline 4.2 "minimum functionality" risk flagged since day one —
a WKWebView wrapper is the textbook rejection, so the notes address it head-on with
facts a reviewer can verify in 30 seconds:

- **No login, no demo account needed.**
- **Not a web wrapper:** all 2,033 records ship in the bundle, no hosted URL, **no network
  calls at all** — it runs in Airplane Mode. D3 is a bundled local rendering engine.
- **Native functionality:** Core Spotlight over 2,033 tables, a WidgetKit extension with
  deep-linking, haptics, native share sheet.
- **Try it:** type `BSEG` → tap the result → burger menu → lock tables → migration impact.
- No data collected, no ads, no purchases.

## Why the 4.2 case is much stronger than it was

Every item here is something a website structurally cannot do:

| Evidence | Status |
|---|---|
| Fully offline, zero network calls | since Phase 0 (vendored D3) |
| Native Spotlight index, 2,033 tables | build 3 |
| WidgetKit extension + deep link | build 4 |
| Native Codex sheets, board, impact | builds 2–4 |
| Zero data collection | still true — **ads would end this** |

That last row is the argument for holding off on AdMob until external review is passed.

## To finish

1. David provides a contact phone number.
2. `PATCH /v1/betaAppReviewDetails/{id}` with the staged payload.
3. Add build 4 to `erp_ext`.
4. `POST /v1/betaAppReviewSubmissions` → Apple review (typically 24–48h).

## Privacy policy

`privacyPolicyUrl` is currently unset and Apple did not reject the localization without it.
It is likely to be required for **public App Store** release even though the app collects
nothing. A one-page "this app collects no data and makes no network requests" policy would
cover it — and stays true only while there are no ads.
