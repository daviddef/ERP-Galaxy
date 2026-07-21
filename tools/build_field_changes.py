#!/usr/bin/env python3
"""Build the systemic field-change dataset.

Every fact here comes out of SAP's own Simplification List (SIMPL_OP2025.pdf,
the same document tools/parse_simplification_deep.py already parses for the
244 table verdicts). Old/new lengths, data types, SAP Note numbers, releases
and the "how to determine relevancy" checks are SAP's; the plain-English
wording is ours, same posture as every other description in the app.

Deliberately NOT sourced from third-party DDIC mirror sites. The only public
source carrying both ECC and S/4 field lists for the same table disallows
AI agents by name in robots.txt and sells the ECC-to-S/4 field diff as a paid
feature -- see ROADMAP_V3.md. So this covers the systemic, domain-wide changes
SAP documents, not a per-table field diff, and it says so in the app.

`tables` is the set SAP names explicitly in the item text. `keyFieldMatch`
additionally flags any table carrying that field as a key field -- resolved
in the app at runtime, because the curated graph and the codex are separate
datasets and only the app holds both. Where SAP describes a change as
domain-wide without enumerating tables, both are empty and the entry stays
browsable-only rather than guessing at a table list.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

CHANGES = [
    {
        "id": "matnr",
        "title": "Material number extended to 40 characters",
        "note": "2267140",
        "release": "S/4HANA 1511 and higher",
        "component": "CA-FLE-MAT",
        "fields": ["MATNR"],
        "from": "CHAR 18",
        "to": "CHAR 40",
        "optIn": "Extended-length material numbers are a switch. In a multi-system "
                 "landscape you decide if and when to switch it on, because it changes "
                 "how the system talks to everything around it.",
        "plain": "The material number field went from 18 to 40 characters. SAP adapted its own "
                 "domains, data elements, structures, tables and interfaces automatically — the "
                 "risk is in your code and your interfaces, not in the standard tables.",
        "action": "Check custom code, and any external interface that moves material numbers, "
                  "for a hard-coded length of 18.",
        "tables": [],
        "keyFieldMatch": ["MATNR"],
    },
    {
        "id": "afle",
        "title": "Currency amount fields extended to 23 digits",
        "note": "2628654",
        "release": "S/4HANA 1809 and higher",
        "component": "CA-FLE-AMT",
        "fields": [],
        "from": "9–22 digits incl. 2 decimals",
        "to": "23 digits incl. 2 decimals",
        "optIn": "Off by default. The amount field length extension must be explicitly "
                 "activated in Customizing — and SAP states that once activated it cannot "
                 "be reversed.",
        "plain": "Currency amount fields with a length between 9 and 22 digits (including 2 "
                 "decimals) were extended to 23 digits. Selected DEC, CHAR and NUMC data elements "
                 "that can hold amounts are affected too.",
        "action": "Decide per application area whether your code supports extended amounts. SAP "
                  "warns that mixing the two can truncate or lose data, because no implicit type "
                  "conversion happens.",
        "scopeNote": "SAP describes this as domain-wide across currency amount fields rather than "
                     "listing affected tables, so this app does not guess at a table list.",
        "tables": [],
        "keyFieldMatch": [],
    },
    {
        "id": "vbtyp",
        "title": "SD document category widened, status tables absorbed",
        "note": "2267306",
        "release": "SD Simplified Data Models",
        "component": "SD-BF-MIG",
        "fields": ["VBTYP", "VBTYP_EXT"],
        "from": "VBTYP — CHAR 1",
        "to": "VBTYPL — CHAR 4",
        "optIn": None,
        "plain": "Data element VBTYP (Char1) was replaced by VBTYPL (Char4), and field VBTYP_EXT "
                 "(Char4) was eliminated. Separately, status tables VBUK and VBUP disappeared — "
                 "their status fields moved into the header and item tables themselves.",
        "action": "Any code reading VBUK or VBUP must read VBAK/VBAP, LIKP/LIPS or VBRK instead. "
                  "Anything comparing a document category against a single character needs widening.",
        "tables": ["VBAK", "VBAP", "LIKP", "LIPS", "VBRK", "VBFA", "VBUK", "VBUP"],
        "keyFieldMatch": [],
    },
    {
        "id": "objknr",
        "title": "Object list number changed from INT4 to INT8",
        "note": "2580670",
        "release": "S/4HANA",
        "component": "PM-WOC-MO",
        "fields": ["OBJKNR"],
        "from": "INT4",
        "to": "INT8",
        "optIn": None,
        "plain": "A data type change, not just a length change. Object list numbers (table OBJK, "
                 "domain OBJKN, data element OBJKNR) moved from INT4 to INT8 so they can carry far "
                 "larger volumes. Every table with a field referencing OBJKNR is affected.",
        "action": "Custom programs must be adjusted for the changed interfaces. Custom tables "
                  "holding object list information must be adjusted and their content converted.",
        "tables": ["OBJK"],
        "keyFieldMatch": ["OBJKNR"],
    },
    {
        "id": "segment",
        "title": "Segment field extended to 40 characters",
        "note": "2522971",
        "release": "S/4HANA 1709",
        "component": "LO-RFM-CA-SE",
        "fields": [],
        "from": "16 characters",
        "to": "40 characters",
        "optIn": None,
        "plain": "The segmentation data model changed and the field length went from 16 to 40 "
                 "characters. SAP states this has no business impact and that the conversion "
                 "handles the adjustment automatically.",
        "action": "Nothing to do — adjustments are made automatically during conversion.",
        "howToCheck": "Only relevant if segmentation is used. Check table MARA in SE16N for "
                      "entries where MARA-SGT_REL is not initial.",
        "tables": ["MARA"],
        "keyFieldMatch": [],
    },
    {
        "id": "season",
        "title": "Season, Collection and Theme extended to 10 characters",
        "note": "2624475",
        "release": "S/4HANA 1809 and higher",
        "component": "LO-RFM-CA-SE",
        "fields": ["SEASON", "COLLECTION", "THEME"],
        "from": None,
        "to": "10 characters",
        "optIn": "Activating extended Season field length can break integration with "
                 "surrounding systems — SAP notes it does not work with SAP Customer "
                 "Activity Repository 3.0 (CARAB 2.0).",
        "plain": "The maximum length of the Season, Collection and Theme IDs was extended to 10 "
                 "characters. Fashion and retail only.",
        "action": "If the S/4HANA system sits in a landscape with other SAP or non-SAP solutions, "
                  "integration may only work if extended Season length is left switched off.",
        "scopeNote": "SAP names the data elements (FSH_SAISO, FSH_COLLECTION, FSH_THEME) rather "
                     "than a table list, so this app does not guess at one.",
        "tables": [],
        "keyFieldMatch": [],
    },
]


def main():
    codex = json.loads((ROOT / "data" / "tables.json").read_text())

    for c in CHANGES:
        # Codex-only preview of the runtime match. The app also matches against
        # the 217 curated tables, so its counts will be higher than these.
        n = 0
        for field in c["keyFieldMatch"]:
            n += sum(1 for t in codex.values()
                     if field in [f.upper() for f in (t.get("keyFields") or [])])
        print(f"{c['id']:9} note {c['note']}"
              f"  named={len(c['tables']):2}  codex-key-match={n}")

    path = ROOT / "data" / "field_changes.json"
    path.write_text(json.dumps(CHANGES, indent=1, ensure_ascii=False) + "\n")
    print(f"\nwrote {len(CHANGES)} field changes -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
