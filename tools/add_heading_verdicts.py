#!/usr/bin/env python3
"""Add verdicts for tables SAP names in the item HEADING rather than the body.

Found because a third-party comparison deck mentioned VBBS, which we did not
hold. Checking that lead against SAP's own Simplification List showed a real
item -- "S4TWL - New advanced ATP in SAP S/4HANA - Table VBBS" -- whose subject
table is named only in the heading. Our extractor reads item bodies, so it never
saw it.

That is the whole value of the third-party corpus: not its content, which
duplicated what SAP publishes, but its pointers to things we had missed in the
source we already trusted.

Each verdict below was read out of the item text by hand rather than pattern
matched, because there are five of them and a bad verdict is worse than a
missing one. The quote is what SAP says; the status is our reading of it.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

VERDICTS = {
    "VBBS": {
        "s4status": "deprecated",
        "replacedBy": "VBBE",
        "evidence": "With the new HANA ATP, we do not need pre-aggregation anymore, and therefore "
                    "this table is obsolete. Instead of the VBBS we use the VBBE, where each "
                    "ATP-relevant requirement is explicitly stored.",
        "action": "The old ERP-ATP check code is redirected to use VBBE. Custom code reading the "
                  "pre-aggregated requirements needs to read VBBE instead.",
        "sapNote": "2209696",
        "item": "15.1.1",
    },
    "BPID001": {
        "s4status": "deprecated",
        "replacedBy": None,
        "evidence": "FSBP table Additional Partner Numbers (BPID001) is obsolete.",
        "action": None,
        "sapNote": "3004812",
        "item": "13.3.4",
    },
    "BP1010": {
        # The table survives; four of its fields are on notice. "changed" rather
        # than "deprecated" -- calling the table gone would be wrong.
        "s4status": "changed",
        "replacedBy": None,
        "evidence": "Date of Credit Standing Information and RATING of the Financial Services "
                    "Business Partner table Creditworthiness Data (table name BP1010) will become "
                    "obsolete in a future release.",
        "action": "Four fields are flagged for future removal. Check custom code and interfaces "
                  "that read them before they go.",
        "sapNote": "3327581",
        "item": "5.1.25",
    },
    "BD001": {
        "s4status": "changed",
        "replacedBy": "CVI_CUST_LINK",
        "evidence": "Usage of obsolete links in tables BD001 / BC001. You need to migrate these "
                    "entries to the new link tables CVI_CUST_LINK / CVI_VEND_LINK.",
        "action": "Migrate the assignment entries to the CVI link tables before conversion.",
        "sapNote": "3010257",
        "item": "5.1.10",
    },
    "BC001": {
        "s4status": "changed",
        "replacedBy": "CVI_VEND_LINK",
        "evidence": "Usage of obsolete links in tables BD001 / BC001. You need to migrate these "
                    "entries to the new link tables CVI_CUST_LINK / CVI_VEND_LINK.",
        "action": "Migrate the assignment entries to the CVI link tables before conversion.",
        "sapNote": "3010257",
        "item": "5.1.10",
    },
}

# Tables named by those items that we simply did not hold. VBBE is NOT flagged
# new -- it exists in ECC as well, and SAP only says it becomes the sole store.
# The CVI link tables SAP does call new, in as many words.
SEED = {
    "VBBE": ("SD", "SD-BF-AC",
             "Holds each ATP-relevant requirement explicitly. In S/4HANA it replaces the "
             "pre-aggregated VBBS as the sole store for ATP requirements.", False),
    "CVI_CUST_LINK": ("SD", "AP-MD-BP",
                      "Maps a customer to its business partner. SAP calls it one of the new link "
                      "tables that the obsolete BD001 assignments must be migrated into.", True),
    "CVI_VEND_LINK": ("MM", "AP-MD-BP",
                      "Maps a vendor to its business partner. SAP calls it one of the new link "
                      "tables that the obsolete BC001 assignments must be migrated into.", True),
}


def main():
    lc_path = ROOT / "data" / "s4_lifecycle.json"
    lc = json.loads(lc_path.read_text())
    added = []
    for name, v in VERDICTS.items():
        if name in lc:
            continue
        lc[name] = {**v, "source": "simplification-list-2025-heading"}
        added.append(name)
    lc_path.write_text(json.dumps(lc, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

    t_path = ROOT / "data" / "tables.json"
    tables = json.loads(t_path.read_text())
    curated = set(json.loads((ROOT / "data" / "curated_ids.json").read_text()))
    seeded = []
    for name, (mod, sub, desc, is_new) in SEED.items():
        if name in tables or name in curated:
            continue
        tables[name] = {"id": name, "module": mod, "submodule": sub, "desc": desc,
                        "keyFields": [], "keySource": None, "lore": None, "tier": 2,
                        "moduleInferred": True}
        seeded.append(name)
    t_path.write_text(json.dumps(tables, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

    nis_path = ROOT / "data" / "new_in_s4.json"
    nis = json.loads(nis_path.read_text())
    for name, (_m, _s, _d, is_new) in SEED.items():
        if is_new and name not in nis:
            nis[name] = {
                "evidence": "You need to migrate these entries to the new link tables "
                            "CVI_CUST_LINK / CVI_VEND_LINK.",
                "held": "index",
            }
    nis_path.write_text(json.dumps(nis, indent=1, ensure_ascii=False) + "\n")

    orphans = [k for k in lc if k not in tables and k not in curated]
    if orphans:
        raise SystemExit(f"REFUSING: verdicts with no catalogue entry would be dead links: {orphans}")

    print(f"verdicts added : {added}")
    print(f"tables seeded  : {seeded}")
    print(f"verdicts total : {len(lc)}   new-in-S4 total: {len(nis)}")


if __name__ == "__main__":
    main()
