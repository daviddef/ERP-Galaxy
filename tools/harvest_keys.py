import json, os, re, sys, time, urllib.request, urllib.error
from sdparse import parse

UA = "Mozilla/5.0 (compatible; SAPGalaxy-research/1.0; +https://github.com/daviddef/ERP-Galaxy)"
CACHE = "cache"; os.makedirs(CACHE, exist_ok=True)
DELAY = float(os.environ.get("DELAY", "1.0"))   # be polite: ~1 req/sec

def url_for(tid):
    # /TDAG/CPT_EXEMLI -> /abap/tabl//tdag/cpt_exemli.html
    return "https://www.sapdatasheet.org/abap/tabl/" + tid.lower() + ".html"

def cache_path(tid):
    return os.path.join(CACHE, re.sub(r'[^a-z0-9_]', '-', tid.lower()) + ".html")

def fetch(tid):
    cp = cache_path(tid)
    if os.path.exists(cp):
        return open(cp, errors="replace").read(), True
    req = urllib.request.Request(url_for(tid), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = f"__HTTP_{e.code}__"
    except Exception as e:
        body = f"__ERR_{type(e).__name__}__"
    open(cp, "w").write(body)
    time.sleep(DELAY)
    return body, False

def harvest(ids, out_path):
    res = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for i, tid in enumerate(ids):
        if tid in res: continue
        body, cached = fetch(tid)
        if body.startswith("__"):
            res[tid] = {"status": body.strip("_")}
        else:
            k, n, d = parse(body)
            res[tid] = {"status": "ok", "keys": k, "nfields": n, "sd_desc": d}
        if i % 25 == 0:
            json.dump(res, open(out_path, "w"), indent=0, sort_keys=True)
            print(f"  {i}/{len(ids)}", flush=True)
    json.dump(res, open(out_path, "w"), indent=0, sort_keys=True)
    return res

if __name__ == "__main__":
    ids = json.load(open(sys.argv[1]))
    harvest(ids, sys.argv[2])
    print("done:", len(ids))
