import sys, os, json, hashlib, urllib.request
sys.path.insert(0,".")
from asc import get, post, patch, token

VER_LOC="add74a4d-be84-4ba4-b3ef-604cbee20a0a"

def ensure_set(display):
    d=get(f"/v1/appStoreVersionLocalizations/{VER_LOC}/appScreenshotSets")
    for s in d.get("data",[]):
        if s["attributes"]["screenshotDisplayType"]==display: return s["id"]
    r=post("/v1/appScreenshotSets", {"data":{"type":"appScreenshotSets",
      "attributes":{"screenshotDisplayType":display},
      "relationships":{"appStoreVersionLocalization":{"data":{"type":"appStoreVersionLocalizations","id":VER_LOC}}}}})
    if "__error" in r: print("  set err", r["__error"], r["body"][:220]); return None
    return r["data"]["id"]

def upload(path, set_id):
    blob=open(path,"rb").read()
    r=post("/v1/appScreenshots", {"data":{"type":"appScreenshots",
      "attributes":{"fileSize":len(blob),"fileName":os.path.basename(path)},
      "relationships":{"appScreenshotSet":{"data":{"type":"appScreenshotSets","id":set_id}}}}})
    if "__error" in r: print("  reserve err", r["__error"], r["body"][:220]); return None
    sid=r["data"]["id"]
    for op in r["data"]["attributes"]["uploadOperations"]:
        chunk=blob[op["offset"]:op["offset"]+op["length"]]
        req=urllib.request.Request(op["url"], data=chunk, method=op["method"])
        for h in op["requestHeaders"]: req.add_header(h["name"], h["value"])
        urllib.request.urlopen(req, timeout=180).read()
    r=patch(f"/v1/appScreenshots/{sid}", {"data":{"type":"appScreenshots","id":sid,
      "attributes":{"uploaded":True,"sourceFileChecksum":hashlib.md5(blob).hexdigest()}}})
    if "__error" in r: print("  commit err", r["__error"], r["body"][:220]); return None
    return sid

if __name__=="__main__":
    display=sys.argv[1]; files=sys.argv[2:]
    sid=ensure_set(display)
    print("set:", sid)
    if sid:
        for f in files:
            r=upload(f, sid)
            print("  ", os.path.basename(f), "->", r or "FAILED")
