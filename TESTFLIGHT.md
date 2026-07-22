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
| Beta review detail | ✅ complete |
| **Beta App Review** | 🟡 **SUBMITTED — WAITING_FOR_REVIEW** (build 5, 2026-07-16) |

Beta groups already exist: `erp_int` (internal), `erp_ext` (external, public link disabled).

## Submission log

Two things blocked the submit and neither was obvious from the docs:

1. **`contactPhone` is required** on `betaAppReviewDetails` (409). Supplied by David;
   it lives only in App Store Connect and is deliberately **not** in this repo.
2. **The beta localization must match the app's `primaryLocale`.** The app is **en-AU**
   (Australia) and the first localization was created as **en-US**, so the submit failed with
   *"betaAppLocalizations not found for this app"* — a confusing error, since a localization
   plainly existed. Same trap for the build's "What to Test": an `en-US`
   `betaBuildLocalization` is not enough. Both now exist in **en-AU**.

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

---

## Build 20 (2026-07-22)

Live for internal testing. Everything since the build in App Store review: field guide,
23 lessons, BAPI catalogue, list view, field finder, business-concept aliases, fate filter,
paste-to-board, saved views, zoom-to-fit, and the corrected verdicts.

**Uploading a TestFlight build does not disturb an in-flight App Store submission.** The
version pins a specific build — 1.0.1 stayed on build 19 throughout — so TestFlight and review
run independently. Verified after upload rather than assumed.

**`POST /v1/builds/{id}/relationships/betaGroups` returns 422 "Builds cannot be assigned to
this internal group" — and that is not a failure.** Internal groups receive every processed
build automatically, so there is nothing to assign. The field that actually answers "is it
testable" is `buildBetaDetail.internalBuildState`, which read `IN_BETA_TESTING` already. Check
that before trying to fix the 422.

External (`erp_ext`) sits at `READY_FOR_BETA_SUBMISSION`: reaching external testers needs a
beta review pass, unlike internal.

`betaBuildLocalizations` already existed for **both** en-AU and en-US on this build, so they
were PATCHed rather than created — creating would have collided. Earlier notes here say a
locale mismatch fails misleadingly; the safe order is list first, then patch or create.
