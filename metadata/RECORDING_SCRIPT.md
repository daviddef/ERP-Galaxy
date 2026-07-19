# Screen recording script — Apple review reply

**Apple requires this on a physical device**, so it has to be recorded on your iPhone 17 Pro.
I can't do it: `devicectl` has no screen-recording capability, and a Simulator recording
would not satisfy "captured on a physical device."

**Target length: 60–90 seconds.** Apple wants to see the app work, not a tour.

---

## Before you start

1. Install the **TestFlight build 5** (or whatever is latest) — this must be the submitted build.
2. **Delete and reinstall** so the recording starts from a clean state. The app persists
   favourites, locked boards and reading mode; a leftover board makes step 5 look pre-cooked.
3. Add Screen Recording to Control Centre: Settings → Control Centre → Screen Recording.
4. Turn on **Airplane Mode**. This is not cosmetic — it visibly proves the "no network
   connection" claim in the review notes, which is the single most useful thing this
   recording can demonstrate.
5. Go to the Home Screen. **Start recording from there**, so the launch is captured.

---

## The script

| # | Do this | Why it matters to the reviewer |
|---|---|---|
| 1 | From the Home Screen, tap the ERP Galaxy icon | Apple asked that it "begin with launching the app" |
| 2 | Let the graph settle. Pinch to zoom, drag to pan | Shows it's an interactive app, not a static page |
| 3 | Tap any circle (e.g. **BSEG**) | Opens the detail sheet — the core interaction |
| 4 | Scroll the sheet slowly: Plain English → Relationships → Migration → Key Fields | This is the substance of the product |
| 5 | Close the sheet. Tap the search field, type **BSEG** | Shows search over 2,033 tables |
| 6 | Tap a result | Confirms search → detail works |
| 7 | Tap the **padlock** on 3–4 different tables | Building a board |
| 8 | Open the **menu** (top right) → tap **Impact** | **The differentiator.** "4 of 5 need attention in an S/4 migration" |
| 9 | In the menu, tap **Classic**, then **Fun** | Shows the reading-mode toggle |
| 10 | Exit to Home Screen. Swipe down, search **BSEG** in Spotlight | Native iOS integration a web page cannot do |
| 11 | *(Optional)* Show the **Table of the Day** widget on the Home Screen | Second piece of native functionality |
| 12 | Stop recording | |

---

## What NOT to do

- Don't narrate or add captions — Apple just needs to see it working.
- Don't rush. A reviewer skimming at 2× still needs to read a screen.
- Don't skip the launch. "The recording must begin with launching the app."
- Don't record in Fun mode only — show both, since Classic is the client-facing register.

---

## After recording

Save the video, then in App Store Connect:
**App Review → Reply to Apple → attach the recording.**

The written answers to their other six questions are already saved in the
**App Review Information → Notes** field (3,991 chars), so the reply itself can be short:

> Thank you. The requested screen recording is attached, captured on a physical
> iPhone 17 Pro running iOS 26.0. Full written answers to items 2–7 are in the
> App Review Information Notes field of this submission.
>
> In summary: the app requires no account or login, makes no network requests
> (the recording is made in Airplane Mode to demonstrate this), contains no
> purchases or user-generated content, and requests no sensitive permissions.
