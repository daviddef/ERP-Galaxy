import json, re

# DDIC-generated tables behind maintenance views, plus retired tables.
# Typed "Transparent Table" in source but not real business tables -- a consultant
# never queries V023_E. Excluded from the dataset entirely.
NOISE = re.compile(r"^(generated table for view|generierte tabelle zu|table no longer in use)", re.I)
SRC_MODULE = {
 "SAP Accounts Payable Tables List":            ("FI","FI-AP"),
 "SAP Accounts Receivable tables List":         ("FI","FI-AR"),
 "SAP BANK ACCOUNTING MODULE TABLES LIST":      ("FI","FI-BL"),
 "SAP Credit And Risk Management Tables":       ("FI","FI-AR-CR"),
 "SAP FI Consolidation Tables list":            ("FI","FI-CS"),
 "SAP General Ledger Tables List":              ("FI","FI-GL"),
 "SAP Travel Management Tables list":           ("FI","FI-TV"),
 "SAP Funds management tables List":            ("FM","FM"),
 "SAP EHS Tables":                              ("EHS","EHS"),
 "SAP HR Infotypes":                            ("HR","HR"),
 "SAP Inventory Management Tables List":        ("MM","MM-IM"),
 "SAP Invoice Verification tables":             ("MM","MM-IV"),
 "SAP Purchasing tables List":                  ("MM","MM-PUR"),
 "SAP Vendor Evaluation tables":                ("MM","MM-VE"),
 "SAP Sales Billing Tables":                    ("SD","SD-BIL"),
 "SAP Sales support Tables":                    ("SD","SD-CAS"),
}
REAL = ("Transparent Table","Pooled Table","Cluster Table","Append Structure")
pdf = json.load(open("tables.json"))

html = open("/Users/daviddefranceski/Claude/Projects/ERP Galaxy/sap-table-explorer.html", errors="replace").read()
tb = html[html.index('const TABLES=['):html.index('const LINKS_RAW=[')]
existing = {m.group(1) for m in re.finditer(r'\{id:"([^"]+)"', tb)}

out={}
for tid, v in pdf.items():
    if v["type"] not in REAL:      # drop Structures + General View Structures
        continue
    if tid in existing:            # curated Tier 1 wins — never overwrite
        continue
    if NOISE.match(v["desc"]):
        continue
    mods = [SRC_MODULE[s] for s in v["sources"] if s in SRC_MODULE]
    if not mods: continue
    module, submodule = mods[0]
    rec = {"id":tid, "module":module, "submodule":submodule, "tier":2,
           "src_desc":v["desc"], "sources":v["sources"]}
    if tid.startswith("/TDAG/"): rec["addon"]="EHS-CP"
    out[tid]=rec

json.dump(out, open("skeleton.json","w"), indent=1, sort_keys=True)
import collections
print("skeleton tables:", len(out))
print("by module:", collections.Counter(r["module"] for r in out.values()).most_common())
print("addon EHS-CP:", sum(1 for r in out.values() if r.get("addon")))
unmapped = {s for v in pdf.values() if v["type"] in REAL for s in v["sources"]} - set(SRC_MODULE)
print("unmapped source docs:", unmapped or "none")
