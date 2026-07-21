#!/usr/bin/env python3
"""Build the BAPI / RFC function-module dataset.

Source: SAP's own "ABAP Cloudification Repository", https://github.com/SAP/abap-atc-cr-cv-s4hc
Licence: Apache-2.0, SAP-owned. Commercially redistributable with attribution,
which is why this is the one API-adjacent source the app uses -- api.sap.com's
robots.txt disallows ClaudeBot on /badi/*, /businessobject/* and /api/*/schema,
and the SAP API Policy prohibits large-scale extraction outright.

Two files:
  objectClassifications_SAP.json -- what each object IS (type, component,
      labels such as remote-enabled, classicAPI vs noAPI)
  objectReleaseInfoLatest.json   -- C1 release status, plus a `successors`
      graph pointing at the CDS view that supersedes an object

THE INFERRED EDGE, AND ITS LIMIT
SAP does NOT publish which database tables a BAPI reads or writes. It does
publish, for some objects, the CDS view that supersedes them. Where a function
module and a table point at the SAME successor view, they are related -- SAP has
said both were modernised into that view. That is our inference from published
data, not SAP's statement, so the app labels these "related objects" and never
"reads/writes", and names the view the link came through.
"""
import json
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Function groups whose modules are not interesting to a data practitioner.
NOISE_PREFIXES = ("/1", "/AIF/", "TR_", "SCP_")


def load(src, key):
    d = json.loads((src).read_text())
    rows = d[key]
    return list(rows.values()) if isinstance(rows, dict) else rows


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: build_bapis.py <dir with the two SAP json files>")
    src = pathlib.Path(sys.argv[1])
    cls = load(src / "objectClassifications_SAP.json", "objectClassifications")
    rel = load(src / "objectReleaseInfoLatest.json", "objectReleaseInfo")

    # ---- function modules -------------------------------------------------
    funcs = {}
    for r in cls:
        if r.get("objectType") != "FUNC":
            continue
        name = r.get("objectKey") or ""
        if not name or name.startswith(NOISE_PREFIXES):
            continue
        labels = r.get("labels") or []
        funcs[name] = {
            "name": name,
            "group": r.get("tadirObjName"),
            "component": r.get("applicationComponent"),
            "software": r.get("softwareComponent"),
            "state": r.get("state"),
            "rfc": "remote-enabled" in labels,
            "transactional": "transactional-consistent" in labels,
            "bapi": name.startswith("BAPI_"),
        }

    # ---- C1 release status + successor views ------------------------------
    successors = defaultdict(list)      # object name -> [cds view]
    view_to_tables = defaultdict(set)   # cds view    -> {tables}
    release_state = {}
    for r in rel:
        name = r.get("objectKey")
        if not name:
            continue
        if r.get("objectType") == "FUNC":
            release_state[name] = r.get("state")
        for s in (r.get("successors") or []):
            if s.get("objectType") != "CDS_STOB":
                continue
            view = s.get("objectKey")
            if r.get("objectType") == "FUNC":
                successors[name].append(view)
            elif r.get("objectType") == "TABL":
                view_to_tables[view].add(name)

    # ---- the inferred edge ------------------------------------------------
    tables = json.loads((ROOT / "data" / "tables.json").read_text())
    curated = set(json.loads((ROOT / "data" / "curated_ids.json").read_text())) \
        if (ROOT / "data" / "curated_ids.json").exists() else set()
    known = set(tables) | curated

    out, linked = {}, 0
    for name, f in funcs.items():
        if name in release_state:
            f["releaseState"] = release_state[name]
        views = successors.get(name) or []
        if views:
            f["successorViews"] = sorted(set(views))
        rel_tables = set()
        for v in views:
            rel_tables |= view_to_tables.get(v, set())
        # Only claim tables the app actually holds, so a chip always resolves.
        hits = sorted(t for t in rel_tables if t in known)
        if hits:
            f["relatedTables"] = hits
            f["via"] = sorted({v for v in views if view_to_tables.get(v, set()) & set(hits)})
            linked += 1
        out[name] = f

    path = ROOT / "data" / "bapis.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

    # App payload: every BAPI, plus any other module that carries a table link
    # or a C1 release status. The remaining ~1,600 internal modules cost 77KB
    # and answer no question a practitioner asks.
    packed = {
        k: [v.get("component") or "", 1 if v["rfc"] else 0,
            v.get("releaseState") or "", v.get("relatedTables") or [], v.get("via") or []]
        for k, v in sorted(out.items())
        if v["bapi"] or v.get("relatedTables") or v.get("releaseState")
    }
    app_path = ROOT / "data" / "bapis_app.json"
    app_path.write_text(json.dumps(packed, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(f"  app payload      {len(packed)} entries, {len(json.dumps(packed,separators=(',',':')))//1024} KB")

    bapis = sum(1 for f in out.values() if f["bapi"])
    rfc = sum(1 for f in out.values() if f["rfc"])
    print(f"function modules   {len(out)}")
    print(f"  BAPI_ prefixed   {bapis}")
    print(f"  RFC-enabled      {rfc}")
    print(f"  with C1 status   {sum(1 for f in out.values() if f.get('releaseState'))}")
    print(f"  with a successor {sum(1 for f in out.values() if f.get('successorViews'))}")
    print(f"  linked to tables {linked}   <- inferred via shared CDS successor")
    print(f"\nwrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
