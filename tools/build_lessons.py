#!/usr/bin/env python3
"""Build the "lessons learned" dataset.

Two kinds, kept visibly distinct because their authority differs:

SOURCED — SAP's own "Required and Recommended Action" from the Simplification
List. 157 of our 244 verdicts carry one, but there are only 26 distinct texts:
the same instruction covers 35 finance tables, or 20 inventory tables. That
repetition IS the lesson. Each keeps SAP's wording as the quote and lists every
table it applies to, so it is checkable.

PRINCIPLE — ours. Conclusions from building and verifying this app, several of
them found the hard way when the app itself got something wrong. They assert no
SAP fact beyond what the sourced half already establishes.

Deliberately NOT sourced from the third-party ECC/S4 decks: those are Scribd
uploads of unknown accuracy, several marked confidential or proprietary, and
their table-level content duplicated what SAP publishes directly anyway.
"""
import collections
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Our titles and plain-English framing for the recurring SAP actions. Keyed by a
# distinctive fragment of SAP's text so the mapping survives re-parsing.
TITLES = [
    ("Adapt access to new simplified finance data model",
     "Read the Universal Journal, not the old FI tables",
     "The classic FI index and totals tables are no longer the system of record. Custom programs "
     "that select from them need to read ACDOCA instead. This single instruction covers more "
     "tables than any other in the Simplification List."),
    ("needs to be changed for MATDOC",
     "Anything writing MKPF or MSEG must write MATDOC",
     "Inventory management collapsed into one document table. Reads may survive through "
     "compatibility views, but updates do not — code that writes the old tables has to be changed."),
    ("statistical moving average",
     "Turn off the statistical moving average for throughput",
     "Not mandatory, but SAP recommends it: leaving it active costs transactional throughput in "
     "Material Ledger processing."),
    ("table pools and table clusters",
     "Table pools and clusters are gone — including CDCLS",
     "Removed as of 1809. Code referencing the container objects breaks; the logical tables "
     "survive as transparent tables. This is why change-document access needs checking."),
    ("append structures to database tables VBUK",
     "Append structures on VBUK or VBUP need rework",
     "The SD status tables were eliminated and their fields folded into the header and item "
     "tables. Any customer append on them has nowhere to go without adaptation."),
    ("until PP analytics in HANA",
     "LIS in PP is an interim solution — don't invest heavily",
     "SAP is explicit that the Logistics Information System is a bridge in S/4HANA. Building new "
     "reporting on these structures is building on something with a stated end."),
    ("until PM analytics in HANA",
     "LIS in PM is an interim solution — don't invest heavily",
     "Same position as PP: the information structures remain usable, but SAP frames them as an "
     "interim step rather than a destination."),
    ("append structures to database table KONV",
     "KONV appends must move to PRCD_ELEMENTS",
     "Pricing conditions changed their persistence table. KONV still exists, which is exactly why "
     "this one is missed — the appends do not come along automatically."),
    ("become obsolete in release 1709",
     "Foreign trade customizing tables retired in 1709",
     "A small set of customizing tables became obsolete. Worth checking early because they are "
     "easy to overlook in a config comparison."),
    ("access via compatibility views with direct access to ACDOCA",
     "CO compatibility views are a stopgap, not a destination",
     "Reading CO data through the compatibility views works, but SAP asks you to move to direct "
     "ACDOCA access for the affected value types."),
    ("Clean up Total Requirements",
     "Clean up total requirements before converting",
     "A pre-conversion housekeeping step. Custom code reading the requirements tables needs "
     "checking at the same time."),
    ("planning in classical PCA",
     "Classic Profit Centre planning needs a new home",
     "Planning in classic PCA is not carried forward as-is; SAP names the alternatives, and the "
     "choice between them is a design decision, not a technical one."),
    ("substance volume tracking",
     "Substance volume tracking selection criteria change",
     "An EHS consequence of the SD status tables disappearing — the selection criteria have to be "
     "adapted."),
    ("AUT_MIGRATE_ENHAT_DB_DATA",
     "Migrate table-logging config before you convert",
     "Run SAP's report in the source ERP system first. Doing it afterwards is not the documented "
     "path."),
    ("fields of table T169P are affected",
     "Exchange-rate-difference customizing moved on",
     "Custom code using the old exchange rate difference customizing has to be adapted; SAP names "
     "the affected fields."),
    ("BUTADRSEARCH is only kept for compatibility",
     "BUTADRSEARCH survives only for compatibility",
     "Business partner address search data is retained for compatibility reasons, not because it "
     "is still the right thing to read."),
]

