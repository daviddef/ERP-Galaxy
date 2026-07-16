import re, os, json, glob
def extract(sd_html):
    """field -> check table (SAP's declared foreign key) from a sapdatasheet page."""
    out={}
    for r in re.findall(r'<tr>(.*?)</tr>', sd_html, re.S):
        m=re.search(r'<a id="FIELD_([A-Z0-9_/]+)"></a>', r)
        if not m: continue
        fld=m.group(1)
        links=re.findall(r'href="/abap/tabl/([a-z0-9_/\-]+)\.html"[^>]*title="([^"]*)"[^>]*>([A-Z0-9_/]+)</a>', r)
        tgts=[t for _,_,t in links if t!=fld]
        if tgts: out[fld]=tgts[-1]
    return out

if __name__=="__main__":
    edges={}; per={}
    for p in glob.glob("cache/*.html"):
        body=open(p,errors="replace").read()
        if body.startswith("__"): continue
        m=re.search(r'<title>\s*SAP ABAP Table\s+(\S+)', body)
        if not m: continue
        src=m.group(1).upper()
        fk=extract(body)
        if fk: per[src]=fk
    json.dump(per, open("fkeys.json","w"), indent=0, sort_keys=True)
    print("tables with foreign keys:", len(per))
    print("total FK field->table links:", sum(len(v) for v in per.values()))
    tgts=set()
    for v in per.values(): tgts|=set(v.values())
    print("distinct target tables:", len(tgts))
