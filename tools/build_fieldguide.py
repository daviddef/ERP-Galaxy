#!/usr/bin/env python3
"""Generate the ECC → S/4HANA field guide from the app's own data.

Every number in the document is computed from the datasets at build time rather
than typed in, so the guide cannot drift from what the app actually holds --
which is the failure mode that put "Unchanged in S/4" next to a table SAP had
eliminated.

Sources are SAP's public Simplification List and SAP's Apache-2.0 cloudification
repository. Nothing here comes from the third-party ECC/S4 comparison decks:
those are uploads of unknown accuracy, several marked confidential, and their
table-level content duplicated what SAP publishes directly.
"""
import collections
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"


def load(name):
    return json.loads((D / name).read_text())


def main():
    lc = load("s4_lifecycle.json")
    tables = load("tables.json")
    curated = set(load("curated_ids.json"))
    fields = load("field_changes.json")
    lessons = load("lessons.json")
    playbooks = load("playbooks.json")
    movements = load("movement_types.json")
    doctypes = load("document_types.json")
    newin = load("new_in_s4.json")
    bapis = load("bapis_app.json")

    status = collections.Counter(v["s4status"] for v in lc.values())
    total = len(tables) + len(curated)
    with_action = sum(1 for v in lc.values() if v.get("action"))
    with_note = sum(1 for v in lc.values() if v.get("sapNote"))
    no_verdict = total - len(lc) - len([k for k in newin if k not in lc])
    linked_bapis = sum(1 for v in bapis.values() if v[3])

    L = []
    w = L.append

    w("# ECC → S/4HANA: what we actually know")
    w("")
    w("*A field guide built from SAP's own published position, generated from the ERP Galaxy "
      "dataset. Every count below is computed from the data, not typed in.*")
    w("")
    w("---")
    w("")
    w("## Why this document exists")
    w("")
    w("SAP mainstream maintenance for ECC ends **31 December 2027**. Between now and then most "
      "SAP estates have to answer one question, table by table: *what happens to this when we "
      "convert?*")
    w("")
    w("There is a lot of writing about S/4HANA. Most of it is either marketing, or a summary of "
      "a summary. This guide restricts itself to what SAP has actually published, and is explicit "
      "about where that runs out — because the gap between *documented* and *unknown* is where "
      "conversion projects get hurt.")
    w("")
    w("---")
    w("")
    w("## The five things that can happen to a table")
    w("")
    w("Every verdict in this guide is one of five outcomes. They are not equally survivable, and "
      "the difference between the middle three is where most of the risk sits.")
    w("")
    w("| Outcome | Tables | What it means for your code |")
    w("|---|---:|---|")
    w(f"| **Disappears** | {status['deprecated']} | Not in S/4HANA. Reads and writes both fail. |")
    w(f"| **Replaced** | {status['replaced']} | Still present, no longer the system of record. Code compiles and returns stale or partial answers. |")
    w(f"| **Compatibility view only** | {status['compat_view']} | Reads work, writes do not. Reporting keeps running, so this is the one that surfaces late. |")
    w(f"| **Changed** | {status['changed']} | Survives with different structure, semantics or content. |")
    w(f"| **Unchanged** | {status['unchanged']} | SAP states it is unaffected. |")
    w("")
    w(f"**{len(lc)} tables carry a published verdict.** {with_note} of those cite a specific SAP "
      f"Note, and {with_action} carry SAP's own required-action text.")
    w("")
    w("### The number that matters most is the one nobody quotes")
    w("")
    w(f"Roughly **{no_verdict:,} tables have no Simplification List entry at all.**")
    w("")
    w("That is not a clean bill of health. It means SAP has not published a change for them. "
      "Absence of an item is not a promise, and treating \"no news\" as \"no change\" is the "
      "single easiest way to be blindsided. Anything material to your business deserves a check "
      "regardless of whether it appears here.")
    w("")
    w("---")
    w("")
    w("## Tables SAP explicitly calls new")
    w("")
    w("Destinations, not risks — but worth knowing, because data you are looking for has moved "
      "into them.")
    w("")
    w("| Table | Held in the app |")
    w("|---|---|")
    for name, meta in sorted(newin.items()):
        w(f"| `{name}` | {meta['held']} |")
    w("")
    w("A caution that cost us a bug: **a successor is not necessarily new.** `KNA1`, `LFA1`, "
      "`MARA`, `MARC` and `RESB` are all named as successors in the Simplification List and all "
      "long predate S/4HANA. \"Data now lives here\" and \"this is new\" are different claims.")
    w("")
    w("---")
    w("")
    w("## Field-level changes that break code quietly")
    w("")
    w("A table surviving tells you nothing about the shape of the fields inside it. These are "
      "systemic — they span whole domains rather than single tables.")
    w("")
    w("| Change | From → To | SAP Note | Opt-in? |")
    w("|---|---|---|---|")
    for f in fields:
        rng = f"`{f['from']}` → `{f['to']}`" if f.get("from") else f"→ `{f['to']}`"
        w(f"| {f['title']} | {rng} | {f['note']} | {'**yes**' if f.get('optIn') else 'no'} |")
    w("")
    w("**The opt-in ones deserve a decision, not a default.** The amount field length extension "
      "is off until someone switches it on in Customizing — and SAP states that once activated it "
      "cannot be reversed.")
    w("")
    w("---")
    w("")
    w("## The scenarios projects actually plan around")
    w("")
    for p in playbooks:
        w(f"### {p.get('icon','')} {p['name']}")
        w("")
        w(p.get("why", ""))
        w("")
        if p.get("watch"):
            w("**What to watch**")
            w("")
            for x in p["watch"]:
                w(f"- {x}")
            w("")
        w(f"*Tables involved: {len(p.get('tables', []))} · SAP Notes: "
          f"{', '.join(p.get('notes', []))}*")
        w("")
    w("---")
    w("")
    w("## Lessons")
    w("")
    sourced = [l for l in lessons if l["kind"] == "sourced"]
    principles = [l for l in lessons if l["kind"] == "principle"]
    w(f"### From SAP's own required actions ({len(sourced)})")
    w("")
    w("SAP repeats the same instruction across many tables. Where it repeats, it is worth reading "
      "once, properly.")
    w("")
    for l in sourced:
        w(f"**{l['title']}**  ")
        w(f"{l['body']}  ")
        w(f"*Applies to {len(l['tables'])} table{'s' if len(l['tables']) != 1 else ''}"
          + (f" · SAP Note {', '.join(l['notes'])}" if l["notes"] else "") + "*")
        w("")
    w(f"### From building this thing ({len(principles)})")
    w("")
    w("Ours, not SAP's. Several were learned by getting it wrong here first.")
    w("")
    for l in principles:
        w(f"**{l['title']}**  ")
        w(f"{l['body']}")
        w("")
    w("---")
    w("")
    w("## What else is in the dataset")
    w("")
    w(f"- **{total:,} tables** with keys and declared foreign keys")
    w(f"- **{len(movements)} movement types** and **{len(doctypes)} document types**, decoded")
    w(f"- **{len(bapis):,} BAPIs and RFC-enabled function modules**, with cloud release status; "
      f"{linked_bapis} carry a derivable link to a table")
    w("")
    w("---")
    w("")
    w("## Where this comes from, and where it stops")
    w("")
    w("**Sources.** SAP's public Simplification List for S/4HANA 2025 FPS01, and SAP's "
      "Apache-2.0 licensed ABAP Cloudification Repository. Table names, field names and Note "
      "numbers are facts; the prose around them is ours.")
    w("")
    w("**What we deliberately do not have:**")
    w("")
    w("- **Full field lists.** We hold key fields and declared foreign keys, not every column. "
      "A table can carry a field without us knowing.")
    w("- **A per-table field diff.** The only public source pairing ECC and S/4 field lists "
      "disallows automated collection and sells that comparison as its own product.")
    w("- **BAPI parameter signatures.** SAP publishes none publicly.")
    w("- **Which tables a BAPI reads or writes.** Not published. Where the app links them, it is "
      "inferred from a shared successor view and labelled as such.")
    w("- **Anything about your system.** Every verdict here is about standard SAP. Your Z-tables, "
      "appends and modifications are yours to assess.")
    w("")
    w("*Not affiliated with or endorsed by SAP SE. SAP and S/4HANA are trademarks of SAP SE.*")

    out = ROOT / "docs" / "FIELD_GUIDE.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print(f"wrote {out.relative_to(ROOT)}  ({len(' '.join(L).split()):,} words)")
    print(f"  verdicts {len(lc)} | no verdict {no_verdict:,} | lessons {len(lessons)} "
          f"| field changes {len(fields)} | new-in-S4 {len(newin)}")


if __name__ == "__main__":
    main()