# Ours. Each is a conclusion this project reached and can defend.
PRINCIPLES = [
    {"id": "no-item-no-promise",
     "title": "No simplification item is not a promise",
     "body": "1,803 of the tables in this app have no Simplification List entry at all. That means "
             "SAP has not published a change — not that the table is safe. The app files these "
             "under “No verdict” rather than “Carries over”, because collapsing the two turns "
             "“we don't know” into “it's fine”, and that is the error most likely to hurt you."},
    {"id": "compat-reads-not-writes",
     "title": "A compatibility view is a read, not a reprieve",
     "body": "59 tables survive only as compatibility views. Reporting keeps working, which is "
             "exactly why they get missed — the failure surfaces later, on the first write. Treat "
             "“still readable” and “still there” as different findings."},
    {"id": "irreversible-switches",
     "title": "Some switches cannot be unflipped",
     "body": "The amount field length extension is off by default and, once activated in "
             "Customizing, SAP states it cannot be reversed. Decide switches like this before "
             "conversion planning hardens, not after."},
    {"id": "successor-not-new",
     "title": "A successor table is not necessarily a new table",
     "body": "KNA1, LFA1, MARA, MARC and RESB are all named as successors in the Simplification "
             "List, and all long predate S/4HANA. “Data now lives here” and “this is new” are "
             "different claims, and conflating them invents history."},
    {"id": "still-there-still-right",
     "title": "“Still there” does not mean “still correct”",
     "body": "KONV still exists after pricing moved to PRCD_ELEMENTS. BSEG still exists after the "
             "Universal Journal. A table that survives can still be the wrong thing to read, and "
             "code that compiles will keep returning plausible answers from it."},
    {"id": "check-the-source",
     "title": "Prefer SAP's words to any summary of them",
     "body": "While building this app, curated one-line notes had drifted from SAP's published "
             "verdicts on 20 tables — VBUK and VBUP read “unchanged” where SAP had eliminated "
             "them. Wherever a summary and the Simplification List disagree, the list wins."},
]


def main():
    lc = json.loads((ROOT / "data" / "s4_lifecycle.json").read_text())

    groups = collections.defaultdict(list)
    for table, v in lc.items():
        act = (v.get("action") or "").strip()
        # Degenerate rows: a lone full stop, or a fragment where the parser ran
        # into the next section header instead of an instruction.
        if len(act) < 40 or act.startswith("None Related SAP Notes"):
            continue
        groups[act].append(table)

    lessons = []
    for act, tables in sorted(groups.items(), key=lambda x: -len(x[1])):
        title = summary = None
        for frag, t, s in TITLES:
            if frag.lower() in act.lower():
                title, summary = t, s
                break
        if not title:
            continue                      # no hand-written framing: leave it out
        notes = sorted({lc[t].get("sapNote") for t in tables if lc[t].get("sapNote")})
        lessons.append({
            "id": "sap-" + str(len(lessons) + 1),
            "kind": "sourced",
            "title": title,
            "body": summary,
            "sapAction": act[:600],
            "tables": sorted(tables),
            "notes": notes,
        })

    for p in PRINCIPLES:
        lessons.append({**p, "kind": "principle", "tables": [], "notes": []})

    path = ROOT / "data" / "lessons.json"
    path.write_text(json.dumps(lessons, indent=1, ensure_ascii=False) + "\n")

    sourced = [l for l in lessons if l["kind"] == "sourced"]
    covered = {t for l in sourced for t in l["tables"]}
    print(f"lessons {len(lessons)}  ({len(sourced)} sourced, {len(PRINCIPLES)} principles)")
    print(f"tables covered by a sourced lesson: {len(covered)}")
    unmatched = sum(1 for a in groups if not any(f.lower() in a.lower() for f, _, _ in TITLES))
    print(f"action clusters with no hand-written framing, omitted: {unmatched}")
    print(f"\nwrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
