import json, os, re, sys, time, urllib.request, urllib.error
from lxparse import parse
UA="Mozilla/5.0 (compatible; SAPGalaxy-research/1.0; +https://github.com/daviddef/ERP-Galaxy)"
C="lxcache"; os.makedirs(C, exist_ok=True)
def fetch(tid):
    cp=os.path.join(C, re.sub(r'[^a-z0-9_]','-',tid.lower())+".html")
    if os.path.exists(cp): return open(cp,errors="replace").read()
    url="https://leanx.eu/en/sap/table/"+tid.lower().strip("/").replace("/","-")+".html"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":UA}), timeout=30) as r:
            b=r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: b=f"__HTTP_{e.code}__"
    except Exception as e: b=f"__ERR_{type(e).__name__}__"
    open(cp,"w").write(b); time.sleep(0.8)
    return b
ids=json.load(open(sys.argv[1])); out=sys.argv[2]
res=json.load(open(out)) if os.path.exists(out) else {}
for i,t in enumerate(ids):
    if t in res: continue
    b=fetch(t)
    res[t]={"status":b.strip("_")} if b.startswith("__") else {"status":"ok","keys":parse(b)}
    if i%25==0: json.dump(res, open(out,"w"), indent=0, sort_keys=True); print(f"  {i}/{len(ids)}", flush=True)
json.dump(res, open(out,"w"), indent=0, sort_keys=True)
print("done")
