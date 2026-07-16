import json, glob, difflib, sys, collections

sk = json.load(open("skeleton.json"))
authored = {}
for f in sorted(glob.glob("out/b*.json")):
    try:
        authored.update(json.load(open(f)))
    except Exception as e:
        print(f"BAD JSON: {f}: {e}"); sys.exit(1)
# overlays, applied last: zz_hr_fix (mechanical infotype restatements, id-derived)
# and zz_verbatim_fix (hand-restructured near-copies)
for f in sorted(glob.glob("out/zz_*.json")):
    authored.update(json.load(open(f)))

missing = set(sk) - set(authored)
# `extra` = ids authored before the generated-view/noise filter landed. Expected; ignored.
extra   = set(authored) - set(sk)
print(f"skeleton={len(sk)} authored={len(authored)} missing={len(missing)} extra(filtered-out)={len(extra)}")
if missing: print("  missing sample:", sorted(missing)[:5])

# --- quality gates -------------------------------------------------
problems = collections.defaultdict(list)
for tid, rec in sk.items():
    d = authored.get(tid)
    if d is None:
        continue
    if not isinstance(d, str) or not d.strip():
        problems["empty_or_wrong_type"].append(tid); continue
    src = rec["src_desc"]
    # licensing: must not be a verbatim lift
    if d.lower().rstrip(". ") == src.lower().rstrip(". "):
        problems["verbatim_copy"].append(tid)
    elif difflib.SequenceMatcher(None, d.lower(), src.lower()).ratio() > 0.92:
        problems["near_verbatim"].append(tid)
    # style
    if len(d) > 200:
        problems["too_long"].append(tid)
    if d.lower().startswith("this table"):
        problems["banned_opener"].append(tid)
    if not d.rstrip().endswith("."):
        problems["no_period"].append(tid)
    # invention smell: describing a table whose source was too thin to support it
    if len(src) < 12 and len(d) > 60:
        problems["possible_invention"].append(tid)

nulls = [k for k, v in authored.items() if v is None]
print(f"\nnulls: {len(nulls)} ({100*len(nulls)/max(1,len(authored)):.1f}%)")
for k, v in sorted(problems.items()):
    print(f"  {k:22s} {len(v):4d}  {v[:3]}")

if len(sys.argv) > 1 and sys.argv[1] == "--write":
    if missing:
        print("\nREFUSING to write: skeleton ids missing from authored output"); sys.exit(1)
    out = {}
    for tid, rec in sk.items():
        out[tid] = {"id": tid, "module": rec["module"], "submodule": rec["submodule"],
                    "tier": 2, "desc": authored[tid], "lore": None}
        if rec.get("addon"): out[tid]["addon"] = rec["addon"]
    json.dump(out, open("/Users/daviddefranceski/Claude/Projects/ERP Galaxy/data/tables.json", "w"),
              indent=1, sort_keys=True, ensure_ascii=False)
    print(f"\nwrote data/tables.json  ({len(out)} tables, {len(nulls)} desc=null)")
